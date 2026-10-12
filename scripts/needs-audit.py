#!/usr/bin/env python3
"""What every Forge Suite app (and nog, mindForge) needs to build and run, measured from the code
(Javier, 2026-10-11: "check all Forge Suite apps for all dependencies needed to build and run them").

For each project: every import (Python), every program the code starts, every library a binary links
(Rust), each mapped to the Arch package that provides it (pacman -Qo); then set beside the AUR
recipe's depends / optdepends / makedepends / checkdepends. Packages of Arch's `base` are left out
(every Arch install has them). A program only looked for (shutil.which, `command -v`) is optional.

    needs-audit.py [project…] [--json FILE]
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

HOME = Path.home() / "Programs"
SUITE = HOME / "forge-suite"
# project → (code folders, AUR recipe folder or None, language)
PROJECTS = {
    "forgekit": ([SUITE / "forgekit/forgekit"], "aur-python-forgekit", "python"),
    "hypeforge": ([SUITE / "hypeforge/applets", SUITE / "hypeforge/scripts"], None, "python"),
    "displayforge": ([SUITE / "displayforge"], "aur-displayforge", "python"),
    "sudoforge": ([SUITE / "sudoforge"], "aur-sudoforge", "python"),
    "workspaceforge": ([SUITE / "workspaceforge"], "aur-workspaceforge", "python"),
    "nightforge": ([SUITE / "nightforge"], "aur-nightforge", "python"),
    "defaultappsforge": ([SUITE / "defaultappsforge"], None, "python"),
    "themeforge": ([SUITE / "themeforge"], None, "python"),
    "alacrittyforge": ([HOME / "alacrittyforge"], "aur-alacrittyforge", "python"),
    "bitlaforge": ([HOME / "bitlaforge"], "aur-bitlaforge", "python"),
    "nogforge": ([HOME / "nogforge"], "aur-nogforge", "python"),
    "grubforge": ([HOME / "grubforge"], "aur-grubforge", "python"),
    "nog": ([HOME / "nog/src"], "aur-nog", "rust"),
    "mindforge": ([HOME / "mindforge/bin", HOME / "mindforge/scripts", HOME / "mindforge/hooks"], "aur-mindforge", "bash"),
}
SKIP_DIRS = {"tests", "testing", "__pycache__", ".git", "logs", "dist-rc", "target", "build", "docs", "examples"}
DEV_DIRS = {"scripts", "tools"}           # benches, previews, screenshot makers: not in the package's needs


def is_dev(p: Path) -> bool:
    return bool(DEV_DIRS & set(p.parts)) or p.name.startswith(("make-", "bench-")) or \
        p.name.endswith(("-bench.py", "-preview.py", "_probe.py"))
RUN_CALL = re.compile(r"(?:run|Popen|check_output|check_call|call|spawnlp|execvp|execlp|_run|run_cmd|sh)\(\s*\[?\s*[fr]?[\"']([a-z0-9][a-z0-9_.+-]*)[\"' ]")
WHICH = re.compile(r"which\(\s*[\"']([a-z0-9][a-z0-9_.+-]*)[\"']")
LIST_FIRST = re.compile(r"\[\s*[\"']([a-z0-9][a-z0-9_.+-]*)[\"']\s*,")
EXEC_STR = re.compile(r"[\"'](?:exec |swaymsg exec )([a-z0-9][a-z0-9_.+-]*)")
RUST_CMD = re.compile(r"Command::new\(\s*\"([^\"]+)\"")


@lru_cache(None)
def base_packages() -> set[str]:
    out = subprocess.run(["pacman", "-Si", "base"], capture_output=True, text=True).stdout
    deps = re.search(r"^Depends On\s*:\s*(.+)$", out, re.M)
    names = set(deps.group(1).split()) if deps else set()
    names = {re.split(r"[<>=]", n)[0] for n in names}
    # what those pull in that a recipe never names (and python, which every Python app names itself)
    return names | {"glibc", "gcc-libs", "bash", "coreutils", "systemd-libs", "util-linux-libs", "procps-ng",
                    "findutils", "grep", "sed", "gawk", "tar", "gzip", "util-linux", "shadow", "file", "which"}


@lru_cache(None)
def owner(path: str) -> str | None:
    r = subprocess.run(["pacman", "-Qoq", path], capture_output=True, text=True)
    return r.stdout.split()[0] if r.returncode == 0 and r.stdout.strip() else None


def module_package(mod: str) -> str:
    if mod == "gi":
        import gi
        return owner(gi.__file__) or "?"
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError):
        spec = None
    if spec is None or not spec.origin:
        return "NOT INSTALLED"
    if spec.origin in ("built-in", "frozen"):
        return "python"
    return owner(spec.origin) or "? (not from a package)"


def gi_package(ns: str, ver: str) -> str:
    tl = Path(f"/usr/lib/girepository-1.0/{ns}-{ver}.typelib")
    return owner(str(tl)) or f"NOT INSTALLED ({ns} {ver})"


def program_package(prog: str) -> str:
    p = shutil.which(prog)
    if not p:
        return "NOT INSTALLED"
    return owner(str(Path(p).resolve())) or owner(p) or "? (not from a package)"


def files(folders, exts):
    for f in folders:
        if f.is_file():
            yield f
            continue
        for p in sorted(f.rglob("*")):
            if p.is_file() and not (SKIP_DIRS & set(p.relative_to(f).parts[:-1])) and \
                    (p.suffix in exts or (not p.suffix and exts == {".py"} and p.read_bytes()[:40].startswith(b"#!") and b"python" in p.read_bytes()[:40])
                     or (exts == {".sh"} and not p.suffix and p.read_bytes()[:30].startswith(b"#!") and b"sh" in p.read_bytes()[:30])):
                yield p


def own_modules(folders) -> set[str]:
    names = set()
    for f in folders:
        base = f if f.is_dir() else f.parent
        for p in base.rglob("*.py"):
            names.add(p.stem)
        for p in base.rglob("__init__.py"):
            names.add(p.parent.name)
        names.add(base.name)
    return names


def scan_python(folders):
    mods, gis, progs, optional = {}, {}, {}, set()
    own = own_modules(folders)
    for f in files(folders, {".py"}):
        text = f.read_text(errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.module and not node.level else []
            for n in names:
                top = n.split(".")[0]
                if top in sys.stdlib_module_names or top in own or top == "__future__":
                    continue
                mods.setdefault(top, set()).add(f.name)
        for ns, ver in re.findall(r"require_version\(\s*[\"']([A-Za-z]+)[\"']\s*,\s*[\"']([0-9.]+)[\"']", text):
            gis.setdefault(f"{ns} {ver}", set()).add(f.name)
        for rx in (RUN_CALL, LIST_FIRST, EXEC_STR):
            for prog in rx.findall(text):
                progs.setdefault(prog, set()).add(f.name)
        for prog in WHICH.findall(text):
            progs.setdefault(prog, set()).add(f.name)
            optional.add(prog)
    return mods, gis, progs, optional


def scan_bash(folders):
    progs, optional = {}, set()
    for f in files(folders, {".sh"}):
        text = f.read_text(errors="replace")
        for line in text.splitlines():
            line = line.split("#", 1)[0] if not line.strip().startswith("#!") else ""
            for m in re.finditer(r"(?:^|[;&|(`]|\$\(|\bthen\b|\bdo\b|\belse\b|&&|\|\|)\s*([a-z][a-z0-9_.+-]+)", line):
                w = m.group(1)
                progs.setdefault(w, set()).add(f.name)
            for w in re.findall(r"command -v\s+([a-z][a-z0-9_.+-]+)", line):
                optional.add(w)
    return progs, optional


def scan_rust(folders, binary: Path | None):
    progs, libs = {}, {}
    for f in files(folders, {".rs"}):
        for prog in RUST_CMD.findall(f.read_text(errors="replace")):
            progs.setdefault(prog, set()).add(f.name)
    if binary and binary.exists():
        out = subprocess.run(["ldd", str(binary)], capture_output=True, text=True).stdout
        for lib, path in re.findall(r"^\s*(\S+) => (\S+)", out, re.M):
            libs[lib] = owner(path) or "?"
    return progs, libs


def recipe(name: str | None) -> dict[str, list[str]]:
    if not name or not (HOME / name / "PKGBUILD").exists():
        return {}
    script = ('source PKGBUILD; for a in depends optdepends makedepends checkdepends; do '
              'eval "v=(\\"\\${$a[@]}\\")"; printf "%s\\t" "$a"; printf "%s|" "${v[@]}"; echo; done')
    out = subprocess.run(["bash", "-c", script], cwd=HOME / name, capture_output=True, text=True).stdout
    arrays = {}
    for line in out.splitlines():
        key, _, rest = line.partition("\t")
        arrays[key] = [x for x in rest.split("|") if x]
    return arrays


def bare(dep: str) -> str:
    return re.split(r"[<>=:]", dep)[0].strip()


DEV_FILES: set[str] = set()


def note_dev(folders):
    for f in folders:
        for p in (f.rglob("*") if f.is_dir() else [f]):
            if p.is_file() and is_dev(p):
                DEV_FILES.add(p.name)


def audit(project: str) -> dict:
    folders, aur, lang = PROJECTS[project]
    note_dev(folders)
    report = {"project": project, "aur": aur, "language": lang, "needs": {}, "optional": {}, "unknown": {}, "dev": {}}
    if lang == "python":
        mods, gis, progs, optional = scan_python(folders)
        report["needs"]["python"] = ["the language"]
        for m, fs in mods.items():
            report["needs"].setdefault(module_package(m), []).append(f"module {m} ({', '.join(sorted(fs))})")
        for ns, fs in gis.items():
            report["needs"].setdefault(gi_package(*ns.split()), []).append(f"GI {ns} ({', '.join(sorted(fs))})")
    elif lang == "bash":
        progs, optional = scan_bash(folders)
        report["needs"]["bash"] = ["the language"]
    else:
        progs, libs = scan_rust(folders, HOME / "nog/target/release/nog")
        for lib, pkg in libs.items():
            report["needs"].setdefault(pkg, []).append(f"library {lib}")
        report["build"] = {"rust": ["cargo build"], "cargo": ["cargo build"]}
        optional = set()
    for prog, fs in progs.items():
        pkg = program_package(prog)
        if pkg == "NOT INSTALLED" and not shutil.which(prog):
            if lang == "bash":
                continue            # a bash word that isn't a program (a function, a keyword)
            report["unknown"].setdefault(prog, sorted(fs))
            continue
        where = "optional" if prog in optional else "needs"
        report[where].setdefault(pkg, []).append(f"program {prog} ({', '.join(sorted(fs))})")
    # a package only the benches and screenshot makers use is the developer's, not the package's
    for where in ("needs", "optional"):
        for pkg in list(report[where]):
            whys = report[where][pkg]
            used = {f.strip() for w in whys for f in re.findall(r"\(([^)]*)\)", w)[-1:] for f in f.split(",")}
            if used and used <= DEV_FILES:
                report["dev"].setdefault(pkg, []).extend(whys)
                del report[where][pkg]
    for prog in [p for p in report["unknown"] if set(report["unknown"][p]) <= DEV_FILES]:
        del report["unknown"][prog]
    base = base_packages()
    for where in ("needs", "optional"):
        report[where] = {k: v for k, v in report[where].items() if k not in base or (k, lang) in (("python", "python"), ("bash", "bash"))}
    for k in list(report["optional"]):
        if k in report["needs"]:
            report["needs"][k] += report["optional"].pop(k)
    # what the recipe's check() runs: the tests (their imports and programs), beyond what running needs
    tests = [t for f in folders for t in [(f if f.is_dir() else f.parent) / "tests", (f.parent if f.name in ("src", "bin") else f) / "testing"]
             if t.is_dir()]
    report["check"] = {}
    if tests and lang == "python":
        global SKIP_DIRS
        keep, SKIP_DIRS = SKIP_DIRS, SKIP_DIRS - {"tests", "testing"}
        tmods, tgis, tprogs, _ = scan_python(tests)
        SKIP_DIRS = keep
        for m, fs in tmods.items():
            if m not in own_modules(folders):
                report["check"].setdefault(module_package(m), []).append(f"module {m} ({', '.join(sorted(fs))})")
        for ns, fs in tgis.items():
            report["check"].setdefault(gi_package(*ns.split()), []).append(f"GI {ns} ({', '.join(sorted(fs))})")
        for prog, fs in tprogs.items():
            pkg = program_package(prog)
            if pkg != "NOT INSTALLED":
                report["check"].setdefault(pkg, []).append(f"program {prog} ({', '.join(sorted(fs))})")
        base = base_packages()
        report["check"] = {k: v for k, v in report["check"].items()
                           if k not in report["needs"] and k not in base and k != "python"}
    rec = recipe(aur)
    report["recipe"] = rec
    if rec:
        declared = {bare(d) for d in rec.get("depends", [])}
        opt = {bare(d) for d in rec.get("optdepends", [])}
        report["missing"] = sorted(k for k in report["needs"] if k not in declared and not k.startswith(("?", "NOT")))
        report["missing_optional"] = sorted(k for k in report["optional"] if k not in declared | opt and not k.startswith(("?", "NOT")))
        report["extra"] = sorted(d for d in declared if d not in report["needs"] and d not in report["optional"])
        checks = {bare(d) for d in rec.get("checkdepends", [])} | declared | {bare(d) for d in rec.get("makedepends", [])}
        report["missing_check"] = sorted(k for k in report["check"] if k not in checks and not k.startswith(("?", "NOT")))
    return report


def show(r: dict):
    print(f"\n━━ {r['project']}  ({r['language']}; AUR recipe: {r['aur'] or 'none yet'})")
    for title, key in (("needs", "needs"), ("optional (only looked for)", "optional")):
        if r[key]:
            print(f"  {title}:")
            for pkg, why in sorted(r[key].items()):
                print(f"    {pkg:<26} {'; '.join(why)[:150]}")
    if r.get("check"):
        print(f"  the tests also use: {'; '.join(f'{k} ({chr(44).join(v)[:80]})' for k, v in sorted(r['check'].items()))}")
    if r.get("missing_check"):
        print(f"  MISSING from checkdepends:       {', '.join(r['missing_check'])}")
    if r.get("dev"):
        print(f"  benches / screenshots only: {', '.join(sorted(r['dev']))}")
    if r.get("unknown"):
        print(f"  named in the code, not on this machine: {', '.join(sorted(r['unknown']))}")
    if r.get("recipe"):
        rec = r["recipe"]
        print(f"  recipe depends:      {' '.join(rec.get('depends', [])) or '—'}")
        print(f"  recipe optdepends:   {' '.join(bare(d) for d in rec.get('optdepends', [])) or '—'}")
        print(f"  recipe makedepends:  {' '.join(rec.get('makedepends', [])) or '—'}   checkdepends: {' '.join(rec.get('checkdepends', [])) or '—'}")
        print(f"  MISSING from depends:            {', '.join(r['missing']) or 'none'}")
        print(f"  MISSING (optional) from the recipe: {', '.join(r['missing_optional']) or 'none'}")
        print(f"  in depends, not seen in the code: {', '.join(r['extra']) or 'none'}")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = None
    if "--json" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--json") + 1])
        args = [a for a in args if a != str(out)]
    reports = [audit(p) for p in (args or PROJECTS)]
    for r in reports:
        show(r)
    if out:
        out.write_text(json.dumps(reports, indent=1, default=sorted))
    return 0


if __name__ == "__main__":
    sys.exit(main())
