# hypeForge — testing

Every step is tested on the **KognogOS test desktop** first — an NVIDIA RTX 3060 with three 1440p screens at 144 Hz — where Javier lives in hypeForge every day. That is one setup among many: hypeForge is meant for one screen or many, and other screen setups are tested as the screen and workspace apps are built. Virtual machines (a KognogOS install, a plain Arch install) follow before any release.

Each finding gets a number (F-1, F-2…) and an [issue](https://github.com/jetomev/forge-suite/issues). Test plans and results are named `YYYYMMDD - Test Matrix for hypeForge <version>.md` and `… Test Results …`.

| Matrix | What it covered |
|---|---|
| [20261004 — sway-barebones](20261004%20-%20Test%20Matrix%20for%20hypeForge%20sway-barebones.md) | The first Sway login: three screens at 144 Hz, video, Discord screen share, WoW, brightness |
