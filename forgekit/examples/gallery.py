"""forgekit v0.5.0 gallery — every new piece on one screen, for looking at.

Run:  PYTHONPATH=. python examples/gallery.py        (FORGE_ASCII=1 for console mode)
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Select, SelectionList, Static

from forgekit import (
    ChangeGroup, Choices, FilterPicker, Toggle, ForgeApp, ManualScreen, Notice, NumberPresets, ProgressDialog,
    ReviewDialog, SettingRow,
)

ENTRIES = [("0", "KognogOS (linux-zen)"), ("1", "KognogOS (linux-lts)"), ("2", "Windows Boot Manager"),
           ("3", "UEFI Firmware Settings"), ("saved", "Last chosen (remembers your pick)")]

PAGES = [
    ("start", "Getting started", "# Getting started\n\nOpen **Settings** with `e`, change a value, press **F10** to save.\n\n## Good to know\n\n- Nothing is written until you save.\n- [Backups](#backups) are made first.\n"),
    ("backups", "Backups and undo", "# Backups and undo\n\nEvery save makes a backup first.\n\n1. Open **Backups**.\n2. Pick one.\n3. Press **R** to restore.\n"),
]


class Form(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("Tab", "next"), ("Enter", "open list"), ("Space", "switch"), ("F10", "save"), ("?", "all keys")]

    def compose(self) -> ComposeResult:
        yield Static("[b $forge-title-accent]Start-up[/]   [$forge-muted]How the boot menu behaves when the computer starts[/]")
        yield Notice("Your own order is in use", ["A kernel update won't show up until you restore the original order."], level="warn")
        yield SettingRow("Start this entry", Select([(l, v) for v, l in ENTRIES], value="0", allow_blank=False, id="default"),
                         note="the entry GRUB starts when nobody presses a key", id="row-default")
        yield SettingRow("Remember last choice", Toggle(False), note='only works with "Last chosen"')
        yield SettingRow("Wait before starting", NumberPresets(5, [("0", 0), ("3", 3), ("5", 5), ("10", 10), ("30", 30), ("wait forever", -1)], unit="seconds", minimum=-1))
        yield SettingRow("Show the menu", Choices([("menu", "Always"), ("countdown", "With a countdown"), ("hidden", "Hidden")], "countdown"))
        yield SettingRow("Kernel options", SelectionList(("quiet  — show fewer messages", "quiet", True),
                                                       ("splash — a picture instead of text", "splash", True),
                                                       ("nomodeset — basic display driver", "nomodeset")))

    def on_mount(self) -> None:
        self.query_one("#row-default", SettingRow).mark_changed("the first entry in the menu")


class Gallery(ForgeApp):
    APP_NAME = "forgekit v0.5.0 · gallery"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    HINTS = [("1", "form"), ("p", "picker"), ("r", "review"), ("g", "progress"), ("m", "manual"), ("q", "quit")]
    MENU = [
        {"id": "form", "title": "Form", "kind": "section"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [("Manual", "m", "manual")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    BINDINGS = [Binding("p", "picker"), Binding("r", "review"), Binding("g", "progress"),
                Binding("m", "act('manual')"), Binding("q", "act('quit')")]

    def compose_sections(self) -> ComposeResult:
        yield Form(id="sec-form")

    def on_mount(self) -> None:
        super().on_mount()
        self.set_title_status("KognogOS · javier · password at save")
        self.changes_bar.show("1 change not saved yet", "changed", [("Save…  F10", "save", True), ("Discard", "discard", False)])

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            self.push_screen(ManualScreen("Gallery manual", PAGES))

    def action_picker(self) -> None:
        self.push_screen(FilterPicker("Start this entry", [(v, l) for v, l in ENTRIES], current="0",
                                      hint="Entries from your boot menu"))

    def action_review(self) -> None:
        self.push_screen(ReviewDialog("Review before saving", [
            ChangeGroup("Settings", "/etc/default/grub", [("Start this entry", "the first entry", "KognogOS (linux-zen)"),
                                                          ("Theme", "none", "Vimix")]),
            ChangeGroup("Boot order", "/etc/grub.d/40_custom", [("Windows Boot Manager", "3rd", "2nd")])],
            steps=["A backup of both files is saved", "The changes are written"],
            note="You'll be asked for your password once.",
            buttons=[("Save", "save", True), ("Save and rebuild", "both", False)]))

    def action_progress(self) -> None:
        d = ProgressDialog("Rebuilding the boot menu", ["Backup saved", "Changes written", "Boot menu rebuilt"])
        self.push_screen(d)
        d.set_step(0, "done", "09:42:07")
        d.set_step(1, "done")
        d.set_step(2, "working")
        d.add_line("Found linux image: /boot/vmlinuz-linux-zen")
        d.add_line("Found Windows Boot Manager on /dev/nvme0n1p1")


if __name__ == "__main__":
    Gallery().run()
