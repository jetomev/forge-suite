-- hypeForge prototype: bringing minimised windows back (D-31).
-- Minimised windows are parked on the hidden workspace "special:minimized" (by the title-bar
-- button, Win + PgDn, or minimise-helper.py when the taskbar asks). When a parked window is
-- activated, for example by clicking its icon in the taskbar, it comes back to the workspace
-- the user is looking at.

local PARK = "special:minimized"

local function restore_parked(w)
    if not w or not w.address or not w.workspace or w.workspace.name ~= PARK then return end
    local target = "address:" .. w.address
    local mon = hl.get_active_monitor()
    local ws = mon and mon.active_workspace
    if not ws then return end
    hl.dispatch(hl.dsp.window.move({ workspace = tostring(ws.id), follow = false, window = target }))
    -- Activating a parked window opened the hidden workspace on screen; close it again.
    if mon.active_special_workspace and mon.active_special_workspace.name == PARK then
        hl.dispatch(hl.dsp.workspace.toggle_special("minimized"))
    end
    hl.dispatch(hl.dsp.focus({ window = target }))
end

hl.on("window.active", function(w)
    restore_parked(w or hl.get_active_window())
end)
