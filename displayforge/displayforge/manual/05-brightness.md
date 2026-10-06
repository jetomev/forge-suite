# Brightness

One row per screen, and **All screens** at the bottom. Pick a step — 10 to 100 % — and it changes **at once**. The screens keep their brightness themselves, so there is nothing to save.

displayForge talks to the screens through their own control channel (DDC/CI), the same way the screen's buttons do. If a screen doesn't answer, look in **its own menu** for a setting called **DDC/CI** and switch it on.

When your screens are the same model, the computer can't tell which control belongs to which screen. Until **Identify** has asked you once, only **All screens** works.
