"""tonelib·검사기·교정기 회귀 테스트. 실행: python -m unittest discover -s tests"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "civil-engineer-tone", "scripts")
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
    def test_fences_do_not_affect_findings_detection_or_grade(self):
        prose = read("R_report.md")
        code = ("650 m3/day\n혁신적인 프로젝트입니다.\n"
                "수신\n제목\n붙임 1\n끝.\n것으로 판단된다\n") * 30
        expected_findings = tonelib.check(prose, "R")
        expected_type = tonelib.detect_type(prose)
        expected_score = tonelib.score(expected_findings, prose)
        for opening, closing in [("```python", "```"), ("~~~text", "~~~"),
                                 ("````", "`````"), ("   ~~~~", "   ~~~~")]:
            with self.subTest(opening=opening):
                text = prose + "\n" + opening + "\n" + code + closing + "\n"
                self.assertEqual(tonelib.check(text, "R"), expected_findings)
                self.assertEqual(tonelib.detect_type(text), expected_type)
                self.assertEqual(tonelib.score(expected_findings, text), expected_score)

    def test_fence_requires_matching_character_length_and_empty_suffix(self):
        text = "````text\n650 m3/day\n```\n~~~\n```` not-a-close\n650 m3/day\n````\n650 m3/day\n"
        fixed, changes = tonelib.fix(text)
        self.assertEqual(fixed, text.rsplit("650 m3/day", 1)[0] + "650㎥/일\n")
        self.assertEqual([c["line"] for c in changes], [8])
        self.assertEqual([f["line"] for f in tonelib.check(text, "B")], [8])

    def test_unclosed_fence_preserves_remaining_text(self):
        text = "~~~\n650 m3/day\n사업을 검토하였습니다.\n"
        self.assertEqual(tonelib.fix(text), (text, []))
        self.assertEqual(tonelib.check(text, "R"), [])

    def test_fence_roundtrip_preserves_crlf(self):
        code = "~~~\r\n650 m3/day\r\n~~~\r\n"
        self.assertEqual(tonelib.fix(code + "650 m3/day\r\n")[0], code + "650㎥/일\r\n")

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

    def test_other_division_terms_not_flagged(self):
        # 건축·설비 시방의 옥상물탱크, 지장물 나열의 상·하수도관
        txt = ("옥상물탱크 등 시설물이 노출되지 않는 구조로 한다\n"
               "물탱크 기초 구조계산\n"
               "통신, 전력, 상·하수도관, 가스관 등 지하매설물")
        self.assertEqual([f["id"] for f in tonelib.check(txt, "S")], [])
        ids = [f["id"] for f in tonelib.check("배수지 대신 물탱크를 설치한다", "R")]
        self.assertIn("T-01", ids)

    def test_ai_chat_addons_and_emoji_flagged(self):
        self.assertIn("K-14", [f["id"] for f in tonelib.check("필요하시면 말씀해 주세요.", "R")])
        self.assertIn("K-08", [f["id"] for f in tonelib.check("검토결과 🚀 유리한 것으로 판단된다.", "R")])
        # 실무 기호(□ ○ ※ ► ∘ ☞)는 이모지로 보지 않는다
        self.assertEqual([f["id"] for f in tonelib.check("□ 개요 ○ 현황 ※ 주) ► ∘ ☞", "B")], [])


class TestDataMapFindings(unittest.TestCase):
    """2026-11 자료지도 재검증(새 문서 388건)에서 찾은 오탐의 회귀 시험."""

    def ids(self, text, doc_type="R"):
        return [f["id"] for f in tonelib.check(text, doc_type)]

    def test_spaced_letter_headers_detect_as_letter(self):
        text = ("수   신 : ㈜○○엔지니어링 대표이사\n"
                "제   목 : 구조계산서에 대한 검토 요청\n"
                "1. 귀 사의 무궁한 발전을 기원합니다.\n"
                "2. 시공사가 제출한 기둥규격 변경 구조계산서를 붙임과 같이 송부하오니 검토하여 주시기 바랍니다.\n"
                "∘ 기둥 단면 변경에 따른 응력 검토 필요\n"
                "∘ 기초 지지력 재검토 필요\n"
                "∘ 변경 도면 반영 여부 확인 필요\n"
                "붙임 : 1. 기술검토요청서 1부.\n"
                "시  행 : ○○-○○호 (2026. 11. 20.)   접수 :\n"
                "전화 /전송 ○○○-○○○-○○○○ / ○○○-○○○-○○○○\n")
        detected, _ = tonelib.detect_type(text)
        self.assertEqual(detected, "G")
        self.assertEqual(tonelib.score(tonelib.check(text, detected), text)["grade"], "A")

    def test_legal_form_phrases_not_flagged(self):
        for line in ["관련 기준을 다음과 같이 고시합니다.", "제출한 증빙자료가 원본과 같음을 확약합니다.",
                     "참여인원의 신원에 이상이 없음을 보증합니다."]:
            self.assertNotIn("END", self.ids(line), line)
        self.assertIn("END", self.ids("대상지역의 계획인구를 검토하였습니다."))

    def test_bold_rule_skips_masking_exponent_and_program_header(self):
        for text in ["○○구 ○○로1**번길**, 1**동 2***호", "V=0.849×C×R**0.63×I**0.54", "[ **좌안배수분구1** ]"]:
            self.assertNotIn("K-08", self.ids(text, "B"), text)
        for text in ["이번 사업의 **핵심**은 관로 교체다", "**목표**: 침수 해소", "처리용량은 **650㎥/일**로"]:
            self.assertIn("K-08", self.ids(text, "B"), text)

    def test_loanword_rule_skips_company_and_product_type(self):
        self.assertNotIn("K-11", self.ids("㈜○○솔루션 폐기물처리시설"))
        self.assertNotIn("K-11", self.ids("임팩트식 스프링클러 반경 35m"))
        self.assertIn("K-11", self.ids("최적의 솔루션을 제공한다"))

    def test_ppm_only_in_water_quality_context(self):
        self.assertIn("U-17", self.ids("방류수 BOD 10ppm 이하"))
        self.assertNotIn("U-17", self.ids("오존 균열시험 50±5ppm"))
        self.assertNotIn("U-17", self.ids("CO 농도 9ppm"))


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
