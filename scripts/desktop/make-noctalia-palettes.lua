-- make-noctalia-palettes.lua: write hypeForge's five themes (D-36) as Noctalia palettes (D-40).
--   lua scripts/desktop/make-noctalia-palettes.lua
-- One source for every colour: desktop/hypr/themes/<id>.lua and themes/terminal.lua.
-- The role mapping is from docs/research/2026-09-30-noctalia-integration.md, section 2.
local root = arg[0]:match("(.*)/scripts/desktop/") or "."
local dir = root .. "/desktop/hypr/themes/"
local out = root .. "/desktop/noctalia/palettes/"
local terminal = dofile(dir .. "terminal.lua")
local names = { mocha = "Mocha", black = "Black", green = "Green", gray = "Gray", white = "White" }
local shadow = { green = "#7f9a88", white = "#8a8a8a" }          -- light themes: a softer shadow
local tnames = { "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white" }

local function block(t, p, id)
    local c = t.c
    local r = {
        { "mPrimary", c.accent }, { "mOnPrimary", c.btnIcon },
        { "mSecondary", c.border }, { "mOnSecondary", c.btnIcon },
        { "mTertiary", c.a4 }, { "mOnTertiary", c.btnIcon },
        { "mError", c.red }, { "mOnError", c.btnIcon },
        { "mSurface", c.window }, { "mOnSurface", c.text },
        { "mSurfaceVariant", c.selection }, { "mOnSurfaceVariant", c.subtext },
        { "mOutline", c.inactive }, { "mShadow", shadow[id] or "#000000" },
        { "mHover", c.selection }, { "mOnHover", c.text },
    }
    local lines = {}
    for _, kv in ipairs(r) do lines[#lines + 1] = string.format('    "%s": "%s"', kv[1], kv[2]) end
    local function set(list)
        local s = {}
        for i, n in ipairs(tnames) do s[#s + 1] = string.format('"%s": "%s"', n, list[i]) end
        return "{ " .. table.concat(s, ", ") .. " }"
    end
    lines[#lines + 1] = string.format('    "terminal": {\n      "background": "%s", "foreground": "%s",\n' ..
        '      "cursor": "%s", "cursorText": "%s",\n      "selectionBg": "%s", "selectionFg": "%s",\n' ..
        '      "normal": %s,\n      "bright": %s\n    }',
        p.bg, p.fg, c.accent, p.bg, c.selection, p.fg, set(p.normal), set(p.bright))
    return "{\n" .. table.concat(lines, ",\n") .. "\n  }"
end

for id, name in pairs(names) do
    local t = dofile(dir .. id .. ".lua")
    local b = block(t, terminal[id], id)
    local f = assert(io.open(out .. "hypeForge-" .. name .. ".json", "w"))
    -- Each hypeForge theme is one kind; the favourite's theme_mode picks dark or light,
    -- so both blocks carry the same colours.
    f:write('{\n  "dark": ' .. b .. ',\n  "light": ' .. b .. '\n}\n')
    f:close()
    print("wrote hypeForge-" .. name .. ".json (" .. t.kind .. ")")
end
