# Default Apps

Web Browser · Email Client · Calendar · Phone Numbers · Image Viewer · Music Player · Video Player · Text Editor · PDF Viewer · File Manager · Terminal Emulator · Archive Manager · Map · Office Suite.

- **Tab** moves between the drop-downs; **Enter** opens one; **↑ ↓** and **Enter** pick.
- A drop-down lists the apps whose own launcher entry says they can do that job, plus whatever does it today. Two apps with the same name show their launcher name too (for example two "Google Chrome" entries).
- **— none installed —** means no app on this computer can do it yet (Phone Numbers, often).
- **Terminal Emulator** uses the `xdg-terminal-exec` standard. If it isn't installed, saving installs it (nog asks for your password) and writes your choice to `~/.config/xdg-terminals.list`. On hypeForge, **Win + Enter** then opens that terminal.

## Web apps

Some jobs can be done by a website, so the lists offer them too, marked **· web app**:

- **Email Client:** Gmail, Outlook. An email link opens a new message there.
- **Calendar:** Google Calendar, Outlook Calendar. A calendar invite opens it, and a click on a day in the desktop's calendar opens that day.
- **Map:** Google Maps, OpenStreetMap. An address opens there.
- **Phone Numbers:** Google Voice. A number opens a call there.

Pick one and save: a small launcher is made (it also shows in your apps), and it opens in its own window of your browser (Chrome, Chromium, Brave, Edge or Vivaldi), or a tab of any other browser. A web app takes links only, never files: an email file (.eml) keeps opening in an email app.

YouTube Music and Google Docs are web apps too, but they can't open a file on your computer, so they're never anyone's default: a double-click on a song or a document would only open the website. They go in the App Library instead, with one command (`--remove` takes them out again):

```
webapp-open --add youtube-music google-docs
```

## Any app… and Find more…

Every list ends with two more lines:

- **Any app…** opens every installed app in a list you can type to filter, for the times an app can do the job but doesn't say so (a picture editor as your image viewer, say).
- **Find more…** opens nogForge already searching for that kind of app (email, music player, PDF…), to install another one.

