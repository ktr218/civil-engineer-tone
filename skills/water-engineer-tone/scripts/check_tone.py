#!/usr/bin/env python3
"""상하수도 실무 문체 정적 검사기 (표준 라이브러리만 사용).

사용법:
    python check_tone.py 파일.md [--type R|S|B|C|A|V|P|M] [--json]
    type 기본값 R. 표준입력도 가능: python check_tone.py - --type B < 파일

종료 코드: 0 = S1 위반 없음, 1 = S1 위반 있음, 2 = 입력 오류
"""
import argparse
import json
import re
import sys

FORMAL_TYPES = set("RSBCAV")  # 경어체를 쓰면 안 되는 유형

# (ID, 심각도, 정규식, 메시지, 적용유형 또는 None=전체)
RULES = [
    # K. AI·일반 문체
    ("K-1", "S1", r"혁신적|획기적|놀라운|탁월한|최첨단|완벽한", "과장 수식어: 삭제하거나 정량 표현으로", None),
    ("K-2", "S1", r"중요한 역할을\s*(합니다|한다)|아무리 강조해도|다양한 측면에서|종합적으로 살펴보면|결론적으로|이를 통해[^.]*수 있(습니다|다)|라고 할 수 있(습니다|다)",
     "AI 관용구: 실무 판단형(~것으로 판단된다)으로", None),
    ("K-3", "S1", r"(입니다|합니다|습니다|해요|세요|이에요)[.\s]*$", "경어체 혼입: 유형에 맞는 종결로", "FORMAL"),
    ("K-4", "S1", r"\*\*[^*]+\*\*|[✅✔👉🚀💡📌⭐🔥]", "마크다운 굵게/이모지: 기호 위계(□ ○ - ·)로", None),
    ("K-5", "S1", r"정말|엄청|꽤|너무|네요|!\s*$", "구어·감탄 표현", "FORMAL"),
    ("K-6", "S2", r"많은 양의|상당한 양|여러 곳|대부분의 지역", "막연한 수량: 수치나 ○○개소로", None),
    ("K-7", "S2", r"솔루션|인사이트|퍼포먼스|프로세스 최적화|임팩트", "외래어 남용: 개선방안/시사점/성능/절차 등으로", None),
    ("K-9", "S2", r"물탱크|하수\s*파이프|수도\s*파이프|물\s*파이프|하수도관(?!로)", "일반어 시설명: 배수지/하수관로/상수관로 등으로", None),
    ("K-10", "S3", r"되어지|개선시키|향상시키|감소시키", "피동·사동 과잉", None),
    # C. 시점어
    ("C-1", "S3", r"(^|\s)이번\s*(사업|과업|용역|계획)", "'이번' → '금회'/'본 사업'", "FORMAL"),
    # G. 단위 표기
    ("G-1", "S2", r"\d\s*(m3|m³|M3)\s*/\s*(day|d|일|DAY)(?![A-Za-z])|\d\s*㎥\s*/\s*(day|d|DAY)(?![A-Za-z])|\d\s*CMD(?![A-Za-z])",
     "유량 단위: ㎥/일 로 표기 (m3/day 등 금지)", None),
    ("G-1", "S2", r"\d\s*(m3|m³)(?!\s*/)", "체적 단위: ㎥ 로 표기", None),
    ("G-1", "S2", r"지름\s*\d+\s*mm|\d+\s*파이(?![가-힣A-Za-z])", "관경: D400mm 형식으로", None),
    ("G-1", "S2", r"\d\s*(km2|m2)(?![A-Za-z0-9])", "면적 단위: ㎢/㎡ 로", None),
    ("G-1", "S3", r"\d\s*(L|리터)\s*/\s*(인|명)\s*/\s*일", "원단위: ℓ/인·일 또는 Lpcd 로", None),
    ("G-2", "S2", r"\d\s*억\s+원|\d\s*백만\s+원|\d\s*천\s+원", "금액 단위는 붙여 씀: 억원/백만원/천원", None),
    ("G-2", "S3", r"\d+\s*퍼센트", "'퍼센트' → %", None),
    ("G-1", "S3", r"\d+\s*%\s*포인트", "'%포인트' → %p", None),
]

POLITE_END = re.compile(r"(입니다|합니다|습니다|십시오|드립니다|됩니다)[.\s]*$")
PLAIN_END = re.compile(r"(한다|하였다|이다|된다|있다|없다|판단된다|나타났다|실정이다)[.\s]*$")


def check(text, doc_type):
    findings = []
    lines = text.splitlines()
    for no, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("```"):
            continue
        for rid, sev, pat, msg, scope in RULES:
            if scope == "FORMAL" and doc_type not in FORMAL_TYPES:
                continue
            m = re.search(pat, s)
            if m:
                findings.append({"line": no, "id": rid, "severity": sev,
                                 "match": m.group(0).strip(), "message": msg,
                                 "text": s[:80]})
    # 종결 혼용 (R/S 문서에서 평서·경어 동시 사용)
    if doc_type in ("R", "S"):
        polite = sum(1 for l in lines if POLITE_END.search(l.strip()))
        plain = sum(1 for l in lines if PLAIN_END.search(l.strip()))
        if polite and plain:
            findings.append({"line": 0, "id": "A-1", "severity": "S1", "match": f"경어 {polite}줄 / 평서 {plain}줄",
                             "message": "종결어미 혼용: 보고서 본문은 평서형(~한다/~하였다)으로 통일", "text": ""})
    # 판단형 과다
    judge = len(re.findall(r"것으로 판단된다", text))
    paras = max(1, len([p for p in re.split(r"\n\s*\n", text) if p.strip()]))
    if judge / paras > 2:
        findings.append({"line": 0, "id": "A-2", "severity": "S2", "match": f"'것으로 판단된다' {judge}회/{paras}문단",
                         "message": "판단 유보형 과다: 사실은 ~나타났다/~이다로 단정", "text": ""})
    # '등' 남용
    for no, line in enumerate(lines, 1):
        if len(re.findall(r"\s등(\s|$|을|이|의|에|으로)", line)) >= 3:
            findings.append({"line": no, "id": "F-3", "severity": "S3", "match": "등 x3+",
                             "message": "'등' 남용: 한 문장 1회", "text": line.strip()[:80]})
    order = {"S1": 0, "S2": 1, "S3": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["line"]))
    return findings


def main():
    ap = argparse.ArgumentParser(description="상하수도 실무 문체 검사기")
    ap.add_argument("path", help="검사할 파일 경로, 표준입력은 -")
    ap.add_argument("--type", default="R", choices=list("RSBCAVPM"), help="문서 유형 코드")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    a = ap.parse_args()
    try:
        if a.path == "-":
            text = sys.stdin.read()
        else:
            with open(a.path, encoding="utf-8") as f:
                text = f.read()
    except OSError as e:
        print(f"입력 오류: {e}", file=sys.stderr)
        return 2
    res = check(text, a.type)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"[유형 {a.type}] 위반 {len(res)}건")
        for i, f in enumerate(res, 1):
            loc = f"{f['line']}행" if f["line"] else "전체"
            print(f"{i}) {f['id']} {f['severity']} {loc} \"{f['match']}\" - {f['message']}")
    return 1 if any(f["severity"] == "S1" for f in res) else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
