# Workspaces Management (applet 1)

**What it does:** gives you six workspaces — **1 Daily · 2 Work · 3 Entertainment · 4 Gaming ·
5 Monitoring · 6 Settings** — that cover **all your screens at once**. Switching workspace
switches every screen together, so each workspace is a whole desk of its own.

## How to use it

- **Win + 1 … 6** switches every screen at once.
- **Workspaces** on the bar (W underlined) — **click it, or press Win + W** — drops down the
  list, the one on screen marked **●**; hover over it to see its name. Pick one and every screen
  switches. Press again (or **Esc**) to close it.
- **Win + Shift + 1 … 6**: send the window you are in to another workspace (it stays on the
  same screen).
- The mouse stays where it is when you switch.

## Apps open on their own workspace

Each workspace can have a list of **its apps**: Steam and your games on Gaming, Spotify on
Entertainment, Chrome on Daily. Open one **however you like** (the launcher, typing its name,
Favorites, a terminal, Steam starting a game) and it opens on its workspace, with **every screen
going there with it**. Window placement then gives it its spot.

- In the **first 30 seconds after you log in**, apps that start by themselves (Dropbox, Discord…)
  go to their workspace quietly: your screens stay where they are.
- **One app, one workspace.** An app on no list opens wherever you are.
- The lists started from the launcher's groups on 9 October 2026. **workspaceForge** will be the
  place to change them; until then, the `apps` lines in the settings file below.

## Sharing a screen (the matrix)

A screen can **share one space** between several workspaces: its apps then stay put while the
other screens change. Example: keep your main apps on the middle screen in Daily, Work and
Entertainment. Sharing works down one screen (the same screen across workspaces), never across
screens — a window can only be in one place.

## Settings

`~/.config/hypeforge/applets/workspaces.toml`

- `enabled = true / false` — switch the applet on or off
- `screens` — the screens in order (screen 1 is the main one)
- one `[[workspace]]` block per workspace (up to 9): add, rename, reorder or delete
- `apps = [...]` in a workspace's block — the apps that open there (their launcher names:
  `steam`, `google-chrome`, `"Sim Companies"`…)
- `[share]` — which workspaces share a space on each screen

After editing by hand: `hypeforge-workspaces reload`.

## Which workspace am I on?

The **square right of the KognogOS emblem** shows the number of the workspace on this screen (1 to 6), in the bar's bright colour; hover it for the name. It changes the moment you switch (Win + 1…6, the Workspaces list, or an app that opens on its own workspace). A click opens the Workspaces list, like Win + W.
