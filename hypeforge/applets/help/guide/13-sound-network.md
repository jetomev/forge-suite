# Sound, network and Bluetooth

**What it does:** three icons in one pill on the bar's right, on every style the same way (since 2026-10-13).

| Icon | Shows | Left click | Right click |
|---|---|---|---|
| **Bluetooth** | on, off (red), or connected | **Quick Settings** | **bluetui** (below) |
| **Network** | a cable when wired, Wi-Fi bars when wireless, red when not connected | **Quick Settings** | **nmtui**, to edit connections |
| **Volume** | the level, red when muted | **Quick Settings** | **wiremix**, the mixer |

**Quick Settings** (on macOS it's called Control Center): tiles for Wi-Fi, Bluetooth, the night light,
Do Not Disturb, Screens and VPN, the volume slider, the update count, a button into
**hypeForge Settings**, and the power buttons; the big buttons open the Forge apps (Screens →
displayForge, updates → nogForge). A click anywhere else closes it.

**Pages inside Quick Settings** (2026-10-25): a click on the **Night light** tile, or on the **sound icon**
at the right end of the volume row (after the %), opens that part's page **in the same card** — **‹** (or Esc) goes
back to Quick Settings. The on/off switch is on the page; its full app is the icon at the bottom right. The speaker at the
start of the volume row mutes.
- **Night light** — on/off, what it's doing in words ("Daylight now · warm again from 18:45"), the
  warmth slider, **Warm now** and **Automatic**; the icon at the bottom right opens nightForge.
- **Sound** — the volume (its speaker mutes), your **outputs** (speakers, headset, a screen's
  speakers) and your **microphones**: click one to make it the one in use; the icon at the bottom
  right opens the mixer (wiremix).
- **Wi-Fi** — the switch in the title row; your **cable** (connected or unplugged); the **networks
  nearby**, strongest first. Click one to connect: a saved or open network connects at once, a new
  secured one opens a **password box** under it (Connect, Cancel). The connected one has
  **Disconnect**. A wrong password says so, and the next try asks again. The list keeps itself
  current (switched on, it says *Starting Wi-Fi…* and fills in by itself); the **refresh** button
  next to the switch looks again at once. Up to 8 named networks, strongest first; **Hidden
  network…** joins one that doesn't show its name (you type the name and password). The icon at the
  bottom right opens the full network settings (nmtui, until networkForge).
- **Bluetooth** — the switch in the title row; **your devices**, the connected ones first, each with
  **Connect** or **Disconnect** (and its battery, when the device tells it); *Connecting…* while it
  works, and a note if it couldn't (is it on, and close by?). **Pair a new device…** opens the
  Bluetooth app (bluetui, until bluetoothForge), and so does the icon at the bottom right.
The bar's network icon opens the Wi-Fi page on its own, the Bluetooth icon its page, and the speaker
the Sound page. Your password is never put on a command line (where any program could read it): it
goes to NetworkManager through a private file that is deleted right after. The **date, time and bell** are one piece too: a click opens the calendar with your
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
