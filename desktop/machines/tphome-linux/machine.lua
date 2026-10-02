-- tphome-linux: Javier's desktop, the KognogOS test machine (D-28: one computer's details).
-- Three Sceptre Y27 screens at 2560x1440, 144 Hz, side by side as in Plasma:
-- DP-2 left, DP-3 middle, DP-1 right (read from KDE's screen settings, 2026-09-30).
-- Monique (Screens) can replace this layout; it saves to monitors.lua next to this file,
-- which hyprland.lua loads after this one.
hl.monitor({ output = "DP-2", mode = "2560x1440@144", position = "0x0",    scale = 1 })
hl.monitor({ output = "DP-3", mode = "2560x1440@144", position = "2560x0", scale = 1 })
hl.monitor({ output = "DP-1", mode = "2560x1440@144", position = "5120x0", scale = 1 })

-- Brightness keys: the three screens share one name, serial and connector, so ddcutil
-- addresses them by I2C bus 3, 4 and 5 (D-20).
local function ddc(delta)
    return hl.dsp.exec_cmd("for b in 3 4 5; do ddcutil --bus $b setvcp 10 " .. delta .. " 10 & done")
end
hl.bind("XF86MonBrightnessUp",   ddc("+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", ddc("-"), { locked = true, repeating = true })

-- Keyboard: US International, the layout this computer's system setting already uses
-- (localectl: us / intl). ' + a gives á, ~ + n gives ñ (Javier, 2026-10-01).
hl.config({ input = { kb_layout = "us", kb_variant = "intl" } })

-- World of Warcraft 3.3.5a under Wine (pi-kognog-azerothcore client): open it full-screen on the
-- middle screen, so the window is exactly the 2560x1440 the game draws at. Left tiled, the window
-- came out a different size from the picture: the view jumped when moving the mouse and clicks
-- landed in the wrong place (2026-10-01).
hl.window_rule({
    name = "wow-fullscreen",
    match = { class = "(?i)^wow.*\\.exe$" },
    monitor = "DP-3",
    fullscreen = true,
})
