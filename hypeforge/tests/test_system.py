"""The system readings (2026-10-17, Javier: "icons and popups for CPU, GPU, Temperature, Memory, Disks
Space"): every reader on a made-up /proc and /sys, so the numbers in the pop-ups are checked against
known answers, not against this computer's."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "applets/system"))
import hfsys  # noqa: E402


def tree(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp(prefix="hfsys."))
    for rel, text in files.items():
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    return root


class Processor(unittest.TestCase):
    def test_busy_is_the_share_of_ticks_not_idle_or_waiting(self):
        a = tree({"proc/stat": "cpu  100 0 100 700 100 0 0 0 0 0\ncpu0 50 0 50 350 50 0 0 0\ncpu1 50 0 50 350 50 0 0 0\nintr 1\n"})
        b = tree({"proc/stat": "cpu  200 0 200 1300 100 0 0 0 0 0\ncpu0 150 0 50 400 50 0 0 0\ncpu1 50 0 150 900 50 0 0 0\nintr 1\n"})
        use = hfsys.usage(hfsys.cpu_times(a), hfsys.cpu_times(b))
        self.assertEqual(use["cpu"], 25.0)          # 200 busy of 800 ticks
        self.assertEqual(use["cpu0"], round(100 * 100 / 150, 1))
        self.assertEqual(use["cpu1"], round(100 * 100 / 650, 1))

    def test_the_model_in_plain_words(self):
        r = tree({"proc/cpuinfo": "processor\t: 0\nmodel name\t: AMD Ryzen 7 7700 8-Core Processor\n"})
        self.assertEqual(hfsys.cpu_model(r), "AMD Ryzen 7 7700")
        r = tree({"proc/cpuinfo": "model name\t: Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz\n"})
        self.assertEqual(hfsys.cpu_model(r), "Intel Core i7-8700")

    def test_the_busiest_apps_add_up_their_helpers(self):
        hz = os.sysconf("SC_CLK_TCK")
        before = {1: ("chrome", 0, 0), 2: ("chrome", 0, 0), 3: ("sway", 0, 0), 4: ("gone", 0, 0)}
        after = {1: ("chrome", hz, 0), 2: ("chrome", hz, 0), 3: ("sway", hz // 2, 0), 5: ("new", 99, 0)}
        top = hfsys.top_cpu(before, after, seconds=1.0, cores=4)
        self.assertEqual(top[0], ("Google Chrome", 50.0))   # two seconds of work in one second, of four cores
        self.assertEqual(top[1][0], "Sway (the desktop)")
        self.assertEqual(len(top), 2, "a program that ended or just started is left out")


class Memory(unittest.TestCase):
    def test_in_use_cache_and_free_add_up(self):
        r = tree({"proc/meminfo": "MemTotal: 1000 kB\nMemFree: 200 kB\nMemAvailable: 600 kB\nBuffers: 50 kB\n"
                                  "Cached: 350 kB\nSReclaimable: 20 kB\nShmem: 20 kB\nSwapTotal: 500 kB\nSwapFree: 400 kB\n"})
        m = hfsys.memory(r)
        self.assertEqual(m["used"], 400 * 1024)
        self.assertEqual(m["cache"], 400 * 1024)
        self.assertEqual(m["used"] + m["cache"] + m["free"], m["total"])
        self.assertEqual(m["percent"], 40.0)
        self.assertEqual(m["swap_used"], 100 * 1024)


class Temperatures(unittest.TestCase):
    def setUp(self):
        self.root = tree({
            "sys/class/hwmon/hwmon0/name": "acpitz\n", "sys/class/hwmon/hwmon0/temp1_input": "50500\n",
            "sys/class/hwmon/hwmon1/name": "nvme\n", "sys/class/hwmon/hwmon1/device/model": "KINGSTON SNV3S1000G\n",
            "sys/class/hwmon/hwmon1/temp1_input": "29850\n", "sys/class/hwmon/hwmon1/temp1_label": "Composite\n",
            "sys/class/hwmon/hwmon1/temp2_input": "46850\n", "sys/class/hwmon/hwmon1/temp2_label": "Sensor 2\n",
            "sys/class/hwmon/hwmon1/temp1_crit": "84850\n",
            "sys/class/hwmon/hwmon3/name": "k10temp\n", "sys/class/hwmon/hwmon3/temp1_input": "91000\n",
            "sys/class/hwmon/hwmon3/temp1_label": "Tctl\n", "sys/class/hwmon/hwmon3/temp3_input": "46750\n",
            "sys/class/hwmon/hwmon3/temp3_label": "Tccd1\n",
            "sys/class/hwmon/hwmon4/name": "dell_smm\n",
            "sys/class/hwmon/hwmon4/temp5_input": "36000\n", "sys/class/hwmon/hwmon4/temp5_label": "GPU\n",
            "sys/class/hwmon/hwmon4/temp6_input": "28000\n", "sys/class/hwmon/hwmon4/temp6_label": "Ambient\n",
            "sys/class/hwmon/hwmon4/fan1_input": "1460\n", "sys/class/hwmon/hwmon4/fan1_label": "Processor Fan\n",
            "sys/class/hwmon/hwmon4/fan2_input": "1092\n", "sys/class/hwmon/hwmon4/fan2_label": "Motherboard Fan\n",
            "sys/class/hwmon/hwmon4/fan3_input": "1180\n", "sys/class/hwmon/hwmon4/fan3_label": "Motherboard Fan\n",
            "sys/class/hwmon/hwmon6/name": "spd5118\n", "sys/class/hwmon/hwmon6/temp1_input": "34000\n",
            "sys/class/hwmon/hwmon7/name": "spd5118\n", "sys/class/hwmon/hwmon7/temp1_input": "33500\n",
            "sys/class/hwmon/hwmon8/name": "some_unknown_chip\n", "sys/class/hwmon/hwmon8/temp1_input": "99000\n",
        })
        self.gpu = {"name": "GeForce RTX 3060", "temp": 41.0, "fan": 30.0}
        self.temps = hfsys.temperatures(self.root, gpu_now=self.gpu)

    def names(self):
        return [r["name"] for r in self.temps]

    def test_each_chip_by_its_own_words_in_group_order(self):
        self.assertEqual(self.names(), ["Processor", "Processor · core die 1", "GeForce RTX 3060", "KINGSTON SNV3S1000G",
                                        "Memory stick 1", "Memory stick 2", "Motherboard", "Inside the case"])

    def test_copies_and_unknown_chips_are_left_out(self):
        """The Dell board's own "GPU" reading copies the card's; an NVMe's extra sensors and a chip we
        don't know have no plain words: they stay out."""
        self.assertNotIn(36.0, [r["temp"] for r in self.temps])
        self.assertNotIn(46.85, [r["temp"] for r in self.temps])
        self.assertNotIn(99.0, [r["temp"] for r in self.temps])

    def test_hot_is_hot_and_the_bar_shows_the_worst(self):
        cpu = self.temps[0]
        self.assertEqual(cpu["state"], "critical")
        self.assertEqual(hfsys.hottest(self.temps)["name"], "Processor")
        self.assertEqual(hfsys.cpu_temp(self.temps), 91.0)

    def test_a_drive_takes_its_own_critical_mark_when_lower(self):
        drive = next(r for r in self.temps if r["group"] == "Drives")
        self.assertEqual(drive["hot"], 70)               # its crit is 84.85: ours (70) is lower, ours stays
        self.assertEqual(drive["state"], "ok")

    def test_fans_get_plain_names_and_numbers(self):
        f = hfsys.fans(self.root, gpu_now=self.gpu)
        self.assertEqual([x["name"] for x in f], ["Processor fan", "Case fan 1", "Case fan 2", "Graphics card fan"])
        self.assertEqual(f[-1]["percent"], 30.0)


