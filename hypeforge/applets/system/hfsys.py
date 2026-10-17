"""hypeForge's system readings (Javier, 2026-10-17: "icons and popups for CPU, GPU, Temperature, Memory,
Disks Space. Let's make them pretty too!!!"). Everything the five bar pop-ups show, read straight from the
kernel's own files (/proc, /sys) — no extra program needed; the graphics card through `nvidia-smi` (it
comes with NVIDIA's driver) or AMD's own files.

The sampler (`hypeforge-system run`, started at login) keeps the last three minutes in
$XDG_RUNTIME_DIR/hypeforge-system/, so a pop-up opens with its graph already drawn; the pop-up itself reads
live while it is open. Every reader takes its root folder, so the tests feed it a fake /proc and /sys.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hypeforge-system"
STATE = RUNTIME / "now.json"
EVERY = 2.0                      # seconds between readings
KEEP = 90                        # readings kept: three minutes
HISTORY_KEYS = ("cpu", "memory", "gpu", "cpu_temp", "gpu_temp")


# ---- levels: the same three on the bar and in the pop-ups -----------------------------------------

def level(value: float | None, warm: float, hot: float) -> str:
    """"ok", "warning" or "critical" (the bar's CSS classes)."""
    if value is None:
        return "ok"
    return "critical" if value >= hot else "warning" if value >= warm else "ok"


BUSY = (70, 90)                  # a processor, graphics card or memory this busy (%) is warm / hot
FULL = (80, 92)                  # a disk this full


# ---- the processor ------------------------------------------------------------------------------

def cpu_times(root: Path = Path("/")) -> dict[str, tuple[int, int]]:
    """Each processor line of /proc/stat → (busy, total) ticks; "cpu" is all of them together."""
    out = {}
    for line in (root / "proc/stat").read_text().splitlines():
        if not line.startswith("cpu"):
            break
        name, *nums = line.split()
        v = [int(n) for n in nums[:8]] + [0] * (8 - len(nums[:8]))
        idle = v[3] + v[4]                       # idle + waiting for a disk
        total = sum(v)
        out[name] = (total - idle, total)
    return out


def usage(before: dict, after: dict) -> dict[str, float]:
    """Percent busy between two readings, per line."""
    out = {}
    for k, (b1, t1) in after.items():
        b0, t0 = before.get(k, (b1, t1))
        dt = t1 - t0
        out[k] = round(100.0 * (b1 - b0) / dt, 1) if dt > 0 else 0.0
    return out


def cpu_model(root: Path = Path("/")) -> str:
    try:
        for line in (root / "proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                name = line.split(":", 1)[1].strip()
                return re.sub(r"\s+(\d+-Core|Processor|CPU)\b.*$", "", name).replace("(R)", "").replace("(TM)", "").strip()
    except OSError:
        pass
    return "Processor"


def cpu_speed(root: Path = Path("/")) -> float | None:
    """The processor's speed right now, in GHz (the fastest core: that is the one working)."""
    speeds = []
    for f in (root / "sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_cur_freq"):
        try:
            speeds.append(int(f.read_text()))
        except (OSError, ValueError):
            pass
    return round(max(speeds) / 1e6, 2) if speeds else None


def load_and_uptime(root: Path = Path("/")) -> tuple[float, float]:
    try:
        load = float((root / "proc/loadavg").read_text().split()[0])
        up = float((root / "proc/uptime").read_text().split()[0])
        return load, up
    except (OSError, ValueError, IndexError):
        return 0.0, 0.0


# ---- memory -------------------------------------------------------------------------------------

def memory(root: Path = Path("/")) -> dict:
    """In bytes: total, used by apps, cache (given back when an app needs it), free; and the swap."""
    m = {}
    for line in (root / "proc/meminfo").read_text().splitlines():
        k, _, v = line.partition(":")
        parts = v.split()
        if parts:
            m[k] = int(parts[0]) * 1024
    total = m.get("MemTotal", 0)
    avail = m.get("MemAvailable", m.get("MemFree", 0))
    cache = m.get("Buffers", 0) + m.get("Cached", 0) + m.get("SReclaimable", 0) - m.get("Shmem", 0)
    used = max(total - avail, 0)
    cache = max(min(cache, total - used), 0)
    swap_total = m.get("SwapTotal", 0)
    swap_used = swap_total - m.get("SwapFree", 0)
    return {"total": total, "used": used, "cache": cache, "free": max(total - used - cache, 0),
            "percent": round(100.0 * used / total, 1) if total else 0.0,
            "swap_total": swap_total, "swap_used": swap_used}


# ---- the graphics card ----------------------------------------------------------------------------

def gpu(root: Path = Path("/"), run=subprocess.run) -> dict | None:
    """The graphics card: name, % busy, its own memory, temperature, power, fan, speed. NVIDIA through
    nvidia-smi; AMD (and Intel Arc) through the card's own files. None when there is nothing to read."""
    if root == Path("/") and shutil.which("nvidia-smi"):
        q = "name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit,fan.speed,clocks.gr"
        try:
            r = run(["nvidia-smi", f"--query-gpu={q}", "--format=csv,noheader,nounits"], capture_output=True,
                    text=True, timeout=3)
            line = r.stdout.strip().splitlines()[0] if r.returncode == 0 and r.stdout.strip() else ""
        except (OSError, subprocess.TimeoutExpired):
            line = ""
        if line:
            f = [x.strip() for x in line.split(",")]
            num = lambda s: float(s) if re.fullmatch(r"[\d.]+", s or "") else None   # "[N/A]" → None
            return {"name": f[0].replace("NVIDIA ", "").replace("GeForce ", "GeForce "), "maker": "NVIDIA",
                    "busy": num(f[1]), "mem_used": (num(f[2]) or 0) * 2**20, "mem_total": (num(f[3]) or 0) * 2**20,
                    "temp": num(f[4]), "power": num(f[5]), "power_limit": num(f[6]), "fan": num(f[7]),
                    "clock": num(f[8])}
    for card in sorted((root / "sys/class/drm").glob("card[0-9]")):
        dev = card / "device"
        busy = dev / "gpu_busy_percent"
        if not busy.is_file():
            continue
        read = lambda p: int((dev / p).read_text()) if (dev / p).is_file() else None
        temp = None
        for t in dev.glob("hwmon/hwmon*/temp1_input"):
            temp = int(t.read_text()) / 1000
        return {"name": "Graphics card", "maker": "AMD", "busy": float(read("gpu_busy_percent") or 0),
                "mem_used": read("mem_info_vram_used") or 0, "mem_total": read("mem_info_vram_total") or 0,
                "temp": temp, "power": None, "power_limit": None, "fan": None, "clock": None}
    return None


def gpu_apps(run=subprocess.run) -> list[tuple[str, float]]:
    """Apps using the graphics card, by its memory they hold (MB), biggest first (NVIDIA only)."""
    if not shutil.which("nvidia-smi"):
        return []
    try:
        r = run(["nvidia-smi", "pmon", "-c", "1", "-s", "m"], capture_output=True, text=True, timeout=3)
    except (OSError, subprocess.TimeoutExpired):
        return []
    apps: dict[str, float] = {}
    for line in r.stdout.splitlines():
        f = line.split()
        if line.startswith("#") or len(f) < 5 or not f[1].isdigit():
            continue
        try:                                          # nvidia-smi cuts names short: the program's own name
            name = Path(f"/proc/{f[1]}/comm").read_text().strip()
        except OSError:
            name = f[-1]
        mb = next((float(x) for x in f[3:-1] if re.fullmatch(r"\d+", x)), 0.0)
        apps[nice(name)] = apps.get(nice(name), 0.0) + mb
    return sorted(apps.items(), key=lambda kv: -kv[1])


# ---- temperatures and fans --------------------------------------------------------------------------

# a sensor chip's name → (the group it shows in, the words for it, warm °C, hot °C)
CHIPS = {
    "k10temp": ("Processor", "Processor", 75, 90), "coretemp": ("Processor", "Processor", 75, 90),
    "zenpower": ("Processor", "Processor", 75, 90),
    "amdgpu": ("Graphics", "Graphics card", 75, 90), "nouveau": ("Graphics", "Graphics card", 75, 90),
    "nvme": ("Drives", "Drive", 60, 70), "drivetemp": ("Drives", "Drive", 50, 60),
    "spd5118": ("Memory", "Memory stick", 60, 80), "jc42": ("Memory", "Memory stick", 60, 80),
    "acpitz": ("Board", "Motherboard", 70, 85),
    "r8169_0_500:00": ("Board", "Network chip", 70, 90),
}
GROUP_ORDER = ["Processor", "Graphics", "Drives", "Memory", "Board"]
EXTRA = {"tccd1": "core die 1", "tccd2": "core die 2", "junction": "hottest spot", "mem": "its memory"}


def drive_name(hwmon: Path) -> str | None:
    for p in ("device/model", "device/device/model"):
        f = hwmon / p
        if f.is_file():
            return f.read_text().strip()
    return None


def temperatures(root: Path = Path("/"), gpu_now: dict | None = None) -> list[dict]:
    """Every temperature worth showing: {group, name, temp, warm, hot, state, key}. The main one of each
    chip (Tctl, Composite…) by the chip's own words; a few extra parts by theirs; the Dell board's copies
    of the processor and graphics readings left out (the chips' own are better)."""
    out = []
    counts: dict[str, int] = {}
    for hw in sorted((root / "sys/class/hwmon").glob("hwmon*"), key=lambda p: int(re.sub(r"\D", "", p.name) or 0)):
        try:
            chip = (hw / "name").read_text().strip()
        except OSError:
            continue
        if chip.startswith("r8169"):
            chip = "r8169_0_500:00"
        if chip == "dell_smm":
            for t in sorted(hw.glob("temp*_input")):
                label = (hw / t.name.replace("_input", "_label"))
                if label.is_file() and label.read_text().strip().lower() == "ambient":
                    out.append(_reading("Board", "Inside the case", t, 45, 55, hw))
            continue
        if chip not in CHIPS:
            continue
        group, words, warm, hot = CHIPS[chip]
        counts[chip] = counts.get(chip, 0) + 1
        n = counts[chip]
        if chip in ("nvme", "drivetemp"):
            words = drive_name(hw) or f"Drive {n}"
        elif chip in ("spd5118", "jc42"):
            words = f"Memory stick {n}"
        for t in sorted(hw.glob("temp*_input"), key=lambda p: int(re.sub(r"\D", "", p.name) or 0)):
            # the chip's main reading (Tctl, Composite, edge…), and a few parts worth their own line
            label_f = hw / t.name.replace("_input", "_label")
            label = label_f.read_text().strip().lower() if label_f.is_file() else ""
            if t.name == "temp1_input":
                name = words
            elif label in EXTRA:
                name = f"{words} · {EXTRA[label]}"
            else:
                continue
            crit = hw / t.name.replace("_input", "_crit")
            hot_here = hot
            try:
                c = int(crit.read_text()) / 1000 if crit.is_file() else 0
                if 30 < c < hot_here:
                    hot_here = c
            except (OSError, ValueError):
                pass
            out.append(_reading(group, name, t, min(warm, hot_here - 5), hot_here, hw))
    if gpu_now and gpu_now.get("temp") is not None and not any(r["group"] == "Graphics" for r in out):
        out.append({"group": "Graphics", "name": gpu_now.get("name") or "Graphics card", "temp": gpu_now["temp"],
                    "warm": 75, "hot": 87, "state": level(gpu_now["temp"], 75, 87), "key": "gpu"})
    out = [r for r in out if r["temp"] is not None]
    out.sort(key=lambda r: GROUP_ORDER.index(r["group"]) if r["group"] in GROUP_ORDER else 99)
    return out


def _reading(group, name, path: Path, warm, hot, hw: Path) -> dict:
    try:
        t = int(path.read_text()) / 1000
    except (OSError, ValueError):
        t = None
    return {"group": group, "name": name, "temp": round(t, 1) if t is not None else None, "warm": warm, "hot": hot,
            "state": level(t, warm, hot), "key": f"{hw.name}/{path.name}"}


def fans(root: Path = Path("/"), gpu_now: dict | None = None) -> list[dict]:
    out = []
    for hw in sorted((root / "sys/class/hwmon").glob("hwmon*")):
        for f in sorted(hw.glob("fan*_input")):
            label_f = hw / f.name.replace("_input", "_label")
            label = label_f.read_text().strip() if label_f.is_file() else f"Fan {len(out) + 1}"
            try:
                rpm = int(f.read_text())
            except (OSError, ValueError):
                continue
            label = {"Processor Fan": "Processor fan", "Motherboard Fan": "Case fan"}.get(label, label)
            out.append({"name": label, "rpm": rpm})
    for name in {o["name"] for o in out}:            # three "Case fan" become Case fan 1, 2, 3
        same = [o for o in out if o["name"] == name]
        if len(same) > 1:
            for i, o in enumerate(same, 1):
                o["name"] = f"{name} {i}"
    if gpu_now and gpu_now.get("fan") is not None:
        out.append({"name": "Graphics card fan", "percent": gpu_now["fan"]})
    return out


def cpu_temp(temps: list[dict]) -> float | None:
    return next((r["temp"] for r in temps if r["group"] == "Processor"), None)


def hottest(temps: list[dict]) -> dict | None:
    """The reading closest to its own "hot" mark: the one that matters on the bar."""
    return max(temps, key=lambda r: r["temp"] / r["hot"], default=None)


# ---- disks -----------------------------------------------------------------------------------------

SKIP_FS = {"tmpfs", "devtmpfs", "efivarfs", "squashfs", "overlay", "proc", "sysfs", "cgroup2", "devpts",
           "securityfs", "pstore", "bpf", "tracefs", "debugfs", "configfs", "fusectl", "mqueue", "hugetlbfs",
           "autofs", "binfmt_misc", "ramfs", "nsfs", "fuse.portal", "fuse.gvfsd-fuse", "zram"}


def unescape(path: str) -> str:
    return re.sub(r"\\(\d{3})", lambda m: chr(int(m.group(1), 8)), path)


def mounts(root: Path = Path("/")) -> list[tuple[str, str, str]]:
    """The real filesystems: (device, folder, type), one per device (its shortest folder: / over /home)."""
    seen: dict[str, tuple[str, str, str]] = {}
    for line in (root / "proc/mounts").read_text().splitlines():
        f = line.split()
        if len(f) < 3:
            continue
        dev, where, fs = f[0], unescape(f[1]), f[2]
        if fs in SKIP_FS or not dev.startswith("/dev/") or dev.startswith("/dev/loop") or "/snap/" in where:
            continue
        if dev not in seen or len(where) < len(seen[dev][1]):
            seen[dev] = (dev, where, fs)
    return sorted(seen.values(), key=lambda m: (m[1] != "/", m[1]))


def block_info() -> dict:
    """lsblk's view: every partition's drive (model, connection, spinning or not) and label."""
    try:
        r = subprocess.run(["lsblk", "-J", "-o", "NAME,PATH,MODEL,LABEL,TRAN,ROTA,TYPE,MOUNTPOINTS,SIZE", "-b"],
                           capture_output=True, text=True, timeout=3)
        devs = json.loads(r.stdout)["blockdevices"]
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        return {"parts": {}, "idle": []}
    parts, idle = {}, []
    for d in devs:
        if d.get("type") != "disk" or d["name"].startswith(("loop", "zram", "sr")):
            continue
        drive = {"model": (d.get("model") or "").strip(), "tran": d.get("tran") or "", "rota": bool(d.get("rota")),
                 "size": int(d.get("size") or 0)}
        kids = d.get("children") or []
        used = False
        for c in kids + [d]:
            parts[c["path"]] = dict(drive, label=c.get("label") or "")
            used = used or any(m for m in (c.get("mountpoints") or []) if m)
        if not used and drive["size"] > 0:
            idle.append(drive)
    return {"parts": parts, "idle": idle}


def disks(root: Path = Path("/"), info: dict | None = None) -> list[dict]:
    """Each real filesystem: its name in plain words, the drive it is on, its size, used and free."""
    info = info if info is not None else (block_info() if root == Path("/") else {"parts": {}, "idle": []})
    out = []
    for dev, where, fs in mounts(root):
        try:
            st = os.statvfs(where if root == Path("/") else root / where.lstrip("/"))
        except OSError:
            continue
        total = st.f_blocks * st.f_frsize
        free = st.f_bavail * st.f_frsize
        if total <= 0:
            continue
        used = total - st.f_bfree * st.f_frsize
        p = info["parts"].get(dev, {})
        name = ("System" if where == "/" else "Home" if where == "/home" else "Boot" if where in ("/boot", "/efi", "/boot/efi")
                else p.get("label") or Path(where).name or where)
        kind = "usb" if p.get("tran") == "usb" else "hdd" if p.get("rota") else "nvme" if p.get("tran") == "nvme" else "ssd"
        out.append({"name": name, "where": where, "device": dev, "fs": fs, "model": p.get("model", ""), "kind": kind,
                    "total": total, "used": used, "free": free,
                    "percent": round(100.0 * used / (used + free), 1) if used + free else 0.0})
    return out


# ---- apps by what they use ------------------------------------------------------------------------

def proc_scan(root: Path = Path("/")) -> dict[int, tuple[str, int, int]]:
    """Every running program: pid → (name, processor ticks so far, memory in bytes)."""
    page = os.sysconf("SC_PAGE_SIZE")
    out = {}
    for d in (root / "proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            stat = (d / "stat").read_text()
            name = stat[stat.index("(") + 1:stat.rindex(")")]
            rest = stat[stat.rindex(")") + 2:].split()
            ticks = int(rest[11]) + int(rest[12])
            rss = int((d / "statm").read_text().split()[1]) * page
        except (OSError, ValueError, IndexError):
            continue
        out[int(d.name)] = (name, ticks, rss)
    return out


NICE = {"chrome": "Google Chrome", "chromium": "Chromium", "firefox": "Firefox", "Xwayland": "XWayland",
        "claude": "Claude", "claude-desktop": "Claude", "exogui": "eXoDOS", "Xorg": "Xorg (the login screen)", "waybar": "the bar", "sway": "Sway (the desktop)", "python3": "Python programs",
        "insync": "Insync", "dropbox": "Dropbox", "alacritty": "Alacritty", "steam": "Steam", "Discord": "Discord",
        "steamwebhelper": "Steam", "gtklock": "the lock screen", "mako": "the notifications", "pipewire": "sound (PipeWire)",
        "wireplumber": "sound (WirePlumber)", "pipewire-pulse": "sound (PipeWire)"}


def nice(name: str) -> str:
    base = re.split(r"[ :/]", name)[0]
    return NICE.get(base, NICE.get(base.lower(), base))


def top_cpu(before: dict, after: dict, seconds: float, cores: int, n: int = 5) -> list[tuple[str, float]]:
    """The busiest apps between two scans, as % of the whole processor; an app's helpers added in
    (Chrome is dozens of programs)."""
    hz = os.sysconf("SC_CLK_TCK")
    apps: dict[str, float] = {}
    for pid, (name, ticks, _rss) in after.items():
        if pid in before and before[pid][0] == name:
            d = ticks - before[pid][1]
            if d > 0:
                apps[nice(name)] = apps.get(nice(name), 0.0) + 100.0 * d / hz / max(seconds, 0.1) / max(cores, 1)
    return sorted(((k, round(v, 1)) for k, v in apps.items() if v >= 0.1), key=lambda kv: -kv[1])[:n]


def top_memory(scan: dict, n: int = 5) -> list[tuple[str, int]]:
    apps: dict[str, int] = {}
    for _pid, (name, _t, rss) in scan.items():
        apps[nice(name)] = apps.get(nice(name), 0) + rss
    return sorted(apps.items(), key=lambda kv: -kv[1])[:n]


# ---- words -----------------------------------------------------------------------------------------

def size(b: float) -> str:
    """Bytes in plain words: 931 GB, 12.3 GB, 647 MB."""
    for unit, n in (("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
        if b >= n:
            v = b / n
            return f"{v:.1f} {unit}" if v < 100 else f"{v:.0f} {unit}"
    return f"{int(b)} B"


def gib(b: float) -> str:
    """Memory in GB as the memory stick says it (1024s): 31.2 GB."""
    v = b / 2**30
    return f"{v:.1f} GB" if v >= 1 else f"{b / 2**20:.0f} MB"


def duration(seconds: float) -> str:
    d, rem = divmod(int(seconds), 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    return f"{d} day{'s' if d != 1 else ''}, {h} h" if d else f"{h} h {m} min" if h else f"{m} min"


# ---- the sampler's file ----------------------------------------------------------------------------

def read_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def fresh(state: dict, within: float = 3 * EVERY) -> bool:
    return bool(state) and time.time() - state.get("time", 0) < within


class Sampler:
    """One reading of everything every EVERY seconds; keeps KEEP of them for the graphs."""

    def __init__(self, history: dict | None = None):
        self.last = cpu_times()
        self.history = {k: list((history or {}).get(k, []))[-KEEP:] for k in HISTORY_KEYS}
        self.cores = max(len(self.last) - 1, 1)
        self.now: dict = {}

    def sample(self, with_gpu: bool = True) -> dict:
        times = cpu_times()
        use = usage(self.last, times)
        self.last = times
        g = gpu() if with_gpu else self.now.get("gpu")
        temps = temperatures(gpu_now=g)
        mem = memory()
        load, up = load_and_uptime()
        self.now = {"time": time.time(), "cpu": use.get("cpu", 0.0),
                    "cores": [use[k] for k in sorted((k for k in use if k != "cpu"), key=lambda k: int(k[3:]))],
                    "speed": cpu_speed(), "load": load, "uptime": up, "memory": mem, "gpu": g, "temps": temps,
                    "fans": fans(gpu_now=g)}
        for k, v in (("cpu", self.now["cpu"]), ("memory", mem["percent"]), ("gpu", (g or {}).get("busy")),
                     ("cpu_temp", cpu_temp(temps)), ("gpu_temp", (g or {}).get("temp"))):
            self.history[k] = (self.history[k] + [v])[-KEEP:]
        self.now["history"] = self.history
        return self.now

    def write(self):
        RUNTIME.mkdir(parents=True, exist_ok=True)
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.now))
        tmp.replace(STATE)
