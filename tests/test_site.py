"""랜딩페이지 빌드와 웹 검사기 시험. Node가 없으면 건너뛴다. 실행: python -m unittest discover -s tests"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, os.path.join(ROOT, "skills", "civil-engineer-tone", "scripts"))
import tonelib  # noqa: E402

NODE = shutil.which("node")


def read_raw(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


@unittest.skipUnless(NODE, "node가 없어 웹 검사기 시험을 건너뜀")
class TestSite(unittest.TestCase):
    def test_docs_match_build(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([NODE, os.path.join(ROOT, "site", "build.js"), d], check=True, capture_output=True)
            for name in ("index.html", "tonecheck.js"):
                self.assertEqual(read_raw(os.path.join(d, name)), read_raw(os.path.join(ROOT, "docs", name)),
                                 f"docs/{name}이 site/ 원본과 다름: node site/build.js")

    def test_web_checker_matches_python(self):
        files = sorted(glob.glob(os.path.join(FIX, "**", "*.md"), recursive=True))
        self.assertGreater(len(files), 20)
        r = subprocess.run([NODE, os.path.join(ROOT, "tests", "js_parity.js"), *files],
                           capture_output=True, text=True, encoding="utf-8", check=True)
        for item in json.loads(r.stdout):
            name = os.path.relpath(item["file"], FIX)
            with self.subTest(file=name):
                text = read_raw(item["file"])
                doc_type, _ = tonelib.detect_type(text)
                found = tonelib.check(text, doc_type)
                score = tonelib.score(found, text)
                fixed, changes = tonelib.fix(text)
                self.assertEqual(item["type"], doc_type)
                self.assertEqual(item["findings"], [[f["line"], f["id"], f["severity"], f["match"]] for f in found])
                self.assertEqual(item["grade"], score["grade"])
                self.assertAlmostEqual(item["per500"], score["per_500_chars"], places=1)
                self.assertEqual(item["fixed"], fixed)
                self.assertEqual(item["nchanges"], len(changes))


if __name__ == "__main__":
    unittest.main()