class Disks(unittest.TestCase):
    def test_one_line_per_drive_part_and_no_snaps_or_loops(self):
        r = tree({"proc/mounts": "\n".join([
            "/dev/sda2 / btrfs rw 0 0", "/dev/sda2 /home btrfs rw 0 0", "/dev/sda1 /boot vfat rw 0 0",
            "/dev/loop3 /var/lib/snapd/snap/snapd/1 squashfs ro 0 0", "tmpfs /tmp tmpfs rw 0 0",
            r"/dev/sdc1 /mnt/my\040book ext4 rw 0 0", "/dev/sdd1 /var/lib/snapd/snap/x ext4 rw 0 0"])})
        self.assertEqual(hfsys.mounts(r), [("/dev/sda2", "/", "btrfs"), ("/dev/sda1", "/boot", "vfat"),
                                           ("/dev/sdc1", "/mnt/my book", "ext4")])


class Words(unittest.TestCase):
    def test_levels(self):
        self.assertEqual([hfsys.level(v, *hfsys.BUSY) for v in (None, 10, 70, 95)], ["ok", "ok", "warning", "critical"])

    def test_sizes_and_times(self):
        self.assertEqual(hfsys.size(931e9), "931 GB")
        self.assertEqual(hfsys.size(12.34e9), "12.3 GB")
        self.assertEqual(hfsys.gib(31.2 * 2**30), "31.2 GB")
        self.assertEqual(hfsys.gib(600 * 2**20), "600 MB")
        self.assertEqual(hfsys.duration(4920), "1 h 22 min")
        self.assertEqual(hfsys.duration(2 * 86400 + 3600), "2 days, 1 h")


