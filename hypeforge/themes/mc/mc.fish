# hypeForge: Midnight Commander opens files for editing (F4) in fresh, KognogOS's editor.
# Only for mc: other programs keep their own editor. Needs use_internal_edit=false in
# ~/.config/mc/ini ([Midnight-Commander]). Installed as ~/.config/fish/functions/mc.fish.
function mc --wraps mc --description 'Midnight Commander, editing in fresh'
    EDITOR=fresh command mc $argv
end
