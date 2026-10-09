# Schedule

- **By the Sun at Your Place:** two numbers, latitude and longitude. One decimal is plenty (about 10 km). Nothing is looked up online: the sun times are worked out on this computer, and the box shows today's and June's so you can see what the numbers mean. Near the poles, where the sun may not set or rise, use Fixed Times.
- **Fixed Times:** warm from, daylight from (HH:MM), and how many minutes the change takes. The same every day, whatever the season.
- **F10** saves, with a review first, and the night light restarts with it.

## Files

- Settings: `~/.config/nightforge/settings.toml` (a backup before every save in `~/.config/nightforge/backups/`, the last 20 kept).
- The night light's own messages: `~/.local/state/nightforge/wlsunset.log`.
- At login hypeForge runs `nightforge start`: the night light as your settings say, and the tray icon.
