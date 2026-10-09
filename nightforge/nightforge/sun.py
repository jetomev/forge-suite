"""Sunrise and sunset for a place and a day, worked out on the computer (no internet).

The NOAA solar calculator's formulas (the same idea wlsunset uses), good to about a minute
between the polar circles. Above them a day can have no sunset or no sunrise: then None.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone


def _times(day: date, lat: float, lon: float) -> tuple[float | None, float | None]:
    """Sunrise and sunset as minutes after midnight UTC, or None when the sun doesn't rise or set."""
    n = day.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1)                     # the fractional year, in radians
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    phi = math.radians(lat)
    zenith = math.radians(90.833)                       # the sun's edge, with the air's bending
    c = (math.cos(zenith) / (math.cos(phi) * math.cos(decl))) - math.tan(phi) * math.tan(decl)
    if c < -1 or c > 1:
        return None, None
    ha = math.degrees(math.acos(c))
    rise = 720 - 4 * (lon + ha) - eqtime
    set_ = 720 - 4 * (lon - ha) - eqtime
    return rise, set_


def sun_times(day: date, lat: float, lon: float, tz=None) -> tuple[datetime | None, datetime | None]:
    """(sunrise, sunset) on `day` at the place, as local times (the computer's time zone by default)."""
    rise, set_ = _times(day, lat, lon)
    if rise is None:
        return None, None
    midnight = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    to_local = (lambda d: d.astimezone(tz)) if tz else (lambda d: d.astimezone())
    return to_local(midnight + timedelta(minutes=rise)), to_local(midnight + timedelta(minutes=set_))
