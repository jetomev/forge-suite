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
  <div class="eyebrow">defaultappsForge · design proposal · 9 October 2026 · second draft</div>
  <h1>defaultappsForge, screen by screen</h1>
  <p class="lede prose">Which app opens what: links, folders, text, PDFs, pictures, music, video, documents, archives. In the terminal, like every Forge app, and a page of hypeForge Settings.</p>
  <p class="prose">Today the only way to choose on the Sway desktop is KDE's page (it leaves with KDE) or a terminal command (issue #19). The drawings show <b>your</b> desktop as it really is right now, read from <code>~/.config/mimeapps.list</code> and from what the system answers for each kind of file. Every drawing is exactly <b>100 columns</b> wide.</p>
  <nav class="toc" aria-label="Contents">
    <a href="#questions">Questions</a><a href="#found">What we found</a><a href="#defaults">Default Apps</a><a href="#dropdown">A drop-down</a><a href="#types">File Types</a><a href="#save">Save</a><a href="#runs">Where it runs</a><a href="#plan">How it gets built</a>
  </nav>
</header>

<section id="questions" class="stack">
  <div class="decide">
    <h3>Your first review · Javier, 9 October</h3>
    <ol>
      <li><b>Kinds → Default Apps</b>, your thirteen: Web Browser · Email Client · Calendar · Phone Numbers · Image Viewer · Music Player · Video Player · Text Editor · PDF Viewer · File Manager · Terminal Emulator · Archive Manager · Map. <b>A drop-down next to each</b> with the apps that can do it. <em>"No need for status, it is kind of overkill."</em></li>
      <li><b>File Types, simpler:</b> the most common types only, assigned to <b>your default apps</b> (not to single apps), <b>like workspaceForge's Apps page</b>: file types on the left, the default apps on the right each with its own types, <b>&gt;&gt;</b> to assign, <b>&lt;&lt;</b> to clear.</li>
    </ol>
  </div>
  <h2>Questions for you</h2>
  <p class="prose">Each with my recommendation in bold. Say "go" and they're all answered that way.</p>
  <ol class="prose">
    <li><b>Documents and spreadsheets</b> (.docx, .xlsx, .odt…) have no default app in your list. <span class="rec">Recommended: add "Office Suite"</span> (ONLYOFFICE today), or leave them on the left, opening where the system guesses.</li>
    <li><b>Terminal Emulator</b> has its own standard, <code>xdg-terminal-exec</code> (in Arch's official repository, small, not installed here). Choosing a terminal installs it through nog and writes its list. <span class="rec">Recommended: yes</span>; hypeForge's Win + Enter follows the same choice.</li>
    <li><b>Phone Numbers:</b> nothing that really handles them is installed (only a KDE leftover). The drop-down says "none installed" until something is. <span class="rec">Recommended: keep the row, as you listed it.</span></li>
    <li><b>Old choices for apps that are gone</b> (Typora, Nemo, Brave on your desktop) are tidied away on save, shown in the review. <span class="rec">Recommended: yes.</span></li>
    <li><b>Each default app starts with its usual file types</b> on the right (Image Viewer: PNG, JPEG, GIF, WebP, SVG…; Text Editor: .txt, .md, .json, .py…); the rest wait on the left. <span class="rec">Recommended: yes.</span></li>
    <li><b>Save</b> is a pop-up review, like nightForge. <span class="rec">Recommended: yes.</span></li>
    <li><b>The file:</b> <code>~/.config/mimeapps.list</code>, the standard one every desktop and app reads; a backup first. <span class="rec">Recommended: yes.</span></li>
    <li><b>Inside hypeForge Settings</b> as <b>Default apps</b>, plus a Home card (browser · files · text). <span class="rec">Recommended: yes.</span></li>
    <li><b>Version:</b> 0.1.0 while it's built, 1.0.0 after your run, the AUR after your install test. <span class="rec">Recommended: yes.</span></li>
  </ol>
</section>

<section id="found" class="stack">
  <h2>What we found on your desktop</h2>
  <ul class="prose">
    <li><b>PDFs open in Chrome</b>, though Master PDF Editor, Zathura and Okular are installed: nobody chose, Chrome just won.</li>
    <li><b>Pictures are split:</b> PNG and JPEG in Pinta, GIF and WebP in Chrome. Assigning them all to Image Viewer fixes it.</li>
    <li><b>Three old choices point to apps that are gone:</b> Typora, Nemo, Brave.</li>
    <li><b>Archives open in Ark</b>, a KDE app that leaves with KDE.</li>
  </ul>
</section>

<section id="defaults">
  <h2>1 · Default Apps</h2>
  <p class="prose">Your thirteen, each with its drop-down. The values are what your desktop uses today.</p>
  {T("defaults")}
</section>

<section id="dropdown">
  <h2>A drop-down, open</h2>
  <p class="prose">Only the apps that can do that job; ● the current one.</p>
  {T("dropdown")}
</section>

<section id="types">
  <h2>2 · File Types</h2>
  <p class="prose">Like workspaceForge's Apps page: the common file types on no default app on the left, your default apps on the right (one open at a time) each with its types, <b>&gt;&gt;</b> assigns the ticked ones to the open default app, <b>&lt;&lt;</b> clears them. In the drawing, <b>.ics</b> (a calendar invite) is about to go to Calendar.</p>
  {T("types")}
</section>

<section id="save">
  <h2>Saving (a pop-up)</h2>
  <p class="prose">A review of every change, the old choices tidied away included; a backup; then at once: the next file or link you open uses it.</p>
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
    <li><b>defaultappsForge on forgekit</b>, in <code>defaultappsforge/</code>: reading the apps and what each can open, the default apps, the two pages, saving.</li>
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