class BarPieces(unittest.TestCase):
    TOOL = REPO / "applets/system/hypeforge-system"

    def piece(self, part, state):
        run = Path(tempfile.mkdtemp())
        (run / "hypeforge-system").mkdir()
        (run / "hypeforge-system/now.json").write_text(json.dumps(state))
        out = subprocess.run([sys.executable, str(self.TOOL), "bar", part], capture_output=True, text=True,
                             env=dict(os.environ, XDG_RUNTIME_DIR=str(run)), timeout=10).stdout
        return json.loads(out)

    def test_the_card_piece_hides_on_a_computer_without_one(self):
        import time
        self.assertEqual(self.piece("gpu", {"time": time.time(), "gpu": None, "temps": []})["text"], "")

    def test_the_temperature_piece_turns_red_when_something_is_hot(self):
        import time
        temps = [{"group": "Processor", "name": "Processor", "temp": 55.0, "warm": 75, "hot": 90, "state": "ok"},
                 {"group": "Drives", "name": "A drive", "temp": 72.0, "warm": 60, "hot": 70, "state": "critical"}]
        p = self.piece("temp", {"time": time.time(), "gpu": None, "temps": temps})
        self.assertIn("55°", p["text"])                  # the processor's number on the bar…
        self.assertEqual(p["class"], "critical")         # …but red, because a drive is hot
        self.assertIn("A drive is hot", p["tooltip"])

    def test_every_piece_opens_its_own_pop_up_from_the_bar_place(self):
        sys.path.insert(0, str(REPO / "tests"))
        text = (REPO / "sway/waybar/modules.jsonc").read_text()
        import importlib.machinery
        import importlib.util
        loader = importlib.machinery.SourceFileLoader("hb_sys", str(REPO / "applets/bar/hypeforge-bar"))
        spec = importlib.util.spec_from_loader("hb_sys", loader)
        hb = importlib.util.module_from_spec(spec)
        loader.exec_module(hb)
        shared = json.loads(hb.strip_comments(text))
        for module, part in (("cpu", "cpu"), ("custom/gpu", "gpu"), ("custom/temperature", "temp"),
                             ("memory", "memory"), ("disk", "disk")):
            self.assertIn(f"hypeforge-panel system --part {part} {{popup}}", shared[module]["on-click"], module)
            if module.startswith("custom/"):
                self.assertIn("interval", shared[module], f"{module}: a piece without an interval runs once")


if __name__ == "__main__":
    unittest.main()
