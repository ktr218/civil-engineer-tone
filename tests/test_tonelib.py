"""tonelib·검사기·교정기 회귀 테스트. 실행: python -m unittest discover -s tests"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "water-engineer-tone", "scripts")
FIX = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, SCRIPTS)
import tonelib  # noqa: E402

GRADES = "ABCD"


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class TestLexicon(unittest.TestCase):
    def test_lexicon_loads_and_ids_unique(self):
        lex = tonelib.load_lexicon()
        ids = [e["id"] for e in lex["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        for e in lex["entries"]:
            self.assertIn(e["severity"], ("S1", "S2", "S3"))
            if e["auto"]:
                self.assertTrue(e["replace"], e["id"])
            for t in e["types"]:
                self.assertIn(t, tonelib.TYPES)

    def test_auto_rules_are_idempotent(self):
        samples = ["650 m3/day", "지름 400mm 관", "2억 원", "335 L/인/일", "3 퍼센트", "12 km2", "3개 곳", "1,200 CMD"]
        for s in samples:
            once, _ = tonelib.fix(s)
            twice, ch = tonelib.fix(once)
            self.assertEqual(once, twice, s)
            self.assertEqual(ch, [], s)

    def test_correct_notation_is_not_flagged(self):
        ok = "Q=650㎥/일, D400mm, L=3.4km, 335ℓ/인·일, 13개소, 상수도관망, 상하수도관 보호공, 60mm/hr"
        found = [f["id"] for f in tonelib.check(ok, "B") if f["id"].startswith(("U-", "T-"))]
        self.assertEqual(found, [])


class TestFix(unittest.TestCase):
    def test_fix_values(self):
        new, ch = tonelib.fix("처리용량 650 m3/day, 지름 400mm 관로, 2억 원 감소, 335 L/인/일")
        self.assertIn("650㎥/일", new)
        self.assertIn("D400mm", new)
        self.assertIn("2억원", new)
        self.assertIn("335ℓ/인·일", new)
        self.assertEqual(len(ch), 4)

    def test_fix_keeps_numbers(self):
        src = read("BAD_ai.md")
        new, _ = tonelib.fix(src)
        nums = re.compile(r"(?<![mM\d,.])\d[\d,.]*")  # m3·km2의 지수는 제외
        self.assertEqual(nums.findall(src), nums.findall(new))

    def test_fix_skips_code_blocks(self):
        src = "```\n650 m3/day\n```\n650 m3/day\n"
        new, ch = tonelib.fix(src)
        self.assertIn("```\n650 m3/day\n```", new)
        self.assertEqual(len(ch), 1)


class TestDetectAndGrade(unittest.TestCase):
    def test_fixtures(self):
        with open(os.path.join(FIX, "expected.json"), encoding="utf-8") as f:
            exp = json.load(f)
        for name, e in exp.items():
            text = read(name)
            detected, _ = tonelib.detect_type(text)
            if e.get("type"):
                self.assertEqual(detected, e["type"], name)
            doc_type = e.get("check_as") or e["type"]
            sc = tonelib.score(tonelib.check(text, doc_type), text)
            if "max_grade" in e:
                self.assertLessEqual(GRADES.index(sc["grade"]), GRADES.index(e["max_grade"]), f"{name} {sc}")
            if "min_grade" in e:
                self.assertGreaterEqual(GRADES.index(sc["grade"]), GRADES.index(e["min_grade"]), f"{name} {sc}")

    def test_polite_in_report_is_s1(self):
        fs = tonelib.check("대상지역의 계획인구를 검토하였습니다.", "R")
        self.assertTrue(any(f["id"] == "END" and f["severity"] == "S1" for f in fs))

    def test_closing_formula_allowed(self):
        fs = tonelib.check("상기와 같이 검토의견을 제출합니다.", "C")
        self.assertFalse(any(f["id"] == "END" for f in fs))

    def test_eum_in_script_is_flagged(self):
        fs = tonelib.check("○ 사업추진이 시급한 실정임", "P")
        self.assertTrue(any(f["id"] == "END" and f["severity"] == "S2" for f in fs))

    def test_standard_spec_terms_not_flagged(self):
        txt = "땅파기 지보계획서, 발주기관과 협의, 맨홀뚜껑 교체, 노후 수도관 교체, 철근 지름 16mm"
        self.assertEqual([f["id"] for f in tonelib.check(txt, "S")], [])


class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8", env=env)

    def test_check_exit_codes(self):
        bad = self.run_cli(os.path.join(SCRIPTS, "check_tone.py"), os.path.join(FIX, "BAD_ai.md"), "--type", "R")
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        good = self.run_cli(os.path.join(SCRIPTS, "check_tone.py"), os.path.join(FIX, "R_report.md"))
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertIn("등급 A", good.stdout)

    def test_check_json(self):
        r = self.run_cli(os.path.join(SCRIPTS, "check_tone.py"), os.path.join(FIX, "C_review.md"), "--json")
        data = json.loads(r.stdout)
        self.assertEqual(data["type"], "C")

    def test_fix_dry_run(self):
        r = self.run_cli(os.path.join(SCRIPTS, "fix_notation.py"), os.path.join(FIX, "BAD_ai.md"))
        self.assertEqual(r.returncode, 0)
        self.assertIn("변경 2건", r.stdout)



class TestPortablePrompt(unittest.TestCase):
    def test_gemini_md_matches_universal_prompt(self):
        with open(os.path.join(ROOT, "prompts", "universal.md"), encoding="utf-8") as f:
            universal = f.read()
        with open(os.path.join(ROOT, "GEMINI.md"), encoding="utf-8") as f:
            gemini = f.read()
        self.assertEqual(universal, gemini, "GEMINI.md는 prompts/universal.md 사본이어야 함")

    def test_universal_prompt_fits_gpt_limit(self):
        with open(os.path.join(ROOT, "prompts", "universal.md"), encoding="utf-8") as f:
            self.assertLessEqual(len(f.read()), 8000)

    def test_gemini_extension_manifest(self):
        with open(os.path.join(ROOT, "gemini-extension.json"), encoding="utf-8") as f:
            m = json.load(f)
        self.assertEqual(m["contextFileName"], "GEMINI.md")


if __name__ == "__main__":
    unittest.main()
