#!/usr/bin/env python3
"""Writes nightForge's design page from build-drawings.py's checked drawings."""
import importlib.util as _u, os as _o
_here = _o.path.dirname(_o.path.abspath(__file__))
_s = _u.spec_from_file_location("build", _o.path.join(_here, "build-drawings.py")); build = _u.module_from_spec(_s); _s.loader.exec_module(build)

S = build.SCREENS
T = lambda k: build.term(S[k])
BAR = build.term(build.s_bar())

body = f'''
<div class="wrap">

<header class="stack">
  <div class="eyebrow">nightForge · design proposal · 9 October 2026</div>
  <h1>nightForge, screen by screen</h1>
  <p class="lede prose">The night light's own app: on or off, how warm the evening gets, and when. In the terminal, like every Forge app, and a page of hypeForge Settings.</p>
  <p class="prose">Today the night light is <b>wlsunset</b>, started at login with Miami's place, 4000 K at night and 6500 K by day, and nothing to change it with (issue #44). The drawings use those real values, and your real sun today in Miami: down at <b>19:00</b>, up at <b>07:15</b>, worked out on this computer. Every drawing is exactly <b>100 columns</b> wide.</p>
  <nav class="toc" aria-label="Contents">
    <a href="#questions">Questions</a><a href="#night">Night Light</a><a href="#preview">Preview</a><a href="#schedule">Schedule</a><a href="#bar">The bar</a><a href="#save">Save</a><a href="#runs">Where it runs</a><a href="#plan">How it gets built</a>
  </nav>
</header>

<section id="questions" class="stack">
  <div class="decide">
    <h3>From your issue (#44, 7 October)</h3>
    <p><em>"Night-Light → needs its own app to be able to activate/deactivate, modify its settings, etc. … nightForge… I guess."</em> On / off, the warmth, the place or fixed times, and a sign on the bar while it's on.</p>
  </div>
  <h2>Questions for you</h2>
  <p class="prose">Each with my recommendation in bold. Say "go" and they're all answered that way.</p>
  <ol class="prose">
    <li><b>The name:</b> nightForge, your first guess. <span class="rec">Recommended: keep it.</span></li>
    <li><b>Off means off</b>, now and at every login, until you switch it on again. <span class="rec">Recommended: yes.</span></li>
    <li><b>Right now</b> (Warm Now / Daylight Now) holds until you pick Automatic again, or log out. Handy for a late movie, or for checking colours in a photo. <span class="rec">Recommended: yes.</span></li>
    <li><b>Evening warmth:</b> five steps, 3000 to 5000 K, with words for each, plus any number you type (1000–6500). <span class="rec">Recommended: yes.</span></li>
    <li><b>Daytime</b> stays the screens' own white (6500 K), with no setting for it. One less thing to get wrong. <span class="rec">Recommended: yes.</span></li>
    <li><b>Your place</b> is two numbers (latitude, longitude), shown in plain words. Nothing is looked up online, so no city names. <span class="rec">Recommended: yes.</span> Or <b>Fixed Times</b>: warm from, daylight from, and a fade.</li>
    <li><b>A moon on the bar</b> (☾) while the screens are warm; a click opens nightForge. <span class="rec">Recommended: yes.</span></li>
    <li><b>Who runs the night light:</b> nightForge does. At login hypeForge runs <code>nightforge start</code>, which reads nightForge's settings and starts wlsunset; saving restarts it at once. The line in hypeForge's Sway settings changes to that. <span class="rec">Recommended: yes.</span></li>
    <li><b>Inside hypeForge Settings</b> as the <b>Night light</b> page; the Home page's Night light card opens it. <span class="rec">Recommended: yes.</span></li>
    <li><b>Version:</b> 0.1.0 while it's built, 1.0.0 after your run, then the AUR after your install test. <span class="rec">Recommended: yes.</span></li>
  </ol>
</section>

<section id="night">
  <h2>1 · Night Light</h2>
  <p class="prose">What's happening now and the main switch. <b>Right now</b> overrides the clock for a while. <b>Evening warmth</b> is how orange the evening gets; <b>Preview</b> shows a warmth on your screens for ten seconds before you choose it.</p>
  {T("night")}
</section>

<section id="preview">
  <h2>Preview</h2>
  <p class="prose">Like displayForge's countdown: it goes back by itself, so nothing gets stuck.</p>
  {T("preview")}
</section>

<section id="schedule">
  <h2>2 · Schedule</h2>
  <p class="prose"><b>By the sun at your place</b> (today's way, Miami) follows the seasons by itself. <b>Fixed times</b> are the same every day. The box shows your real sun times, worked out on this computer, so you can see what the numbers mean.</p>
  {T("schedule")}
</section>

<section id="bar">
  <h2>The bar</h2>
  <p class="prose">A small moon on the right side of the bar while the screens are warm; gone by day. A click opens nightForge.</p>
  {BAR}
</section>

<section id="save">
  <h2>Saving</h2>
  <p class="prose">A review first, a backup, then the night light restarts with the new settings at once, and at every login after.</p>
  {T("save")}
</section>

<section id="runs">
  <h2>Where it runs</h2>
  <ul class="prose">
    <li><b>Desktop:</b> made for <b>KognogOS's hypeForge desktop on Sway</b>. The night light itself (wlsunset) works on Sway and other desktops of its family (wlroots); not on KDE or GNOME, which have their own.</li>
    <li><b>Terminal:</b> a terminal app; any terminal window, and a <b>plain text console</b> too, where it edits the settings for the next login (the screens can't be warmed from there).</li>
    <li><b>Distribution:</b> written for <b>KognogOS</b>; needs Python, Textual, forgekit and wlsunset, so it runs on any Linux distribution that has them.</li>
  </ul>
</section>

<section id="plan">
  <h2>How it gets built</h2>
  <ol class="prose">
    <li><b>Your answers</b>, and any change to the drawings.</li>
    <li><b>nightForge on forgekit</b>, in <code>nightforge/</code>: the settings, <code>nightforge start</code>, the two pages, preview and save.</li>
    <li><b>hypeForge:</b> the login line, the moon on the bar, the Settings page and its Home card, Help page 17.</li>
    <li><b>Tests</b>, each seen failing first; pictures of every page; the start-and-restart tried on the hidden bench before your desktop.</li>
    <li><b>Your run</b>, a release, and the AUR after your install test.</li>
  </ol>
</section>

</div>
'''

out = _o.path.join(_here, "v0.1.0-screens.html")
open(out, "w").write(open(_o.path.join(_here, "page-head.html")).read() + body)
print("written", out, len(body), "chars")
