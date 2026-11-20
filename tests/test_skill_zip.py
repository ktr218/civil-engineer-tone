"""docs/civil-engineer-tone-skill.zip이 스킬 폴더와 같은지 확인. 다르면 python tools/build_skill_zip.py로 다시 만든다."""
import os
import sys
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_skill_zip  # noqa: E402


class TestSkillZip(unittest.TestCase):
    def test_zip_matches_skill_folder(self):
        with zipfile.ZipFile(build_skill_zip.OUT) as z:
            names = sorted(z.namelist())
            expected = sorted(arc for _, arc in build_skill_zip.skill_files())
            self.assertEqual(names, expected, "python tools/build_skill_zip.py 로 zip을 다시 만드세요")
            for p, arc in build_skill_zip.skill_files():
                with open(p, "rb") as f:
                    self.assertEqual(z.read(arc), f.read(), arc + " 내용이 다름: python tools/build_skill_zip.py")
        self.assertIn("civil-engineer-tone/SKILL.md", names)


if __name__ == "__main__":
    unittest.main()
