#!/usr/bin/env bash
# Lets libvirt's system-wide VMs (the "QEMU/KVM" connection in Virtual Machine Manager) use an
# NVIDIA card for 3D graphics: virtio-gpu with 3D acceleration, rendered on the card by an
# egl-headless display and shown through ordinary SPICE. (SPICE with OpenGL on also starts after
# this fix, but its window stays black on NVIDIA. See testing/README.md.)
#
# Why this is needed: libvirt starts every VM's QEMU in a private /dev that holds only the
# devices on its allow-list (cgroup_device_acl). NVIDIA's EGL, which QEMU uses to draw with the
# card, must open /dev/nvidiactl, /dev/nvidia0 and /dev/nvidia-modeset. They are not on the
# default list, so QEMU stops at start-up with:
#     egl: eglInitialize failed: EGL_NOT_INITIALIZED
# The same QEMU run as a normal user (no private /dev) starts fine; that is how the cause
# was confirmed on 2026-09-28. Details: https://github.com/jetomev/hypeforge/issues/2
#
# What it does: backs up /etc/libvirt/qemu.conf to /var/backups/kognog/, appends an allow-list
# made of libvirt 12.7's seven default entries plus the three NVIDIA files, and restarts libvirtd.
# Running it twice changes nothing. Undo: restore the backup and restart libvirtd.
#
# Run with sudo:  sudo bash scripts/test-rig/enable-nvidia-vm-3d.sh
set -euo pipefail

conf=/etc/libvirt/qemu.conf
marker="# hypeForge test rig: NVIDIA 3D for VMs"

[[ $EUID -eq 0 ]] || { echo "Run this with sudo." >&2; exit 1; }
for dev in /dev/nvidiactl /dev/nvidia0 /dev/nvidia-modeset; do
    [[ -c $dev ]] || { echo "$dev is missing: is the NVIDIA driver loaded?" >&2; exit 1; }
done

if grep -qF "$marker" "$conf"; then
    echo "Already applied: $conf has the NVIDIA allow-list."
else
    if grep -qE '^\s*cgroup_device_acl' "$conf"; then
        echo "$conf already sets cgroup_device_acl by hand; not touching it. Add the three NVIDIA files there." >&2
        exit 1
    fi
    mkdir -p /var/backups/kognog
    backup=/var/backups/kognog/qemu.conf.$(date +%Y%m%d-%H%M%S)
    cp -a "$conf" "$backup"
    cat >> "$conf" <<'EOF'

# hypeForge test rig: NVIDIA 3D for VMs (added 2026-09-28, github.com/jetomev/hypeforge/issues/2)
# The first seven entries are libvirt 12.7's own defaults. The last three are the NVIDIA device
# files that its EGL opens when a VM draws with the card (SPICE OpenGL / virtio-gpu 3D).
cgroup_device_acl = [
    "/dev/null", "/dev/full", "/dev/zero",
    "/dev/random", "/dev/urandom",
    "/dev/ptmx", "/dev/userfaultfd",
    "/dev/nvidiactl", "/dev/nvidia0", "/dev/nvidia-modeset"
]
EOF
    echo "Backed up to $backup and appended the allow-list to $conf."
fi

systemctl restart libvirtd
systemctl is-active --quiet libvirtd && echo "libvirtd restarted and running."
