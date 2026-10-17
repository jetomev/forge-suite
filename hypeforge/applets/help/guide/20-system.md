# The system on the bar (CPU, graphics card, temperature, memory, disks)

**What it does:** five small pieces on the bar — the **processor**, the **graphics card**, the
**temperature**, the **memory** and the **system disk** — each an icon and a number. The number turns
**yellow** when it's busy, full or warm, and **red** when it really matters (a processor over 90 %
busy, a disk over 92 % full, a part at its hot mark). The temperature shows the processor's, but turns
red when *anything* inside is hot.

## How to use it

- **Click a piece**: its own pop-up under the bar, in your theme's look. The numbers move while it's
  open, and each graph shows the **last three minutes**.
  - **Processor:** how busy, every thread as a small bar, its speed, temperature, load and how long
    the computer has been on, and the busiest apps right now.
  - **Graphics card:** how busy, its own memory, temperature, power, fan and speed, and the apps
    using it.
  - **Temperature:** every sensor in plain words — the processor, the graphics card, each drive, the
    memory sticks, the board, inside the case — each with a bar up to its own "hot" mark, and every
    fan.
  - **Memory:** in use, cache (memory the computer gives back the moment an app needs it) and free,
    the swap (memory kept on the disk), and the apps holding the most.
  - **Disks:** each disk in plain words (System, Boot, a USB drive by its name) and how much is free.
    **Click one** to open it; **Free up space** opens nogForge.
- **Right click** the processor or memory: **btop**, every program, in the terminal.
- **Esc**, a click outside, or the same piece again closes it; another piece swaps it.

## Good to know

- The graphics card piece hides on a computer without a card it can read (NVIDIA through its
  driver's `nvidia-smi`, AMD on its own).
- The readings come from the system itself: nothing to install, nothing to set up.
