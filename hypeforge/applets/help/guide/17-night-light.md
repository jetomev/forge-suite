# Night light

**What it does:** after sunset the screens turn a little warmer (less blue), and at sunrise they
go back to normal. Easier on the eyes in the evening; no effect on screenshots or on what
you share.

## How it works

hypeForge starts **wlsunset** with your session. It works out sunset and sunrise from a place
(today: Miami, set in `sway/config`) and shifts the colour slowly over about an hour each way,
so you never see it jump. Night is 4000 K, day is 6500 K (the usual screen white).

- Nothing to press. If the screens look slightly orange in the evening, it is working.
- To stop it for the rest of the session: `pkill -x wlsunset` in a terminal. It comes back at
  the next login.
- Not installed yet? `nog install wlsunset` — hypeForge only starts it when it is there.

## Coming

The place, the two temperatures and an on/off switch move into the **Screens** / **Power & Lock**
Forge apps (hypeForge Settings).
