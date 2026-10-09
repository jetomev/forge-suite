#!/usr/bin/env python3
"""Writes defaultappsForge's design page from build-drawings.py's checked drawings."""
import importlib.util as _u, os as _o
_here = _o.path.dirname(_o.path.abspath(__file__))
_s = _u.spec_from_file_location("build", _o.path.join(_here, "build-drawings.py")); build = _u.module_from_spec(_s); _s.loader.exec_module(build)

S = build.SCREENS
T = lambda k: build.term(S[k])

body = f'''
<div class="wrap">

<header class="stack">
  <div class="eyebrow">defaultappsForge · design proposal · 9 October 2026</div>
  <h1>defaultappsForge, screen by screen</h1>
  <p class="lede prose">Which app opens what: links, folders, text, PDFs, pictures, music, video, documents, archives. In the terminal, like every Forge app, and a page of hypeForge Settings.</p>
  <p class="prose">Today the only way to choose on the Sway desktop is KDE's page (it leaves with KDE) or a terminal command (issue #19). The drawings show <b>your</b> desktop as it really is right now, read from <code>~/.config/mimeapps.list</code> and from what the system answers for each kind of file. Every drawing is exactly <b>100 columns</b> wide.</p>
  <nav class="toc" aria-label="Contents">
    <a href="#found">What we found</a><a href="#questions">Questions</a><a href="#kinds">Kinds</a><a href="#pick">Change</a><a href="#types">File Types</a><a href="#save">Save</a><a href="#runs">Where it runs</a><a href="#plan">How it gets built</a>
  </nav>
</header>

<section id="found" class="stack">
  <h2>What we found on your desktop</h2>
  <ul class="prose">
    <li><b>PDFs open in Chrome</b>, though Master PDF Editor, Zathura and Okular are installed: nobody chose, Chrome just won.</li>
    <li><b>Pictures are split:</b> PNG and JPEG in Pinta, GIF and WebP in Chrome.</li>
    <li><b>Three old choices point to apps that are gone:</b> Typora (Markdown), Nemo (folders), Brave (links). The system quietly skips them.</li>
    <li><b>Archives open in Ark</b> and shell scripts in <b>Konsole</b>: both KDE apps, which leave when KDE does.</li>
    <li>Music and video go to mpv; VLC is installed too.</li>
  </ul>
</section>

<section id="questions" class="stack">
  <div class="decide">
    <h3>Already decided · Javier, 9 October</h3>
    <p>Next after nightForge, and its name: <em>"defaultappsForge"</em>.</p>
  </div>
  <h2>Questions for you</h2>
  <p class="prose">Each with my recommendation in bold. Say "go" and they're all answered that way.</p>
  <ol class="prose">
    <li><b>Ten kinds</b> on the first page: Web browser · Email · Files &amp; folders · Text &amp; code · PDF · Pictures · Music · Video · Documents &amp; sheets · Archives. <span class="rec">Recommended: these.</span> Anything to add (a terminal, a calendar)?</li>
    <li><b>A kind sets all its file types:</b> choosing Pinta for Pictures sets PNG, JPEG, GIF, WebP, SVG… each one Pinta can open; the rest stay as they are. <span class="rec">Recommended: yes.</span></li>
    <li><b>Old choices for apps that are gone are tidied away on save</b>, shown in the review first. <span class="rec">Recommended: yes.</span></li>
    <li><b>KDE apps are flagged</b> ("leaves with KDE"), never changed by themselves: you pick their replacements. <span class="rec">Recommended: yes.</span></li>
    <li><b>Change</b> is a pop-up listing only the apps that can open that kind, the current one marked. Save is a pop-up review, like nightForge (D-2 there). <span class="rec">Recommended: yes.</span></li>
    <li><b>File Types</b> page for the rare one-off (every type the system knows, 1,129 here), with Find and a status filter, headings that sort. <span class="rec">Recommended: yes.</span></li>
    <li><b>The file:</b> <code>~/.config/mimeapps.list</code>, the standard one every desktop and app reads; a backup before every save. <span class="rec">Recommended: yes.</span></li>
    <li><b>Inside hypeForge Settings</b> as a <b>Default apps</b> page, plus a card on the Home page (browser · files · text). <span class="rec">Recommended: yes.</span></li>
    <li><b>Version:</b> 0.1.0 while it's built, 1.0.0 after your run, the AUR after your install test. <span class="rec">Recommended: yes.</span></li>
  </ol>
</section>

<section id="kinds">
  <h2>1 · Kinds</h2>
  <p class="prose">What needs attention on top, then the ten kinds: the app for each and where that came from. <b>✓ your choice</b> was picked by someone; <b>~ the system's guess</b> means nobody chose and the system took the first app that said it could. A table like every table we make: headings that sort, the status as a column, a filter top right.</p>
  {T("kinds")}
</section>

<section id="pick">
  <h2>Change (a pop-up)</h2>
  <p class="prose">Only the apps that can open that kind, the current one marked, a word where it helps.</p>
  {T("pick")}
</section>

<section id="types">
  <h2>2 · File Types</h2>
  <p class="prose">For the one-off: every file type the system knows, with Find and a status filter. <b>Back to the System's Guess</b> removes a choice.</p>
  {T("types")}
</section>

<section id="save">
  <h2>Saving (a pop-up)</h2>
  <p class="prose">A review of every change, the old choices tidied away included; a backup; then it applies at once: the next file you open uses it.</p>
  {T("save")}
</section>

<section id="runs">
  <h2>Where it runs</h2>
  <ul class="prose">
    <li><b>Distribution:</b> <b>any Linux distribution</b>. Written for KognogOS; needs Python, Textual and forgekit.</li>
    <li><b>Desktop:</b> <b>any desktop, or none</b>. The file it writes is the freedesktop.org standard that Sway, KDE, GNOME and every app read. The first Forge Suite app that isn't tied to hypeForge.</li>
    <li><b>Terminal:</b> any terminal, and a <b>plain text console</b> too.</li>
  </ul>
</section>

<section id="plan">
  <h2>How it gets built</h2>
  <ol class="prose">
    <li><b>Your answers</b>, and any change to the drawings.</li>
    <li><b>defaultappsForge on forgekit</b>, in <code>defaultappsforge/</code>: reading the apps and what each can open, the kinds, the two pages, the pop-ups, saving.</li>
    <li><b>hypeForge:</b> the Default apps page in Settings and its Home card, a launcher entry, Help.</li>
    <li><b>Tests</b>, each seen failing first, on throwaway copies of the file; pictures of every page.</li>
    <li><b>Your run</b>, a release, and the AUR after your install test.</li>
  </ol>
</section>

</div>
'''

out = _o.path.join(_here, "v0.1.0-screens.html")
open(out, "w").write(open(_o.path.join(_here, "page-head.html")).read() + body)
print("written", out, len(body), "chars")
