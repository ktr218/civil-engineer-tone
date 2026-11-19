"""가상 제원으로 윤문 전후 수치 대조의 동작과 한계를 검증한다."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/civil-engineer-tone/scripts"
sys.path.insert(0, str(SCRIPTS))
import check_values


class TestValues(unittest.TestCase):
    def test_equivalent_notation_and_reordering(self):
        original = "Q=1,200 m3/day, 지름 400mm 관로, 길이 13km, 335 L/인/일, 2억 원"
        revised = "금회 관로는 D400mm, L=13.0km이다. 2억원, Q=1200㎥/일, 335ℓ/인·일을 적용한다."
        result = check_values.compare(original, revised)
        self.assertFalse(result["needs_review"], result)
        self.assertEqual(result["original_count"], 5)

    def test_changed_value_unit_sign_relation_and_exponent(self):
        cases = [("Q=650㎥/일", "Q=660㎥/일"), ("fck=27MPa", "fck=27kPa"),
                 ("EL. -3.2m", "EL. +3.2m"), ("S≤3%", "S≥3%"),
                 ("허용값 1e-3m", "허용값 1e3m"), ("감액 △20백만원", "증액 +20백만원"),
                 ("연장 100m", "면적 100㎡"), ("정밀값 123456789012345678901234567890m",
                                                "정밀값 123456789012345678901234567891m")]
        for original, revised in cases:
            with self.subTest(original=original):
                result = check_values.compare(original, revised)
                self.assertTrue(result["needs_review"], result)
                self.assertEqual(sum(x["count"] for x in result["removed"]), 1)
                self.assertEqual(sum(x["count"] for x in result["added"]), 1)

    def test_equal_scientific_and_unicode_forms(self):
        cases = [("연장 1e3m", "연장 1000m"), ("허용값 ≤0.30m", "허용값 <=.3m"),
                 ("EL. −3.2m", "EL. -3.20m"), ("면적 12m2", "면적 12㎡"),
                 ("지표 아래 3m", "GL-3m"), ("3 퍼센트 포인트", "3%p")]
        for original, revised in cases:
            with self.subTest(original=original):
                self.assertFalse(check_values.compare(original, revised)["needs_review"])

    def test_missing_repeated_value_is_not_hidden_by_set_comparison(self):
        result = check_values.compare("A관 D400mm\nB관 D400mm", "A관 D400mm")
        self.assertTrue(result["needs_review"])
        self.assertEqual(result["removed"][0]["count"], 1)
        self.assertEqual([x["line"] for x in result["removed"][0]["locations"]], [1, 2])

    def test_added_value(self):
        result = check_values.compare("검토 필요", "용량 500㎥/일 검토 필요")
        self.assertTrue(result["needs_review"])
        self.assertEqual(result["original_count"], 0)
        self.assertEqual(result["revised_count"], 1)

    def test_attached_datum_sign_and_date_day_changes(self):
        for original, revised in [("GL-3m", "GL+3m"), ("EL.-2.1m", "EL.+2.1m"),
                                  ("2026.11.19", "2026.11.20"), ("제3.2.1절", "제3.2.2절")]:
            with self.subTest(original=original):
                self.assertTrue(check_values.compare(original, revised)["needs_review"])

    def test_fenced_examples_are_excluded_but_line_numbers_retained(self):
        result = check_values.compare("~~~\n100m\n~~~\n연장 20m", "~~~\n999m\n~~~\n연장 30m")
        self.assertEqual(result["original_count"], 1)
        self.assertEqual(result["removed"][0]["locations"][0]["line"], 4)

    def test_conversion_is_reviewed_without_guessing(self):
        self.assertTrue(check_values.compare("연장 1km", "연장 1000m")["needs_review"])

    def test_swapped_assignment_is_explicitly_out_of_scope(self):
        result = check_values.compare("A관 100m, B관 200m", "A관 200m, B관 100m")
        self.assertFalse(result["needs_review"])
        self.assertIn("다른 시설·항목", result["scope"])

    def test_cli_exit_codes_json_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            original, revised = Path(tmp) / "원문.md", Path(tmp) / "윤문.md"
            original.write_text("용량 650㎥/일", encoding="utf-8-sig")
            revised.write_text("용량 660㎥/일", encoding="utf-8")
            saved = [p.read_bytes() for p in (original, revised)]
            args = [sys.executable, str(SCRIPTS / "check_values.py"), str(original), str(revised), "--json"]
            result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertTrue(json.loads(result.stdout)["needs_review"])
            self.assertEqual(saved, [p.read_bytes() for p in (original, revised)])
            args[3] = str(original)
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
            args[3] = str(Path(tmp) / "missing.md")
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
