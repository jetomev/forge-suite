# Using this help (applet 6)

**What it does:** **Win + F1** (or *Help & Keys* in the launcher) opens this help: the **key
chart**, searchable — type *close* and you get *Alt + F4* — and this **guide**, one page per
applet. The hypeForge Settings will show the same pages.

## Where it comes from

- The key chart: `applets/help/keys.toml` in the hypeForge project — **one list**, compared with
  Sway's real keys on every save, so it cannot quietly go out of date.
- The guide: `applets/help/guide/`, one page per applet.

## Moving around

- **← →** the previous / next tab; **1 to 7** go straight to a tab, and so does **Ctrl + the underlined
  letter** in its name (Ctrl+K Keys, Ctrl+S Start, Ctrl+W Workspaces, Ctrl+I Windows, Ctrl+A Apps,
  Ctrl+T Tools, Ctrl+B About).
- Help & Keys has no Help menu of its own; **About** is the last tab.
- **↑ ↓** or **Page Up / Page Down** to read; **q**, **Esc** or **Ctrl+Q** to close.

## Inside hypeForge Settings

Every Forge app in Settings, this help included, runs **without a Quit of its own**: Settings starts
them with `--hypeforge`, so q, Esc and Ctrl+Q do nothing there. Settings' own **Quit** closes them all,
and an app with something not saved asks you first, on its own page.
