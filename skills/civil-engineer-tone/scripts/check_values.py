#!/usr/bin/env python3
"""윤문 전후 숫자·단위 출현 개수 비교. 내용의 정당성·대상 연결은 판단하지 않는다.

python check_values.py 원문.md 윤문.md [--json]
종료 코드: 0 차이 미검출, 1 대조 필요, 2 입력 오류. 파일은 수정하지 않는다.
"""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys
import unicodedata

import tonelib

# 수치 환산은 하지 않는다. 표기만 동등한 단위와 어휘집의 auto 규칙을 사용한다.
UNITS = (
    "ℓ/인·일", "m³/일", "m³/min", "m³/s", "㎥/일", "㎥/min", "㎥/s",
    "mm/hr", "mm/h", "km/h", "m/s", "mg/L", "㎎/L", "kg/m³", "kN/m²",
    "MWh/년", "Gcal/년", "TOE/년", "백만원", "억원", "천원", "원",
    "km²", "m²", "m³", "㎢", "㎡", "㎥", "km", "mm", "cm", "m",
    "MPa", "kPa", "Pa", "kN", "N", "MW", "kW", "W", "kV", "V",
    "kg", "mg", "㎎", "g", "ℓ", "L", "ha", "ppm", "℃", "°C", "%p", "%",
    "개소", "개", "기", "대", "명", "인", "년", "개월", "월", "일", "시간", "분", "초",
)
UNIT_PATTERN = "|".join(re.escape(u) for u in sorted(UNITS, key=len, reverse=True))
NUMBER = r"(?:\d{1,3}(?:,\d{3})+(?!\d)|\d+)(?:\.\d+)?|\.\d+"
TOKEN = re.compile(
    r"(?<![0-9_])(?P<symbol>D(?:N)?\s*=?\s*|[ΦØφ]\s*|(?:GL|EL|DL)\.?\s*)?"
    r"(?P<relation><=|>=|≤|≥|<|>)?\s*"
    r"(?(symbol)|(?<![A-Za-z0-9_]))"
    r"(?P<number>[+−±△-]?\s*(?:" + NUMBER + r")(?:[eE][+-]?\d+)?)"
    r"(?:\s*(?P<unit>(?:" + UNIT_PATTERN + r")(?![A-Za-z0-9_])))?"
)
SCOPE = (
    "숫자·인식한 단위·부등호의 출현 개수를 비교함. 숫자 순서와 문장 재배치는 허용함. "
    "같은 수치가 다른 시설·항목에 옮겨 붙은 경우, 단위 환산, 표 머리글의 단위, "
    "미지원 단위, 사업명·근거·부정문·계획/완료 변경은 별도 원문 대조가 필요함. "
    "fenced code는 제외하며 문서 번호·날짜도 숫자로 집계함. 차이 미검출은 사실 검증 통과가 아님."
)


def number_key(value):
    value = re.sub(r"\s|,", "", value).replace("−", "-")
    prefix = value[0] if value[0] in "±△" else ""
    if prefix:
        value = value[1:]
    # Decimal.normalize()는 기본 정밀도로 반올림하므로 tuple을 직접 정규화한다.
    sign, digits, exponent = Decimal(value).as_tuple()
    digits = list(digits)
    if not any(digits):
        return prefix + "0"
    while digits[-1] == 0:
        digits.pop()
        exponent += 1
    return f"{prefix}{'-' if sign else ''}{''.join(map(str, digits))}e{exponent}"


def extract(text):
    normalized, _ = tonelib.fix(text)
    rows = []
    for line_no, line in tonelib.content_lines(normalized):
        for match in TOKEN.finditer(line):
            unit = unicodedata.normalize("NFKC", match["unit"] or "")
            relation = {"≤": "<=", "≥": ">="}.get(match["relation"], match["relation"] or "")
            rows.append({"key": (relation, number_key(match["number"]), unit),
                         "line": line_no, "value": match.group().strip(),
                         "context": line[max(0, match.start() - 30):match.end() + 30].strip()})
    return rows


def compare(original, revised):
    before, after = extract(original), extract(revised)
    old_count, new_count = Counter(r["key"] for r in before), Counter(r["key"] for r in after)

    def differences(rows, counts):
        locations = defaultdict(list)
        for row in rows:
            locations[row["key"]].append({k: v for k, v in row.items() if k != "key"})
        return [{"value": locations[key][0]["value"], "count": count,
                 "locations": locations[key]} for key, count in counts.items()]

    removed = differences(before, old_count - new_count)
    added = differences(after, new_count - old_count)
    return {"needs_review": bool(removed or added), "original_count": len(before),
            "revised_count": len(after), "removed": removed, "added": added, "scope": SCOPE}


def main(argv=None):
    parser = argparse.ArgumentParser(description="윤문 전후 수치·단위 대조 (읽기 전용)")
    parser.add_argument("original")
    parser.add_argument("revised")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = compare(Path(args.original).read_text(encoding="utf-8-sig"),
                         Path(args.revised).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, InvalidOperation, ValueError) as error:
        print(f"입력 오류: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("수치·단위 대조 필요" if result["needs_review"] else "수치·단위 차이 미검출")
        for label, key in (("원문에서 감소·누락", "removed"), ("윤문에서 증가·추가", "added")):
            for item in result[key]:
                lines = ", ".join(str(row["line"]) for row in item["locations"])
                print(f"{label}: {item['value']} × {item['count']} (후보 행: {lines})")
        print(SCOPE)
    return 1 if result["needs_review"] else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
