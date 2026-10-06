"""polkit's password question, asked inside the app (v0.6.0).

A Forge app that changes system files (grubForge) runs as the user and asks
polkit for permission through ``pkexec``. polkit then has the session's
*authentication agent* ask for the password: on a desktop that is the
desktop's own window; on a text console there is none, and the change
failed. (Javier, 4 Oct 2026: a desktop window "doesn't make sense" for a
terminal app, and "how does it work on the tty?" — it didn't.)

``InAppPolkitAgent`` makes the app the authentication agent **for its own
process only**. polkit asks it; it shows the app's password box; polkit's own
setuid helper (through ``PolkitAgent.Session``) checks the password. The app
never gets root and never decides whether the password is right. A wrong
password is asked again (three tries, as polkit's own agents do); Cancel
cancels. Proven on a text console in the KognogOS VM before it was written
(pkexec ran as root after the app answered).

It speaks polkit's D-Bus interface directly (``org.freedesktop.PolicyKit1.
AuthenticationAgent``) rather than subclassing ``PolkitAgent.Listener``: the
Python bridge to that class's asynchronous callback crashed (SIGSEGV) after a
successful answer, in the same spike.

Needs PyGObject with the Polkit typelibs (``python-gobject``, ``polkit``).
Without them ``start()`` returns False and says why; the app keeps its old way.
"""

from __future__ import annotations

import os
import threading
from typing import Awaitable, Callable

Asker = Callable[[str, int], Awaitable[str | None]]      # (message, attempt) -> password or None

PATH = "/org/kognogos/forge/AuthenticationAgent"
TRIES = 3
_XML = """<node><interface name="org.freedesktop.PolicyKit1.AuthenticationAgent">
<method name="BeginAuthentication"><arg type="s" name="action_id" direction="in"/>
<arg type="s" name="message" direction="in"/><arg type="s" name="icon_name" direction="in"/>
<arg type="a{ss}" name="details" direction="in"/><arg type="s" name="cookie" direction="in"/>
<arg type="a(sa{sv})" name="identities" direction="in"/></method>
<method name="CancelAuthentication"><arg type="s" name="cookie" direction="in"/></method>
</interface></node>"""


class InAppPolkitAgent:
    def __init__(self, asker: Asker, call_from_thread: Callable) -> None:
        """``call_from_thread`` is the app's (Textual's ``App.call_from_thread``):
        polkit's questions arrive on a thread of their own and must reach the
        app inside its own context."""
        self._asker = asker
        self._call_in_app = call_from_thread
        self.reason = ""
        self.active = False
        self._glib_loop = None
        self._reg_id = None
        self._jobs: dict[str, dict] = {}

    # ── start / stop ─────────────────────────────────────────────────────────
    def start(self) -> bool:
        try:
            import gi
            gi.require_version("Polkit", "1.0")
            gi.require_version("PolkitAgent", "1.0")
            from gi.repository import GLib, Gio, Polkit, PolkitAgent  # noqa: F401
        except (ImportError, ValueError) as e:
            self.reason = f"polkit's Python parts are missing ({e}); install python-gobject"
            return False
        self._GLib, self._Polkit, self._PolkitAgent = GLib, Polkit, PolkitAgent
        try:
            self._bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            node = Gio.DBusNodeInfo.new_for_xml(_XML)
            self._reg_id = self._bus.register_object(PATH, node.interfaces[0], self._call, None, None)
            self._authority = Polkit.Authority.get_sync(None)
            self._subject = Polkit.UnixProcess.new_for_owner(os.getpid(), 0, os.getuid())
            self._authority.register_authentication_agent_sync(
                self._subject, os.environ.get("LANG", "en_US.UTF-8"), PATH, None)
        except Exception as e:                              # GLib.Error and friends
            self.reason = f"polkit did not accept the app as the password asker ({e})"
            self._unexport()
            return False
        self._glib_loop = GLib.MainLoop()
        threading.Thread(target=self._glib_loop.run, name="forge-polkit", daemon=True).start()
        self.active = True
        return True

    def stop(self) -> None:
        if not self.active:
            return
        self.active = False
        for job in list(self._jobs.values()):
            self._finish(job, ok=False, cancelled=True)
        try:
            self._authority.unregister_authentication_agent_sync(self._subject, PATH, None)
        except Exception:
            pass
        self._unexport()
        if self._glib_loop is not None:
            self._glib_loop.quit()

    def _unexport(self) -> None:
        if self._reg_id:
            try:
                self._bus.unregister_object(self._reg_id)
            except Exception:
                pass
            self._reg_id = None

    # ── polkit's calls (GLib thread) ─────────────────────────────────────────
    def _call(self, conn, sender, path, iface, method, params, inv) -> None:
        if method == "BeginAuthentication":
            _action, message, _icon, _details, cookie, idents = params.unpack()
            users = [i[1].get("uid") for i in idents if i[0] == "unix-user"]
            uid = os.getuid() if os.getuid() in users else (users[0] if users else os.getuid())
            job = {"cookie": cookie, "inv": inv, "uid": uid, "message": message, "attempt": 0,
                   "cancelled": False, "session": None}
            self._jobs[cookie] = job
            self._try(job)
        elif method == "CancelAuthentication":
            (cookie,) = params.unpack()
            job = self._jobs.get(cookie)
            if job:
                job["cancelled"] = True
                if job["session"]:
                    job["session"].cancel()
                self._finish(job, ok=False, cancelled=True)
            inv.return_value(None)
        else:
            inv.return_dbus_error("org.freedesktop.DBus.Error.UnknownMethod", method)

    def _try(self, job: dict) -> None:
        job["attempt"] += 1
        s = self._PolkitAgent.Session.new(self._Polkit.UnixUser.new(job["uid"]), job["cookie"])
        job["session"] = s
        s.connect("request", lambda s_, prompt, echo: self._request(job, s_))
        s.connect("completed", lambda s_, gained: self._completed(job, gained))
        s.initiate()

    def _request(self, job: dict, session) -> None:
        # ask on a thread of its own, so polkit's thread stays free (a cancel
        # can still arrive) while the person types
        def ask() -> None:
            try:
                pw = self._call_in_app(self._asker, job["message"], job["attempt"])
            except Exception:
                pw = None

            def respond() -> bool:
                if pw is None:
                    job["cancelled"] = True
                    session.cancel()
                else:
                    session.response(pw)
                return False
            self._GLib.idle_add(respond)
        threading.Thread(target=ask, name="forge-polkit-ask", daemon=True).start()

    def _completed(self, job: dict, gained: bool) -> None:
        if gained:
            self._finish(job, ok=True)
        elif job["cancelled"] or job["attempt"] >= TRIES:
            self._finish(job, ok=False, cancelled=job["cancelled"])
        else:
            self._try(job)                                   # a wrong password: ask again

    def _finish(self, job: dict, ok: bool, cancelled: bool = False) -> None:
        if self._jobs.pop(job["cookie"], None) is None:
            return
        inv = job["inv"]
        if ok:
            inv.return_value(None)
        elif cancelled:
            inv.return_dbus_error("org.freedesktop.PolicyKit1.Error.Cancelled", "Cancelled in the app")
        else:
            inv.return_dbus_error("org.freedesktop.PolicyKit1.Error.Failed", "The password was not accepted")
