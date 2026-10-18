#!/bin/bash
# hypeForge's login starter, three ways, on a hidden screen (run as the VM's user, 2026-10-17): the versions
# match (our build, the login's own copy of the button lines) · a Sway update (the system's Sway, flagged) ·
# our build broken (the system's Sway, flagged). Copies a minimal ~/.config/sway/config: a VM's, never the desktop's.
set -u
# never on a desktop: it writes its own ~/.config/sway/config
if [ -n "${SWAYSOCK:-}${WAYLAND_DISPLAY:-}" ] || { [ -f ~/.config/sway/config ] && ! grep -q '^# login-test' ~/.config/sway/config; }; then
    echo "login-test.sh: refusing — this looks like a real desktop (a running Sway, or a ~/.config/sway/config of its own)"
    exit 1
fi
H=~/Programs/forge-suite/hypeforge
mkdir -p ~/.config/sway ~/fakebin
cat > ~/.config/sway/config <<'CONF'
# login-test (sway-hypeforge/login-test.sh): a test VM's minimal config
set $hf_button_hover #303337
set $hf_button_hover_text #d4d8dd
set $hf_close_hover #ffa09c
set $hf_close_hover_text #200e0e
xwayland disable
output * bg #ff00ff solid_color
exec env > "$XDG_RUNTIME_DIR/sway-env.txt"
CONF
try() {   # label, PATH to use
    rt=$(mktemp -d); chmod 700 "$rt"
    env -i HOME="$HOME" PATH="$2" XDG_RUNTIME_DIR="$rt" WLR_BACKENDS=headless WLR_RENDERER=pixman \
        WLR_LIBINPUT_NO_DEVICES=1 sh "$H/sway-hypeforge/hypeforge-session" >"$rt/log" 2>&1 &
    sleep 4
    pid=$(pgrep -u "$USER" -n -x sway)
    if [ -n "$pid" ]; then
        args=$(tr '\0' ' ' < /proc/$pid/cmdline)
        fb=$(grep '^HYPEFORGE_SWAY_FALLBACK=' "$rt/sway-env.txt" 2>/dev/null || echo "no fallback flag")
        echo "$1: $args"; echo "    $fb"
        kill "$pid"; sleep 1
    else
        echo "$1: NO SWAY RUNNING"; tail -5 "$rt/log"
    fi
    rm -rf "$rt"
}
try "1. versions match      " "/usr/bin:/bin"
printf '#!/bin/sh\nif [ "$1" = "--version" ]; then echo "sway version 1.13"; exit; fi\nexec /usr/bin/sway "$@"\n' > ~/fakebin/sway; chmod +x ~/fakebin/sway
try "2. Sway updated (1.13) " "$HOME/fakebin:/usr/bin:/bin"
rm ~/fakebin/sway
real=$(readlink ~/.local/opt/sway-hypeforge/current); ln -sfn missing ~/.local/opt/sway-hypeforge/current
try "3. our build broken    " "/usr/bin:/bin"
ln -sfn "$real" ~/.local/opt/sway-hypeforge/current
echo "build link back to: $(readlink ~/.local/opt/sway-hypeforge/current)"
