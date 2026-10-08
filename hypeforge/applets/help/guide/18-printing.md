# Printing

**What it does:** printing works on the Sway desktop the same way it did on Plasma: the printing
service (CUPS) runs in the background, and the printers it knows are offered by every app's
Print dialog.

## The printer on the bar

The printer icon sits with the indicators at the right. **Grey** means idle; **lit, with a
number**, means something is printing or waiting (the number is the count of jobs); **red**
means a printer is stopped. **Click** it for the list of waiting jobs (pick one to cancel it),
**right click** opens Print Settings.

## Setting up a printer

**Print Settings** (the launcher → Settings section, or `system-config-printer`) adds, removes
and configures printers. When it needs admin rights, **sudoForge's box** asks for your password.
Most network printers are found by themselves and need no driver ("driverless", IPP).

## From a terminal

- `lpstat -p -d` — the printers and the default one
- `lp -d <printer> <file>` — print a file (`lp -d HP_M15w notes.pdf`)
- `lpstat -o` — what is waiting to print; `cancel -a` — clear the queue
- `lpstat -v` — each printer's address (run it after any change, to see it took)

## Coming

**printerForge** (Javier's name, 2026-10-07) in hypeForge Settings (step 19 of the order): the same list, add and
remove, a test page, and the queue — in the forgekit look, no GTK window.
