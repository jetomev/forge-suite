# Sound, network and Bluetooth

**What it does:** three icons in one pill on the bar's right, on every style the same way (since 2026-10-13).

| Icon | Shows | Left click | Right click |
|---|---|---|---|
| **Bluetooth** | on, off (red), or connected | **Quick Settings** | **bluetui** (below) |
| **Network** | a cable when wired, Wi-Fi bars when wireless, red when not connected | **Quick Settings** | **nmtui**, to edit connections |
| **Volume** | the level, red when muted | **Quick Settings** | **wiremix**, the mixer |

**Quick Settings** (on macOS it's called Control Center): tiles for Wi-Fi, Bluetooth, the night light,
Do Not Disturb, Screens and VPN, the volume slider (the night light's warmth is in its own pop-up, from the moon), the update count, a button into
**hypeForge Settings**, and the power buttons; the big buttons open the Forge apps (Screens →
displayForge, updates → nogForge). A click anywhere else closes it. The **moon** next to the tray is
the night light: its own small pop-up (Warm Now · Daylight Now · Automatic, the warmth slider, a button
into nightForge). The **date, time and bell** are one piece too: a click opens the calendar with your
alerts as cards; a right click on the bell switches Do Not Disturb.

**Scroll** over the volume icon for louder / quieter; the volume keys on the keyboard work too.
Hover over any of them for details. The terminal apps open in a small floating window. Close
wiremix with **q**, bluetui with **q** or **Esc**, nmtui with **Esc** (or any of them with
**Alt + F4**).

## The network menu

A list like the others, under the bar's right end: what you are connected to (marked **●**),
the Wi-Fi networks with their signal, and lines to switch Wi-Fi, Bluetooth or all networking
on and off. **Pick a Wi-Fi network** → if it needs one, a password box opens (the password
shows as dots) → connected. Wi-Fi is off on this computer for now; **Enable WiFi** turns it on.

## The mixer (wiremix)

**Tab** / **Shift + Tab** move between the tabs at the bottom: **Playback** (each app's
volume), Recording, **Output Devices** (speakers, headsets — the SteelSeries Arctis 5 shows as
**Chat** and **Game**), Input Devices, Configuration. **↑ ↓** pick, **← →** change the volume,
**1–9** set it in tens (**0** = 100 %), **m** mutes, **Enter** opens a choice (where an app plays, for example),
**d** makes a device the default, **?** shows every key.

## Bluetooth (bluetui)

**Tab** moves between the sections: the **adapter** (your Bluetooth), **paired devices**, and
**new devices**. **s** searches for new devices. On a new device, **Enter** pairs it. On a
paired one: **Enter** connects or disconnects, **t** trusts it (it reconnects by itself), **f**
favourite, **e** rename, **u** unpair. On the adapter: **o** power on / off, **p** pairing,
**d** discoverable.

## Settings

The icons: the bar's settings (`bluetooth`, `network`, `wireplumber`). The mixer's look and
names: `~/.config/wiremix/wiremix.toml`. The network menu: `~/.config/networkmanager-dmenu/`.
