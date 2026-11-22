"""토목 실무 문체 공통 라이브러리 (표준 라이브러리만 사용).

- load_lexicon(): references/lexicon.json 로드
- detect_type(text): 문서 유형 추정 (R S B C A V P M)
- classify_ending(line): 줄 종결 유형 분류
- check(text, doc_type): 위반 목록
- score(findings, text): 가중 점수와 등급(A~D)
- fix(text, doc_type): auto=true 어휘집 항목으로 표기 정규화
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON_PATH = os.path.normpath(os.path.join(HERE, "..", "references", "lexicon.json"))

TYPES = "RSBCAVPMG"
WEIGHT = {"S1": 5.0, "S2": 2.0, "S3": 0.5}

# 종결 분류 정규식 (줄 끝 기준, 괄호·첨부 표기 제거 후)
END_PATTERNS = [
    ("polite", re.compile(r"(니다|니까|세요|십시오|어요|아요|에요|해요|죠)$")),
    ("haja", re.compile(r"(하자|줄이자|바꾸자|늘리자|없애자|높이자|낮추자|세우자|만들자|쓰자|두자)$")),
    ("eum", re.compile(r"(임|함|음|됨|있음|없음|바람|바랍|하였음|되었음|예정임|필요함)$")),
    ("plain", re.compile(r"(다)$")),
]
TRAIL = re.compile(r"[\s.。,;:)\]>」』\"'”’]+$|<[^>]*>$|\([^)]*\)$")
BULLET = re.compile(r"^[\s□■○❍◦•∙·‧⦁￭▪►▶※*\-–—\d.)(가-하]{0,4}[.)]?\s*")

# 유형별 허용 종결
ALLOWED = {
    "R": {"plain", "noun"},
    "S": {"plain", "noun", "eum"},
    "B": {"noun", "eum"},
    "C": {"noun", "eum", "polite"},  # 기관 검토의견은 ~하여야 합니다 · ~필요합니다
    "A": {"eum", "noun"},
    "V": {"haja", "noun"},
    "P": {"polite", "noun"},
    "M": {"polite", "noun", "eum"},
    "G": {"polite", "noun", "eum", "plain"},
}
# 유형별 금지 종결 (위반으로 보고)
FORBIDDEN = {
    "R": {"polite", "haja", "eum"},
    "S": {"polite", "haja"},
    "B": {"polite", "haja"},
    "C": {"haja"},
    "A": {"polite", "haja"},
    "V": {"polite"},
    "P": {"eum", "haja"},
    "M": {"haja"},
    "G": {"haja"},
}
# 유형과 무관하게 관용으로 쓰이는 맺음·제출 문구 (종결 규칙 예외)
CLOSING_OK = re.compile(r"상기와\s*같이|위와\s*같이|이상과\s*같이|귀중|제출합니다|보고합니다|"
                        r"감사합니다|바랍니다|드립니다|주시기|하시기|알려드리|작성요령|기재합니다|적습니다|"
                        # 고시문·공고문·서약서·확약서 같은 법정 서식의 정형 문구
                        r"공고합니다|고시합니다|확약합니다|서약합니다|보증합니다|위임합니다|신고합니다|통지합니다")
BULLETS = ("□", "■", "○", "❍", "∘", "◦", "-", "∙", "·", "⋅", "․", "‧", "⦁", "•", "▪")
END_NAME = {"polite": "경어체(~니다)", "plain": "평서형(~다)", "eum": "음슴체(~임/함/음)",
            "haja": "청유형(~하자)", "noun": "명사형"}


def load_lexicon(path=None):
    with open(path or LEXICON_PATH, encoding="utf-8") as f:
        data = json.load(f)
    for e in data["entries"]:
        e["_re"] = re.compile(e["pattern"], re.M)
    return data


def _strip(line):
    s = line.strip()
    prev = None
    while prev != s:
        prev = s
        s = TRAIL.sub("", s).strip()
    return s


def classify_ending(line):
    s = _strip(line)
    if len(s) < 6 or not re.search(r"[가-힣]", s):
        return None
    if s.startswith("|") or s.count("|") >= 2:
        return None  # 표 행
    for name, pat in END_PATTERNS:
        if pat.search(s):
            return name
    if re.search(r"[가-힣]$", s):
        return "noun"
    return None


def marked_lines(text):
    """(행 번호, 원래 줄, fenced code 여부). 닫는 fence도 보호한다."""
    fence = None
    for no, line in enumerate(text.splitlines(keepends=True), 1):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        protected = fence is not None
        if match:
            run, info = match.groups()
            if fence is None:
                if run[0] != "`" or "`" not in info:
                    fence = (run[0], len(run))
                    protected = True
            elif run[0] == fence[0] and len(run) >= fence[1] and not info.strip():
                fence = None
        yield no, line, protected


def content_lines(text):
    for no, line, protected in marked_lines(text):
        if protected:
            continue
        line = line.rstrip("\r\n")
        if line.strip().startswith(">"):
            line = line.strip()[1:]
        yield no, line


def detect_type(text):
    """문서 유형 추정. (코드, 점수 dict) 반환."""
    sc = {t: 0.0 for t in TYPES}
    ends = {}
    lines = [l for _, l in content_lines(text) if l.strip()]
    prose = "\n".join(lines)
    nl = max(1, len(lines))
    bullets = pauses = haja = plain_bul = 0
    for l in lines:
        s = l.strip()
        e = classify_ending(s)
        if e == "haja":
            haja += 1
        if len(s) >= (40 if nl > 60 else 15):  # 긴 문서는 표 셀·제목을 빼고 문장 길이 줄만 통계
            if e:
                ends[e] = ends.get(e, 0) + 1
            if e == "plain" and s.startswith(("○", "❍", "•", "-", "∘", "◦")):
                plain_bul += 1
        if s.startswith(BULLETS):
            bullets += 1
        if "/" in s and re.search(r"니다[.\s]*$", s):
            pauses += 1
    n = sum(ends.values()) or 1
    r = {k: v / n for k, v in ends.items()}
    b = bullets / nl
    sc["B"] += 2.5 * b
    sc["C"] += 1.0 * b
    sc["A"] += 1.0 * b
    sc["P"] += 6 * min(1.0, pauses / nl * 5)
    sc["R"] += 8 * r.get("plain", 0)
    sc["S"] += 6 * r.get("plain", 0)
    sc["B"] += 5 * r.get("noun", 0)
    sc["A"] += 12 * r.get("eum", 0)
    sc["C"] += 2 * r.get("noun", 0) + 3 * r.get("eum", 0)
    sc["V"] += 8 * r.get("haja", 0) + 8 * min(1.0, haja / 5.0)
    sc["S"] += 5 * (plain_bul / max(1, ends.get("plain", 0)))  # 조항식(○ ~한다)
    sc["P"] += 4 * r.get("polite", 0)
    sc["M"] += 3 * r.get("polite", 0)
    sc["G"] += 1.5 * r.get("polite", 0) + 1.0 * r.get("eum", 0)
    kw = {
        "C": r"수정\s*바람|제시\s*필요|하기\s*바람|불일치|상이함|과소산정|과다산정|누락|검토\s*의견|권고|쟁점\s*:|질의\s*\d*\s*:|질의사항|여야\s*합니다|필요합니다|【[^】]*검토[^】]*】|재원협의",
        "A": r"하였음|조치\s*결과|조치\s*계획|반영\s*여부|<첨부|일부반영",
        "S": r"원칙으로\s*한다|에\s*따른다|에\s*의한다|할\s*수\s*있다|하여야\s*한다|기준으로\s*한다",
        "P": r"보고\s*드리|되겠습니다|위원님|감사합니다|사료됩니다",
        "M": r"드립니다|부탁드립니다|공유드|제목\s*:|님,|회신",
        "V": r"제안\s*No|하자$|VE",
        # 공문 머리·꼬리. HWP 공문은 '수   신', '제   목'처럼 글자 사이를 띄워 쓴다
        "G": r"^\s*수\s*신\s*(?:자|[:：]|\s)|\(경유\)|^\s*제\s*목\s*[:：]|끝\.\s*$|^\s*붙\s*임\s*[:：\d]|붙임\s*\d|위\s*호와\s*관련|"
             r"알려드리|^\s*시\s*행\s*[:：]|시행\s*[가-힣]+-\d|접\s*수\s*[:：]|접수\s*번호|전화\s*/?\s*전송|귀하$",
        "B": r"과\s*업\s*명|사\s*업\s*명|추진경위|사업개요|과업기간",
        "R": r"판단된다|나타났다|검토하였다|산정하였다|실정이다|다음과\s*같다",
    }
    for t, p in kw.items():
        hits = len(re.findall(p, prose, re.M))
        sc[t] += 1.5 * min(3.0, hits / max(1.0, nl / 20.0))  # 20줄당 빈도, 상한 3
    best = max(sc, key=sc.get)
    return best, sc


def check(text, doc_type, lexicon=None):
    lex = lexicon or load_lexicon()
    findings = []
    lines = list(content_lines(text))
    prose = "\n".join(line for _, line in lines)
    for no, line in lines:
        s = line.strip()
        if not s:
            continue
        for e in lex["entries"]:
            if e["types"] and doc_type not in e["types"]:
                continue
            m = e["_re"].search(s)
            if m:
                findings.append({
                    "line": no, "id": e["id"], "taxonomy": e["taxonomy"], "severity": e["severity"],
                    "match": m.group(0).strip(), "suggest": e["suggest"], "auto": e["auto"],
                    "message": e["note"] or "어휘·표기 정규화", "text": s[:90]})
        end = classify_ending(s)
        if end and end in FORBIDDEN.get(doc_type, set()) and not CLOSING_OK.search(s):
            if doc_type in "RS" and end == "polite":
                sev = "S1"
            elif (doc_type == "R" and end == "eum") or (doc_type in "CA" and end == "haja"):
                sev = "S3"  # 기술검토서의 음슴체, 의견표 안의 VE 제안문은 실무에도 섞여 쓰임
            else:
                sev = "S2"  # 장표·의견표의 경어(외부 검토자 문장, 발언 인용), 발표 원고의 음슴체 등
            findings.append({
                "line": no, "id": "END", "taxonomy": "A-1", "severity": sev, "match": _strip(s)[-8:],
                "suggest": [END_NAME[x] for x in sorted(ALLOWED[doc_type])], "auto": False,
                "message": f"유형 {doc_type}에 맞지 않는 종결: {END_NAME[end]}", "text": s[:90]})
    # 문서 단위 규칙
    judge = len(re.findall(r"것으로\s*(?:판단된다|판단됨|사료된다)", prose))
    kchars = max(1.0, len(re.sub(r"\s", "", prose)) / 1000.0)
    if doc_type == "R" and judge >= 3 and judge / kchars > 2.0:
        findings.append({"line": 0, "id": "DOC-1", "taxonomy": "A-2", "severity": "S2",
                         "match": f"'것으로 판단된다' 1,000자당 {judge / kchars:.1f}회",
                         "suggest": ["~나타났다", "~이다", "~검토되었다"],
                         "auto": False, "message": "판단 유보형 과다: 사실은 단정형으로", "text": ""})
    for no, line in lines:
        if len(re.findall(r"\s등(?=\s|$|을|이|의|에|으로)", line)) >= 4:
            findings.append({"line": no, "id": "DOC-2", "taxonomy": "F-3", "severity": "S3", "match": "등 x3+",
                             "suggest": ["한 문장 1회"], "auto": False, "message": "'등' 남용", "text": line.strip()[:90]})
    short = 0
    for no, line in lines:
        e = classify_ending(line)
        if doc_type == "R" and e == "plain" and len(line.strip()) < 18:
            short += 1
            if short == 3:
                findings.append({"line": no, "id": "DOC-3", "taxonomy": "J-1", "severity": "S3", "match": "짧은 문장 3연속",
                                 "suggest": ["문장 결합"], "auto": False,
                                 "message": "보고서 본문은 60~120자 문장이 일반적", "text": ""})
        else:
            short = 0
    order = {"S1": 0, "S2": 1, "S3": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["line"]))
    return findings


def score(findings, text):
    prose = "\n".join(line for _, line in content_lines(text))
    chars = len(re.sub(r"\s", "", prose))
    units = max(1.0, chars / 500.0)
    pts = sum(WEIGHT[f["severity"]] for f in findings)
    density = pts / units
    if density < 0.5:
        grade = "A"
    elif density < 1.5:
        grade = "B"
    elif density < 3.0:
        grade = "C"
    else:
        grade = "D"
    counts = {k: sum(1 for f in findings if f["severity"] == k) for k in WEIGHT}
    return {"points": round(pts, 1), "per_500_chars": round(density, 2), "grade": grade, "counts": counts}


def fix(text, doc_type=None, lexicon=None):
    """auto=true 항목만 치환. (교정문, 변경목록) 반환."""
    lex = lexicon or load_lexicon()
    changes = []
    out_lines = []
    for no, line, protected in marked_lines(text):
        if protected:
            out_lines.append(line)
            continue
        new = line
        for e in lex["entries"]:
            if not e["auto"] or not e["replace"]:
                continue
            if e["types"] and doc_type and doc_type not in e["types"]:
                continue
            for m in list(e["_re"].finditer(new)):
                before = m.group(0)
                after = m.expand(e["replace"])
                if before != after:
                    changes.append({"line": no, "id": e["id"], "before": before, "after": after})
            new = e["_re"].sub(e["replace"], new)
        out_lines.append(new)
    return "".join(out_lines), changes
