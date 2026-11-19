#!/usr/bin/env python3
"""토목 실무 문체 검사기 (표준 라이브러리만 사용).

사용법:
    python check_tone.py 파일.md                 # 유형 자동 판별
    python check_tone.py 파일.md --type B        # 유형 지정
    python check_tone.py - --type R < 파일       # 표준입력
    python check_tone.py 파일.md --json          # JSON 출력
    python check_tone.py 파일.md --min-grade B   # 등급 미달 시 종료코드 1

유형: R 보고서 / S 설계기준·과업지시서 / B 장표·협의자료·회의록 / C 검토의견 / A 조치결과 / V VE제안 / P 발표 / M 메일 / G 공문
종료 코드: 0 통과, 1 S1 위반 또는 등급 미달, 2 입력 오류
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tonelib  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description="토목 실무 문체 검사기")
    ap.add_argument("path", help="검사할 파일 경로, 표준입력은 -")
    ap.add_argument("--type", choices=list(tonelib.TYPES), help="문서 유형 코드(생략 시 자동 판별)")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    ap.add_argument("--min-grade", choices=list("ABCD"), help="이 등급보다 낮으면 종료코드 1")
    a = ap.parse_args(argv)
    try:
        if a.path == "-":
            text = sys.stdin.read()
        else:
            with open(a.path, encoding="utf-8") as f:
                text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"입력 오류: {e}", file=sys.stderr)
        return 2
    detected, scores = tonelib.detect_type(text)
    doc_type = a.type or detected
    findings = tonelib.check(text, doc_type)
    sc = tonelib.score(findings, text)
    if a.json:
        print(json.dumps({"type": doc_type, "detected": detected, "score": sc, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        src = "지정" if a.type else "자동"
        print(f"[유형 {doc_type}({src})] 등급 {sc['grade']} | 위반 {len(findings)}건 "
              f"(S1 {sc['counts']['S1']}, S2 {sc['counts']['S2']}, S3 {sc['counts']['S3']}) | "
              f"500자당 {sc['per_500_chars']}점")
        if a.type and a.type != detected:
            print(f"  참고: 자동 판별 결과는 {detected}")
        for i, f in enumerate(findings, 1):
            loc = f"{f['line']}행" if f["line"] else "전체"
            sug = " / ".join(f["suggest"][:3])
            fixable = " [자동교정]" if f["auto"] else ""
            print(f"{i:>3}) {f['id']:<6}{f['severity']} {loc:>5} \"{f['match']}\" → {sug}{fixable}")
            if f["message"] and f["message"] != "어휘·표기 정규화":
                print(f"       {f['message']}")
    fail = sc["counts"]["S1"] > 0
    if a.min_grade and "ABCD".index(sc["grade"]) > "ABCD".index(a.min_grade):
        fail = True
    return 1 if fail else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
