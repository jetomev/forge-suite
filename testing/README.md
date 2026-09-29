# hypeForge — testing

*Test matrices and their results are published here, like every Forge app. Nothing has been tested yet, because there is nothing to test yet. This page is the plan.*

---

## Where it gets tested

| Machine | Why | Status |
|---|---|---|
| **Omarchy** virtual machine | Study the reference hands-on, and prove that our virtual machines can run Hyprland at all | proposed |
| **KognogOS** virtual machine | The main target: a real KognogOS install | waits on a fully rebuilt KognogOS installer image |
| **Plain Arch** virtual machine | The "any Arch install" promise | planned |
| **The test desktop** | Real hardware: NVIDIA RTX 3060, three 2560×1440 screens at 144 Hz | after the virtual machines pass |

## House rules

1. **Start clean every time.** Every virtual machine has a saved clean state (a *snapshot*). Each test run starts by returning to it, so no run inherits leftovers from the one before.
2. **3D graphics first.** Hyprland will not run without 3D graphics, even inside a virtual machine. On this NVIDIA desktop, getting that working is proven before anything else.
3. **A plain text screen in every matrix.** hypeForge must be readable before any desktop exists ([forgekit#1](https://github.com/jetomev/forgekit/issues/1)). No Forge test matrix included this run until now, which is how the problem went unnoticed in four apps.
4. **Test the installed package, not the source folder.** The final pass installs what users would install.
5. **Findings are numbered** F-1, F-2… Each gets its own issue, titled `F-n: <description>`, with the full result attached. They ship together as one fix batch.

## File names

```
YYYYMMDD - Test Matrix for hypeForge vX-Y-Z.md
YYYYMMDD - Test Results for hypeForge vX-Y-Z.md
```

The version uses hyphens, never dots.
