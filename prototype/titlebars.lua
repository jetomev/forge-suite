-- hypeForge prototype: title bars with maximise and close (D-33, D-34: no minimise).
-- Drawn by hyprbars, the Hyprland team's title-bar plugin (github.com/hyprwm/hyprland-plugins),
-- for windows that do not draw their own, such as Alacritty and other terminals.
-- Needs the plugin loaded (hyprpm enable hyprbars && hyprpm reload). Colours: Catppuccin Mocha.

local mocha = {
    mantle = "rgba(181825ee)", base = "rgba(1e1e2eff)", text = "rgba(cdd6f4ff)",
    red = "rgba(f38ba8ff)", green = "rgba(a6e3a1ff)",
}

-- Runs Lua inside Hyprland from a button click (buttons run a shell command).
local function lua_cmd(code) return "hyprctl eval '" .. code .. "'" end

local MAXIMISE = lua_cmd('hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" }))')

hl.config({
    plugin = {
        hyprbars = {
            bar_height = 26,
            bar_color = mocha.mantle,
            ["col.text"] = mocha.text,
            bar_text_font = "JetBrainsMono Nerd Font",
            bar_text_size = 10,
            bar_text_align = "left",
            bar_padding = 10,
            bar_button_padding = 8,
            bar_buttons_alignment = "right",
            on_double_click = MAXIMISE,
        },
    },
})

-- Buttons are listed right to left: close, maximise.
local hb = hl.plugin and hl.plugin.hyprbars
if hb and hb.add_button then
    hb.add_button({ bg_color = mocha.red, fg_color = mocha.base, size = 14, icon = "󰖭",
                    action = lua_cmd("hl.dispatch(hl.dsp.window.close())") })
    hb.add_button({ bg_color = mocha.green, fg_color = mocha.base, size = 14, icon = "󰖯",
                    action = MAXIMISE })
end

-- Apps that draw their own title bar keep theirs, so they do not get two.
hl.window_rule({
    name = "hypeforge-own-titlebar",
    match = { class = "^(chromium|google-chrome|brave-browser|org\\.gnome\\..*)$" },
    ["hyprbars:no_bar"] = true,
})
