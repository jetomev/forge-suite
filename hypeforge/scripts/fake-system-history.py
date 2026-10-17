#!/usr/bin/env python3
"""Three minutes of made-up system history for a preview (2026-10-17): this computer's readings now, and
a gentle made-up past for the graphs (a preview's hidden screen has no sampler running for minutes).
Writes $XDG_RUNTIME_DIR/hypeforge-system/now.json — run it with a bench's own XDG_RUNTIME_DIR, never the
desktop's."""

import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "applets/system"))
import hfsys  # noqa: E402

random.seed(17)
s = hfsys.Sampler()
time.sleep(0.5)
now = s.sample()
n = hfsys.KEEP


def wave(base, swing, spikes=()):
    out = []
    for i in range(n):
        v = base + swing * math.sin(i / 9) + random.uniform(-swing, swing) / 2
        for at, height in spikes:
            v += height * math.exp(-((i - at) / 3) ** 2)
        out.append(round(max(0.0, min(v, 100.0)), 1))
    return out


cpu_t = hfsys.cpu_temp(now["temps"]) or 50
gpu_t = (now.get("gpu") or {}).get("temp") or 40
s.history = {"cpu": wave(12, 5, ((30, 55), (70, 25))), "memory": wave(now["memory"]["percent"], 0.6),
             "gpu": wave(14, 4, ((50, 40),)), "cpu_temp": wave(cpu_t, 2, ((32, 14),)), "gpu_temp": wave(gpu_t, 1, ((52, 8),))}
now["history"] = s.history
now["time"] = time.time() + 600          # stays "fresh" through the preview
s.now = now
s.write()
print(hfsys.STATE)
