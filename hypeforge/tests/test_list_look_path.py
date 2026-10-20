"""F-81 (2026-10-20): every pop-up list finds its look through hfmenu.LOOK, which follows
$XDG_CONFIG_HOME — a hidden preview sets it, and its lists must wear the PREVIEWED look, not the live one."""

import importlib
import os
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))


class ListLookPath(unittest.TestCase):
    def test_follows_the_config_folder_in_use(self):
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/tmp/preview-conf"}):
            import hfmenu
            m = importlib.reload(hfmenu)
            self.assertEqual(m.LOOK, "/tmp/preview-conf/sway/fuzzel/fuzzel.ini")
            self.assertEqual(m.config_path("~/.config/sway/fuzzel/fuzzel.ini"), "/tmp/preview-conf/sway/fuzzel/fuzzel.ini")
            self.assertEqual(m.config_path("~/elsewhere.ini"), os.path.expanduser("~/elsewhere.ini"))

    def test_the_real_home_without_it(self):
        env = {k: v for k, v in os.environ.items() if k != "XDG_CONFIG_HOME"}
        with mock.patch.dict(os.environ, env, clear=True):
            import hfmenu
            m = importlib.reload(hfmenu)
        self.assertEqual(m.LOOK, os.path.expanduser("~/.config/sway/fuzzel/fuzzel.ini"))

    def test_no_applet_hard_codes_the_real_home(self):
        bad = []
        for f in (HERE / "applets").rglob("*"):
            if f.is_file() and f.suffix in ("", ".py") and "__pycache__" not in f.parts:
                text = f.read_text(errors="ignore")
                if re.search(r'expanduser\(\s*["\']~/\.config/sway/fuzzel', text):
                    bad.append(str(f.relative_to(HERE)))
        self.assertEqual(bad, [], "use hfmenu.LOOK, so a preview's lists wear the previewed look")


if __name__ == "__main__":
    unittest.main()
