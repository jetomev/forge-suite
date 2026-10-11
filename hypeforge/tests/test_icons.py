"""Finding an app's icon file (hficons), on throwaway folders.

Steam and Lutris put game icons in ~/.local/share/icons/hicolor, a copy of the hicolor theme with
no index.theme of its own. The freedesktop rule: the folder list comes from the first index.theme
found, and every copy of the theme is searched with it (Javier, 2026-10-10: Battle.net and Sim
Companies showed no picture).
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "applets/common"))
from hficons import Icons  # noqa: E402

INDEX = "[Icon Theme]\nName=Hicolor\nDirectories=32x32/apps,128x128/apps,scalable/apps\n"


class IconCopies(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.user, self.system = root / "user/icons", root / "system/icons"
        (self.system / "hicolor").mkdir(parents=True)
        (self.system / "hicolor/index.theme").write_text(INDEX)
        (self.system / "hicolor/scalable/apps").mkdir(parents=True)
        (self.system / "hicolor/scalable/apps/editor.svg").write_text("<svg/>")
        # the user's copy: pictures, no index.theme (what Steam and Lutris leave)
        (self.user / "hicolor/128x128/apps").mkdir(parents=True)
        (self.user / "hicolor/128x128/apps/lutris_battlenet.png").write_bytes(b"png")
        self.icons = Icons(themes=("hicolor",), dirs=[self.user, self.system])

    def tearDown(self):
        self.tmp.cleanup()

    def test_setup_has_no_index_in_the_user_copy(self):
        self.assertFalse((self.user / "hicolor/index.theme").exists())

    def test_a_picture_in_the_copy_without_an_index_is_found(self):
        self.assertEqual(self.icons.find("lutris_battlenet"),
                         str(self.user / "hicolor/128x128/apps/lutris_battlenet.png"))

    def test_the_copy_with_the_index_still_works(self):
        self.assertEqual(self.icons.find("editor"), str(self.system / "hicolor/scalable/apps/editor.svg"))

    def test_no_index_anywhere_finds_nothing(self):
        (self.system / "hicolor/index.theme").unlink()
        self.assertIsNone(Icons(themes=("hicolor",), dirs=[self.user, self.system]).find("lutris_battlenet"))


if __name__ == "__main__":
    unittest.main()
