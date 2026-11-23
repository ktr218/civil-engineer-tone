"""랜딩페이지 빌드와 웹 검사기 시험. Node가 없으면 건너뛴다. 실행: python -m unittest discover -s tests"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures")
sys.path.insert(0, os.path.join(ROOT, "skills", "civil-engineer-tone", "scripts"))
import check_values  # noqa: E402
import tonelib  # noqa: E402

NODE = shutil.which("node")

# 웹 수치 대조와 check_values.py를 맞춰 보는 쌍: test_values.py 사례에 유니코드 숫자·기호·공백 경계를 더함
VALUE_CASES = [
    ("Q=1,200 m3/day, 지름 400mm 관로, 길이 13km, 335 L/인/일, 2억 원",
     "금회 관로는 D400mm, L=13.0km이다. 2억원, Q=1200㎥/일, 335ℓ/인·일을 적용한다."),
    ("Q=650㎥/일", "Q=660㎥/일"), ("fck=27MPa", "fck=27kPa"), ("EL. -3.2m", "EL. +3.2m"), ("S≤3%", "S≥3%"),
    ("허용값 1e-3m", "허용값 1e3m"), ("감액 △20백만원", "증액 +20백만원"), ("연장 100m", "면적 100㎡"),
    ("정밀값 123456789012345678901234567890m", "정밀값 123456789012345678901234567891m"),
    ("연장 1e3m", "연장 1000m"), ("허용값 ≤0.30m", "허용값 <=.3m"), ("EL. −3.2m", "EL. -3.20m"),
    ("면적 12m2", "면적 12㎡"), ("지표 아래 3m", "GL-3m"), ("3 퍼센트 포인트", "3%p"),
    ("A관 D400mm\nB관 D400mm", "A관 D400mm"), ("검토 필요", "용량 500㎥/일 검토 필요"),
    ("GL-3m", "GL+3m"), ("EL.-2.1m", "EL.+2.1m"), ("2026.11.19", "2026.11.20"), ("제3.2.1절", "제3.2.2절"),
    ("~~~\n100m\n~~~\n연장 20m", "~~~\n999m\n~~~\n연장 30m"), ("연장 1km", "연장 1000m"),
    ("A관 100m, B관 200m", "A관 200m, B관 100m"),
    ("연장 " + chr(0xFF11) + chr(0xFF12) + "0m", "연장 120m"),
    ("높이 " + chr(0x1D7D9) + chr(0x1D7DA) + "m", "높이 12m"),
    (chr(0x1F697) * 3 + " 연장 3.4km 공사 " + chr(0x1F6A7), "연장 4.3km"),
    ("Φ300 관, Ø250, φ200", "D300 관, D250, D200"), ("DN 400, D = 300mm", "DN400, D=300mm"),
    ("허용 ≥ 5 mm", "허용 >=5mm"), ("±0.5m", "0.5m"), ("2.5E+3 m", "2500m"), ("0.0m", "0m"),
    ("연장" + chr(0xA0) + "120m", "연장 120m"), ("12,345.67원", "12345.67원"), ("1,20m", "120m"),
    ("> 인용 100m", "100m"), ("| 구분 | 30 m³/s |", "| 구분 | 30㎥/s |"),
]


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

    def test_web_value_compare_matches_python(self):
        texts = [read_raw(f) for f in sorted(glob.glob(os.path.join(FIX, "**", "*.md"), recursive=True))]
        pairs = list(VALUE_CASES)
        for i, text in enumerate(texts):
            bumped = re.sub(r"[0-8]", lambda m: str(int(m.group()) + 1), text, count=5)
            pairs += [(text, tonelib.fix(text)[0]), (text, bumped), (text, texts[(i + 1) % len(texts)])]
        r = subprocess.run([NODE, os.path.join(ROOT, "tests", "js_values.js")], input=json.dumps(pairs, ensure_ascii=False),
                           capture_output=True, text=True, encoding="utf-8", check=True)
        out = json.loads(r.stdout)
        self.assertEqual(out["units"], list(check_values.UNITS))
        self.assertEqual(len(out["results"]), len(pairs))
        for (original, revised), result in zip(pairs, out["results"]):
            with self.subTest(original=original[:40], revised=revised[:40]):
                self.assertEqual(result, check_values.compare(original, revised))


if __name__ == "__main__":
    unittest.main()
