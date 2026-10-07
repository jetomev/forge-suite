"""polkit's admin pop-up, answered for the whole login session.

Adapted from forgekit's ``InAppPolkitAgent`` (forgekit 0.6.0, same authors),
with two differences: it registers for the **session** (``Polkit.UnixSession``)
instead of one process, and it keeps the request's kind and details so the box
can say who is asking. It speaks polkit's D-Bus interface directly; forgekit's
spike found the PyGObject ``PolkitAgent.Listener`` subclass crashing (SIGSEGV)
after a successful answer.

polkit calls arrive on the GLib main loop; the box is asked on a thread of its
own so a cancel can still arrive while the person types. polkit's own setuid
helper checks the password; three tries, as polkit's own agents do.
"""

from __future__ import annotations

import os
import pwd
import threading

from .words import polkit_lines

PATH = "/org/kognogos/sudoforge/AuthenticationAgent"
TRIES = 3
_XML = """<node><interface name="org.freedesktop.PolicyKit1.AuthenticationAgent">
<method name="BeginAuthentication"><arg type="s" name="action_id" direction="in"/>
<arg type="s" name="message" direction="in"/><arg type="s" name="icon_name" direction="in"/>
<arg type="a{ss}" name="details" direction="in"/><arg type="s" name="cookie" direction="in"/>
<arg type="a(sa{sv})" name="identities" direction="in"/></method>
<method name="CancelAuthentication"><arg type="s" name="cookie" direction="in"/></method>
</interface></node>"""


class SessionAgent:
    def __init__(self, service) -> None:
        self.service = service
        self.active = False
        self._jobs: dict[str, dict] = {}
        self._reg_id = None

    def start(self) -> str | None:
        try:
            import gi
            gi.require_version("Polkit", "1.0")
            gi.require_version("PolkitAgent", "1.0")
            from gi.repository import GLib, Gio, Polkit, PolkitAgent
        except (ImportError, ValueError) as e:
            return f"polkit's Python parts are missing ({e}); install python-gobject"
        self._GLib, self._Polkit, self._PolkitAgent = GLib, Polkit, PolkitAgent
        session = os.environ.get("XDG_SESSION_ID")
        if not session:
            return "no login session id (XDG_SESSION_ID is not set)"
        try:
            self._bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            node = Gio.DBusNodeInfo.new_for_xml(_XML)
            self._reg_id = self._bus.register_object(PATH, node.interfaces[0], self._call, None, None)
            self._authority = Polkit.Authority.get_sync(None)
            self._subject = Polkit.UnixSession.new(session)
            self._authority.register_authentication_agent_sync(
                self._subject, os.environ.get("LANG", "en_US.UTF-8"), PATH, None)
        except Exception as e:                              # GLib.Error and friends
            self._unexport()
            return f"polkit did not accept sudoForge for this session ({e})"
        self.active = True
        return None

    def stop(self) -> None:
        if not self.active:
            return
        self.active = False
        for job in list(self._jobs.values()):
            self._cancel_job(job)
            self._finish(job, ok=False, cancelled=True)
        try:
            self._authority.unregister_authentication_agent_sync(self._subject, PATH, None)
        except Exception:
            pass
        self._unexport()

    def _unexport(self) -> None:
        if self._reg_id:
            try:
                self._bus.unregister_object(self._reg_id)
            except Exception:
                pass
            self._reg_id = None

    # ── polkit's calls (GLib main loop) ─────────────────────────────────────
    def _call(self, conn, sender, path, iface, method, params, inv) -> None:
        if method == "BeginAuthentication":
            action, message, _icon, details, cookie, idents = params.unpack()
            users = [i[1].get("uid") for i in idents if i[0] == "unix-user"]
            uid = os.getuid() if os.getuid() in users else (users[0] if users else os.getuid())
            try:
                name = pwd.getpwuid(uid).pw_name
            except KeyError:
                name = str(uid)
            lines = polkit_lines(action, message, dict(details), name, self.service.procs)
            from .service import log
            log(f"polkit asks: {action} — {lines.heading}")
            job = {"cookie": cookie, "inv": inv, "uid": uid, "lines": lines, "attempt": 0,
                   "cancelled": False, "session": None, "box": None}
            self._jobs[cookie] = job
            self._try(job)
        elif method == "CancelAuthentication":
            (cookie,) = params.unpack()
            job = self._jobs.get(cookie)
            if job:
                self._cancel_job(job)
                self._finish(job, ok=False, cancelled=True)
            inv.return_value(None)
        else:
            inv.return_dbus_error("org.freedesktop.DBus.Error.UnknownMethod", method)

    def _cancel_job(self, job: dict) -> None:
        job["cancelled"] = True
        if job["session"]:
            try:
                job["session"].cancel()
            except Exception:
                pass
        current = self.service._current
        if current is not None and job.get("asking"):
            current.cancel()

    def _try(self, job: dict) -> None:
        job["attempt"] += 1
        s = self._PolkitAgent.Session.new(self._Polkit.UnixUser.new(job["uid"]), job["cookie"])
        job["session"] = s
        s.connect("request", lambda s_, prompt, echo: self._request(job, s_))
        s.connect("completed", lambda s_, gained: self._completed(job, gained))
        s.initiate()

    def _request(self, job: dict, session) -> None:
        def ask() -> None:
            job["asking"] = True
            try:
                pw = self.service.ask(job["lines"], job["attempt"], lambda: job["cancelled"])
            except Exception:
                pw = None
            finally:
                job["asking"] = False

            def respond() -> bool:
                if job["cookie"] not in self._jobs:
                    return False
                if pw is None:
                    job["cancelled"] = True
                    session.cancel()
                else:
                    session.response(pw)
                return False
            self._GLib.idle_add(respond)
        threading.Thread(target=ask, name="sudoforge-polkit-ask", daemon=True).start()

    def _completed(self, job: dict, gained: bool) -> None:
        from .service import log
        if gained:
            log("polkit: accepted")
            self._finish(job, ok=True)
        elif job["cancelled"] or job["attempt"] >= TRIES:
            log("polkit: cancelled" if job["cancelled"] else "polkit: three wrong passwords")
            self._finish(job, ok=False, cancelled=job["cancelled"])
        else:
            log("polkit: wrong password, asking again")
            self._try(job)

    def _finish(self, job: dict, ok: bool, cancelled: bool = False) -> None:
        if self._jobs.pop(job["cookie"], None) is None:
            return
        inv = job["inv"]
        if ok:
            inv.return_value(None)
        elif cancelled:
            inv.return_dbus_error("org.freedesktop.PolicyKit1.Error.Cancelled", "Cancelled in sudoForge")
        else:
            inv.return_dbus_error("org.freedesktop.PolicyKit1.Error.Failed", "The password was not accepted")
