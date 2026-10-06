#!/usr/bin/env python3
"""Writes displayForge's design page from build.py's checked drawings."""
import importlib.util as _u, os as _o
_s = _u.spec_from_file_location("build", _o.path.join(_o.path.dirname(__file__), "build-drawings.py")); build = _u.module_from_spec(_s); _s.loader.exec_module(build)

S = build.SCREENS
T = lambda k: build.term(S[k])

body = f'''
<div class="wrap">

<header class="stack">
  <div class="eyebrow">displayForge · design proposal · 5 October 2026</div>
  <h1>displayForge, screen by screen</h1>
  <p class="lede prose">Screen settings for the KognogOS desktop, in the terminal: arrange your screens, pick resolution and refresh rate, size, rotation, the main screen and brightness. Every screen is drawn here before any code is written. Javier approved it on 5 October, with the changes listed below.</p>
  <p class="prose">It follows grubForge 2.0 and alacrittyForge on purpose: the same frame, the same menu bar with underlined letters, a form for settings, and a review before every save. Every drawing is exactly <b>100 columns</b> wide, the size of a small text console. The drawings show <b>your</b> three Sceptre Y27 screens, numbered the way your workspaces already number them: <b>1 is the middle one</b> (the main one, ★), 2 the left, 3 the right.</p>
  <nav class="toc" aria-label="Contents">
    <a href="#questions">Decided</a><a href="#screens">Screens</a><a href="#settings">Settings</a><a href="#keep">Keep or go back</a><a href="#arrange">Arrange</a><a href="#brightness">Brightness</a><a href="#identify">Identify</a><a href="#save">Save</a><a href="#keys">Keys</a><a href="#plan">How it gets built</a>
  </nav>
</header>

<section id="questions">
  <div class="decide">
    <h3>Decided · Javier, 5 October</h3>
    <ol>
      <li><b>Approved, with changes</b>: <em>"Wow!!!! I love what you have done! Let's go!"</em> The seven open questions go with the recommendations: five screens for 0.1.0 (profiles later); try first with <kbd>F9</kbd> and the countdown, save with <kbd>F10</kbd>; "main screen" is where the workspaces start; brightness is not saved; only real options are offered; saved to <code>~/.config/sway/outputs</code> with a backup; night light a later version.</li>
      <li><b>Any arrangement</b>: four in a row, three over three, a fourth under screen 1. Sway places screens anywhere; Arrange handles every layout.</li>
      <li><b>Size below 100 %</b>: 80 % and 90 % added, with a note that older X11 apps look slightly blurry at non-whole sizes. Proven in the test machine before it is offered.</li>
      <li><b>Brightness in tens</b>, 10 % to 100 %, per screen and for all screens.</li>
      <li><b>HDR</b> only for screens that support it. Sway reports it per screen; your Sceptre Y27s report no HDR, so for them it reads "not supported by this screen".</li>
      <li><b>Names</b>: name your screens in Identify (Main, Left, Right…); displayForge shows the names everywhere.</li>
    </ol>
  </div>
</section>

<section id="screens">
  <h2>1 · Screens</h2>
  <p class="prose">The first screen answers "are my screens set up right?": a drawing of your screens as they sit on the desk, the one you picked, and anything that needs attention. With one screen it shows one box; with six, six.</p>
  {T("screens")}
  <p class="cap">"Needs attention" would show, for example: a screen that is switched off, screens that overlap, or saved settings that differ from what is on screen (then a button puts back the saved ones). Today nothing does, so it says so in green.</p>
</section>

<section id="settings">
  <h2>2 · Settings</h2>
  <p class="prose">A form, like grubForge's: your screens on the left, the picked one's settings on the right. Everything is picked from what the screen really offers; nothing is typed except an exact brightness. The drawing shows a change waiting: 120 Hz instead of 144.</p>
  {T("settings")}
  <p class="cap">Resolution opens a list of the sizes the screen reports. Refresh rate shows only the rates that size supports. "Smooth motion" is adaptive sync (FreeSync); off by default because some screens flicker with it.</p>
</section>

<section id="keep">
  <h2>Keep or go back</h2>
  <p class="prose">Every change that can leave a screen black (resolution, refresh rate, size, rotation, position, switching a screen off) is tried with a countdown. If you see the question, press Enter. If the screen went black and you see nothing, wait: it goes back by itself.</p>
  {T("keep")}
</section>

<section id="arrange">
  <h2>3 · Arrange</h2>
  <p class="prose">Move a screen with the arrow keys, or say where it goes: left of, right of, above or below another. Edges snap together, so there are no gaps or overlaps. The drawing shows screen 2 moved from the left to the right of screen 1.</p>
  {T("arrange")}
</section>

<section id="brightness">
  <h2>4 · Brightness</h2>
  <p class="prose">One bar per screen, changed at once, or all screens together. It talks to the screens directly (the same way your monitor's own buttons do), so it needs no password and nothing to save.</p>
  {T("brightness")}
</section>

<section id="identify">
  <h2>5 · Identify</h2>
  <p class="prose">Your three screens are the same model and report the same serial number, so the computer can't tell which brightness control belongs to which screen (ddcutil says so itself). Identify asks you once: a big number appears on each screen, one screen at a time goes dark for three seconds, and you say which. The answer is remembered. On computers with different screens it is never needed.</p>
  {T("identify")}
</section>

<section id="save">
  <h2>Saving</h2>
  <p class="prose">A review first, like every Forge app: each change, before and after. Then the file is written, a backup having been made first, and a closing note says what was written and where.</p>
  {T("save")}
</section>

<section id="keys">
  <h2>Keys</h2>
  <div class="tw"><table>
    <tr><th>Keys</th><th>What happens</th></tr>
    <tr><td><kbd>1</kbd>–<kbd>5</kbd>, or the underlined letter</td><td>Go to a screen: Screens, Settings, Arrange, Brightness, Identify</td></tr>
    <tr><td><kbd>↑</kbd> <kbd>↓</kbd> · <kbd>Tab</kbd></td><td>Pick a screen · move into its settings</td></tr>
    <tr><td><kbd>←</kbd> <kbd>→</kbd> <kbd>↑</kbd> <kbd>↓</kbd> (Arrange)</td><td>Move the picked screen</td></tr>
    <tr><td><kbd>F9</kbd></td><td>Try the changes live, with the countdown</td></tr>
    <tr><td><kbd>F10</kbd></td><td>Save (with the review first)</td></tr>
    <tr><td><kbd>Esc</kbd></td><td>Put back what you haven't tried yet · go back now (countdown)</td></tr>
    <tr><td><kbd>F1</kbd> · <kbd>?</kbd></td><td>Help · all keys</td></tr>
  </table></div>
</section>

<section id="plan">
  <h2>How it gets built</h2>
  <ol class="prose">
    <li><b>Your answers</b> to the questions above, and any change to the drawings.</li>
    <li><b>Build on forgekit</b>, in the Forge Suite's <code>displayforge/</code> section: read the screens, the form, the countdown, the review and save, then Arrange, Brightness and Identify.</li>
    <li><b>Tests</b>: one, two and three screens in a virtual machine; 100 columns; a plain text console; the countdown in the failing direction (a mode the screen can't show).</li>
    <li><b>Your run</b> on the desktop with a written test list, then a release on GitHub and the AUR.</li>
  </ol>
  <p class="prose">Until then your screens keep working exactly as they are.</p>
</section>

</div>
'''

open("v0.1.0-screens.html", "w").write(open("page-head.html").read() + body)
print("written", len(body), "chars")
