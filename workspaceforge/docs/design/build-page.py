#!/usr/bin/env python3
"""Writes workspaceForge's design page from build-drawings.py's checked drawings."""
import importlib.util as _u, os as _o
_here = _o.path.dirname(_o.path.abspath(__file__))
_s = _u.spec_from_file_location("build", _o.path.join(_here, "build-drawings.py")); build = _u.module_from_spec(_s); _s.loader.exec_module(build)

S = build.SCREENS
T = lambda k: build.term(S[k])

body = f'''
<div class="wrap">

<header class="stack">
  <div class="eyebrow">workspaceForge · design proposal · 9 October 2026</div>
  <h1>workspaceForge, screen by screen</h1>
  <p class="lede prose">Your workspaces, in the terminal: their names and order, which apps open on each one, and which screens keep the same apps across workspaces. Every screen is drawn here before any code is written.</p>
  <p class="prose">Today all of this lives in a settings file you'd have to edit by hand. workspaceForge is the friendly way in. It follows displayForge on purpose: the same frame, the same menu bar with underlined letters, a list on the left, the picked thing on the right, and a review before every save. Every drawing is exactly <b>100 columns</b> wide. The drawings show <b>your</b> six workspaces, your three screens and the apps on this desktop today.</p>
  <nav class="toc" aria-label="Contents">
    <a href="#questions">Questions</a><a href="#workspaces">Workspaces</a><a href="#delete">Delete</a><a href="#apps">Apps</a><a href="#add">Add an app</a><a href="#sharing">Sharing</a><a href="#save">Save</a><a href="#keys">Keys</a><a href="#plan">How it gets built</a>
  </nav>
</header>

<section id="questions" class="stack">
  <div class="decide">
    <h3>Already decided · Javier, 9 October</h3>
    <ol>
      <li><b>Workspaces only.</b> <em>"Notice I said only workspaces, windows is another Forge app. I like atomized solutions."</em> Where windows go on a screen (the fill order) and which windows float become their own Forge app later.</li>
      <li><b>Apps open on their workspace however you start them</b> (F-50, #55): typed in the launcher, Favorites, the bar, a terminal, or Steam starting a game.</li>
      <li><b>The screens go with the app</b> when it opens on another workspace.</li>
      <li><b>Shared screens need no special rule:</b> their windows already belong to every workspace in the group, and the fill order counts them.</li>
    </ol>
  </div>
  <h2>Questions for you</h2>
  <p class="prose">Each one has my recommendation in bold. Say "go" and they're all answered that way; change any you like.</p>
  <ol class="prose">
    <li><b>Up to nine workspaces</b> (Win + 1 … 9), any names, any order. <span class="rec">Recommended: yes.</span></li>
    <li><b>One app, one workspace.</b> Adding Discord to Gaming takes it off Daily. <span class="rec">Recommended: yes.</span> Two workspaces for one app would need a rule for which one wins.</li>
    <li><b>Deleting a workspace that has windows open:</b> it asks where they go (Daily picked for you). Nothing is ever closed. <span class="rec">Recommended: yes.</span></li>
    <li><b>The lists start from the launcher's groups</b>, once: Internet on Daily (11 apps), Office and Development on Work (15), Multimedia on Entertainment (6), Games on Gaming (7), the monitors on Monitoring (5), Settings on Settings (14); the other 26 open where you are. After that the lists are the only place this is set, and the launcher follows them too. <span class="rec">Recommended: yes.</span> Heads-up: Discord, Dropbox, Insync and the VPN start by themselves at login. They'll go to Daily quietly, without moving your screens.</li>
    <li><b>Saving:</b> <kbd>F10</kbd> shows a review, then it applies <b>at once</b>, no logout. No countdown like displayForge's: nothing here can black out a screen. <span class="rec">Recommended: yes.</span></li>
    <li><b>Who does the work:</b> hypeForge's Workspaces applet, which already runs all the time, moves the windows. workspaceForge only edits its settings file and tells it to re-read. Your workspaces keep working with workspaceForge closed, or even uninstalled. <span class="rec">Recommended: yes.</span></li>
    <li><b>Inside hypeForge Settings:</b> a "Workspaces" page that opens workspaceForge, like Screens opens displayForge. <span class="rec">Recommended: yes.</span></li>
    <li><b>Version:</b> 0.1.0 while it's built; 1.0.0 when this whole design works and you've run it, like displayForge. <span class="rec">Recommended: yes.</span></li>
  </ol>
</section>

<section id="workspaces">
  <h2>1 · Workspaces</h2>
  <p class="prose">Your workspaces down the left, with the Win key that reaches each one; ● marks the one on screen now. On the right, the picked one: its name, how many apps open there, whether it shares a screen, and what's open on it right now. Rename, add, delete and reorder from here. Moving a workspace up or down changes its Win number. At the bottom, the main switch: workspaces that span every screen, or Sway's own way, where each screen switches by itself.</p>
  {T("workspaces")}
</section>

<section id="delete">
  <h2>Deleting a workspace</h2>
  <p class="prose">If windows are open on it, they're moved, never closed. The ones after it move up a number. Its apps go back to "opens where you are" until you place them.</p>
  {T("delete")}
</section>

<section id="apps">
  <h2>2 · Apps</h2>
  <p class="prose">This is F-50. Pick a workspace and see the apps that open on it, however you start them. The numbers on the left are real: what this desktop's launcher would put on each workspace today. "Where you are" holds the apps with no workspace (GIMP, the calculator, KeePassXC…), which open on whatever is on screen. The switch at the bottom is your answer from this morning: the screens go with the app.</p>
  {T("apps")}
</section>

<section id="add">
  <h2>Adding an app</h2>
  <p class="prose">Type to search every installed app. Each one shows where it opens now, so you can see that adding Discord to Gaming takes it off Daily.</p>
  {T("add")}
</section>

<section id="sharing">
  <h2>3 · Sharing</h2>
  <p class="prose">The grid you set by hand today in <code>[share]</code>: workspaces down, screens across. Linking a cell with the one above makes that screen keep the same apps in both workspaces. The drawing shows an <b>example</b>: the left screen shared by Daily, Work and Entertainment, so your chat or music could sit there while the other two screens change. Today nothing is shared. Screens are named the way displayForge names them (Main, Left, Right).</p>
  {T("sharing")}
</section>

<section id="save">
  <h2>Saving</h2>
  <p class="prose">A review first: every change, before and after. A backup of the file is made, then it's written, and the Workspaces applet re-reads it right away. Open windows don't move; a renamed workspace keeps its windows.</p>
  {T("save")}
</section>

<section id="keys">
  <h2>Keys</h2>
  <p class="prose">The same rules as every Forge app: Ctrl + the underlined letter, or the number in menu order, Help included.</p>
  <div class="tw"><table>
    <tr><th>Keys</th><th>What happens</th></tr>
    <tr><td><kbd>Ctrl+W</kbd> <kbd>Ctrl+A</kbd> <kbd>Ctrl+S</kbd> <kbd>Ctrl+H</kbd> · <kbd>1</kbd>–<kbd>4</kbd></td><td>Workspaces, Apps, Sharing, Help</td></tr>
    <tr><td><kbd>↑</kbd> <kbd>↓</kbd> · <kbd>Tab</kbd></td><td>Pick in the list · move into the page</td></tr>
    <tr><td><kbd>r</kbd> <kbd>n</kbd> <kbd>d</kbd> <kbd>+</kbd> <kbd>-</kbd> (Workspaces)</td><td>Rename, new, delete, move up, move down</td></tr>
    <tr><td><kbd>a</kbd> <kbd>m</kbd> <kbd>d</kbd> (Apps)</td><td>Add an app, move it to another workspace, remove it</td></tr>
    <tr><td><kbd>Space</kbd> <kbd>d</kbd> (Sharing)</td><td>Share with the one above · stop sharing</td></tr>
    <tr><td><kbd>F10</kbd></td><td>Save, with the review first</td></tr>
    <tr><td><kbd>Esc</kbd></td><td>Back · close a question</td></tr>
    <tr><td><kbd>F1</kbd> · <kbd>Q</kbd></td><td>Help · Quit (it asks first if something isn't saved)</td></tr>
  </table></div>
</section>

<section id="plan">
  <h2>How it gets built</h2>
  <ol class="prose">
    <li><b>Your answers</b> to the questions above, and any change to the drawings.</li>
    <li><b>The engine first (F-50):</b> the Workspaces applet learns the app lists and moves new windows to their workspace, screens following. It works with the settings file edited by hand, so you can live with it before the app exists.</li>
    <li><b>workspaceForge on forgekit</b>, as a new section of the Forge Suite (<code>workspaceforge/</code>): Workspaces, Apps, Sharing, the review and save, then its page inside hypeForge Settings.</li>
    <li><b>Tests</b>: one, two and three screens; 100 columns; a plain text console; a broken or missing settings file; each check proven failing first.</li>
    <li><b>Your run</b> with a written test list, then a release on GitHub, and the AUR after your local test.</li>
  </ol>
  <p class="prose">Until then your workspaces keep working exactly as they do now.</p>
</section>

</div>
'''

out = _o.path.join(_here, "v0.1.0-screens.html")
open(out, "w").write(open(_o.path.join(_here, "page-head.html")).read() + body)
print("written", out, len(body), "chars")
