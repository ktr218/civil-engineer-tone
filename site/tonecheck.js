/* 토목 실무 문체 검사기 — skills/civil-engineer-tone/scripts/tonelib.py와 check_values.py(수치 대조)를 브라우저용으로 옮긴 것.
 * 규칙·판정은 Python판과 같아야 한다(tests/test_site.py가 시험 문서로 대조한다).
 * site/build.js가 아래 LEXICON 자리에 references/lexicon.json을 넣어 docs/tonecheck.js로 쓴다.
 * 브라우저: window.ToneCheck / Node: require("./tonecheck.js")
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ToneCheck = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var LEXICON = /*@LEXICON*/ null;

  var TYPES = "RSBCAVPMG";
  var WEIGHT = { S1: 5.0, S2: 2.0, S3: 0.5 };
  var END_PATTERNS = [
    ["polite", /(니다|니까|세요|십시오|어요|아요|에요|해요|죠)$/],
    ["haja", /(하자|줄이자|바꾸자|늘리자|없애자|높이자|낮추자|세우자|만들자|쓰자|두자)$/],
    ["eum", /(임|함|음|됨|있음|없음|바람|바랍|하였음|되었음|예정임|필요함)$/],
    ["plain", /(다)$/]
  ];
  var TRAIL = /[\s.。,;:)\]>」』"'”’]+$|<[^>]*>$|\([^)]*\)$/g;
  var ALLOWED = {
    R: ["plain", "noun"], S: ["plain", "noun", "eum"], B: ["noun", "eum"], C: ["noun", "eum", "polite"],
    A: ["eum", "noun"], V: ["haja", "noun"], P: ["polite", "noun"], M: ["polite", "noun", "eum"],
    G: ["polite", "noun", "eum", "plain"]
  };
  var FORBIDDEN = {
    R: ["polite", "haja", "eum"], S: ["polite", "haja"], B: ["polite", "haja"], C: ["haja"], A: ["polite", "haja"],
    V: ["polite"], P: ["eum", "haja"], M: ["haja"], G: ["haja"]
  };
  var CLOSING_OK = new RegExp("상기와\\s*같이|위와\\s*같이|이상과\\s*같이|귀중|제출합니다|보고합니다|" +
    "감사합니다|바랍니다|드립니다|주시기|하시기|알려드리|작성요령|기재합니다|적습니다|" +
    "공고합니다|고시합니다|확약합니다|서약합니다|보증합니다|위임합니다|신고합니다|통지합니다");
  var BULLETS = ["□", "■", "○", "❍", "∘", "◦", "-", "∙", "·", "⋅", "․", "‧", "⦁", "•", "▪"];
  var END_NAME = { polite: "경어체(~니다)", plain: "평서형(~다)", eum: "음슴체(~임/함/음)", haja: "청유형(~하자)", noun: "명사형" };
  var KW = {
    C: "수정\\s*바람|제시\\s*필요|하기\\s*바람|불일치|상이함|과소산정|과다산정|누락|검토\\s*의견|권고|쟁점\\s*:|질의\\s*\\d*\\s*:|질의사항|여야\\s*합니다|필요합니다|【[^】]*검토[^】]*】|재원협의",
    A: "하였음|조치\\s*결과|조치\\s*계획|반영\\s*여부|<첨부|일부반영",
    S: "원칙으로\\s*한다|에\\s*따른다|에\\s*의한다|할\\s*수\\s*있다|하여야\\s*한다|기준으로\\s*한다",
    P: "보고\\s*드리|되겠습니다|위원님|감사합니다|사료됩니다",
    M: "드립니다|부탁드립니다|공유드|제목\\s*:|님,|회신",
    V: "제안\\s*No|하자$|VE",
    G: "^\\s*수\\s*신\\s*(?:자|[:：]|\\s)|\\(경유\\)|^\\s*제\\s*목\\s*[:：]|끝\\.\\s*$|^\\s*붙\\s*임\\s*[:：\\d]|붙임\\s*\\d|위\\s*호와\\s*관련|" +
      "알려드리|^\\s*시\\s*행\\s*[:：]|시행\\s*[가-힣]+-\\d|접\\s*수\\s*[:：]|접수\\s*번호|전화\\s*/?\\s*전송|귀하$",
    B: "과\\s*업\\s*명|사\\s*업\\s*명|추진경위|사업개요|과업기간",
    R: "판단된다|나타났다|검토하였다|산정하였다|실정이다|다음과\\s*같다"
  };
  var KW_ORDER = ["C", "A", "S", "P", "M", "V", "G", "B", "R"];
  var KW_RE = {};
  KW_ORDER.forEach(function (t) { KW_RE[t] = new RegExp(KW[t], "gm"); });

  // Python str.isspace()와 같은 공백 집합
  var PY_WS = "\\t\\n\\x0b\\x0c\\r\\x1c-\\x1f \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000";
  var STRIP_RE = new RegExp("^[" + PY_WS + "]+|[" + PY_WS + "]+$", "g");
  var WS_RE = new RegExp("[" + PY_WS + "]", "g");
  var LINEBREAK = new RegExp("\\r\\n|[\\n\\r\\x0b\\x0c\\x1c\\x1d\\x1e\\x85\\u2028\\u2029]", "g");

  function strip(s) { return s.replace(STRIP_RE, ""); }
  function len(s) { return Array.from(s).length; }
  function head(s, n) { return Array.from(s).slice(0, n).join(""); }
  function tail(s, n) { var a = Array.from(s); return a.slice(Math.max(0, a.length - n)).join(""); }
  function count(re, s) { re.lastIndex = 0; var m = s.match(re); return m ? m.length : 0; }

  var compiled = null;
  function compile(pattern) {
    var p = pattern.replace(/\\U([0-9A-Fa-f]{8})/g, function (_, h) { return "\\u{" + parseInt(h, 16).toString(16) + "}"; });
    try { return new RegExp(p, "mu"); } catch (e) { return new RegExp(p, "m"); }
  }
  function setLexicon(lex) {
    compiled = {
      version: lex.version,
      entries: lex.entries.map(function (e) {
        var re = compile(e.pattern);
        return {
          id: e.id, re: re, reAll: new RegExp(re.source, re.flags + "g"), replace: e.replace, suggest: e.suggest || [],
          types: e.types || [], severity: e.severity, taxonomy: e.taxonomy, auto: !!e.auto, note: e.note || ""
        };
      })
    };
    return compiled;
  }
  function lexicon() {
    if (!compiled) {
      if (!LEXICON) throw new Error("lexicon not loaded");
      setLexicon(LEXICON);
    }
    return compiled;
  }

  function pyStripTrail(line) {
    var s = strip(line), prev = null;
    while (prev !== s) {
      prev = s;
      TRAIL.lastIndex = 0;
      s = strip(s.replace(TRAIL, ""));
    }
    return s;
  }

  function classifyEnding(line) {
    var s = pyStripTrail(line);
    if (len(s) < 6 || !/[가-힣]/.test(s)) return null;
    if (s.charAt(0) === "|" || (s.match(/\|/g) || []).length >= 2) return null;
    for (var i = 0; i < END_PATTERNS.length; i++) if (END_PATTERNS[i][1].test(s)) return END_PATTERNS[i][0];
    if (/[가-힣]$/.test(s)) return "noun";
    return null;
  }

  // Python str.splitlines(keepends=True)
  function splitKeep(text) {
    var out = [], last = 0, m;
    LINEBREAK.lastIndex = 0;
    while ((m = LINEBREAK.exec(text))) {
      out.push(text.slice(last, m.index + m[0].length));
      last = m.index + m[0].length;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
  }

  function markedLines(text) {
    var fence = null, out = [];
    splitKeep(text).forEach(function (line, i) {
      var m = /^ {0,3}(`{3,}|~{3,})(.*)$/.exec(line.replace(/[\r\n]+$/, ""));
      var prot = fence !== null;
      if (m) {
        var run = m[1], info = m[2];
        if (fence === null) {
          if (run.charAt(0) !== "`" || info.indexOf("`") < 0) { fence = [run.charAt(0), run.length]; prot = true; }
        } else if (run.charAt(0) === fence[0] && run.length >= fence[1] && !strip(info)) {
          fence = null;
        }
      }
      out.push([i + 1, line, prot]);
    });
    return out;
  }

  function contentLines(text) {
    var out = [];
    markedLines(text).forEach(function (x) {
      if (x[2]) return;
      var line = x[1].replace(/[\r\n]+$/, "");
      var st = strip(line);
      if (st.charAt(0) === ">") line = st.slice(1);
      out.push([x[0], line]);
    });
    return out;
  }

  function startsWithAny(s, arr) { for (var i = 0; i < arr.length; i++) if (s.indexOf(arr[i]) === 0) return true; return false; }

  function detectType(text) {
    var sc = {}; TYPES.split("").forEach(function (t) { sc[t] = 0; });
    var ends = {}, lines = contentLines(text).map(function (x) { return x[1]; }).filter(function (l) { return strip(l); });
    var prose = lines.join("\n"), nl = Math.max(1, lines.length);
    var bullets = 0, pauses = 0, haja = 0, plainBul = 0;
    lines.forEach(function (l) {
      var s = strip(l), e = classifyEnding(s);
      if (e === "haja") haja++;
      if (len(s) >= (nl > 60 ? 40 : 15)) {
        if (e) ends[e] = (ends[e] || 0) + 1;
        if (e === "plain" && startsWithAny(s, ["○", "❍", "•", "-", "∘", "◦"])) plainBul++;
      }
      if (startsWithAny(s, BULLETS)) bullets++;
      if (s.indexOf("/") >= 0 && /니다[.\s]*$/.test(s)) pauses++;
    });
    var n = 0; Object.keys(ends).forEach(function (k) { n += ends[k]; }); n = n || 1;
    function r(k) { return (ends[k] || 0) / n; }
    var b = bullets / nl;
    sc.B += 2.5 * b; sc.C += 1.0 * b; sc.A += 1.0 * b;
    sc.P += 6 * Math.min(1.0, pauses / nl * 5);
    sc.R += 8 * r("plain"); sc.S += 6 * r("plain"); sc.B += 5 * r("noun"); sc.A += 12 * r("eum");
    sc.C += 2 * r("noun") + 3 * r("eum");
    sc.V += 8 * r("haja") + 8 * Math.min(1.0, haja / 5.0);
    sc.S += 5 * (plainBul / Math.max(1, ends.plain || 0));
    sc.P += 4 * r("polite"); sc.M += 3 * r("polite"); sc.G += 1.5 * r("polite") + 1.0 * r("eum");
    KW_ORDER.forEach(function (t) {
      var hits = count(KW_RE[t], prose);
      sc[t] += 1.5 * Math.min(3.0, hits / Math.max(1.0, nl / 20.0));
    });
    var best = "R", bv = -Infinity;
    TYPES.split("").forEach(function (t) { if (sc[t] > bv) { bv = sc[t]; best = t; } });
    return [best, sc];
  }

  function check(text, docType) {
    var lex = lexicon(), findings = [], lines = contentLines(text);
    var prose = lines.map(function (x) { return x[1]; }).join("\n");
    lines.forEach(function (x) {
      var no = x[0], s = strip(x[1]);
      if (!s) return;
      lex.entries.forEach(function (e) {
        if (e.types.length && e.types.indexOf(docType) < 0) return;
        var m = e.re.exec(s);
        if (m) {
          findings.push({ line: no, id: e.id, taxonomy: e.taxonomy, severity: e.severity, match: strip(m[0]),
            suggest: e.suggest, auto: e.auto, message: e.note || "어휘·표기 정규화", text: head(s, 90) });
        }
      });
      var end = classifyEnding(s);
      if (end && FORBIDDEN[docType].indexOf(end) >= 0 && !CLOSING_OK.test(s)) {
        var sev;
        if ("RS".indexOf(docType) >= 0 && end === "polite") sev = "S1";
        else if ((docType === "R" && end === "eum") || ("CA".indexOf(docType) >= 0 && end === "haja")) sev = "S3";
        else sev = "S2";
        findings.push({ line: no, id: "END", taxonomy: "A-1", severity: sev, match: tail(pyStripTrail(s), 8),
          suggest: ALLOWED[docType].slice().sort().map(function (k) { return END_NAME[k]; }), auto: false,
          message: "유형 " + docType + "에 맞지 않는 종결: " + END_NAME[end], text: head(s, 90) });
      }
    });
    var judge = count(/것으로\s*(?:판단된다|판단됨|사료된다)/g, prose);
    var kchars = Math.max(1.0, len(prose.replace(WS_RE, "")) / 1000.0);
    if (docType === "R" && judge >= 3 && judge / kchars > 2.0) {
      findings.push({ line: 0, id: "DOC-1", taxonomy: "A-2", severity: "S2",
        match: "'것으로 판단된다' 1,000자당 " + (judge / kchars).toFixed(1) + "회",
        suggest: ["~나타났다", "~이다", "~검토되었다"], auto: false, message: "판단 유보형 과다: 사실은 단정형으로", text: "" });
    }
    lines.forEach(function (x) {
      if (count(/\s등(?=\s|$|을|이|의|에|으로)/g, x[1]) >= 4) {
        findings.push({ line: x[0], id: "DOC-2", taxonomy: "F-3", severity: "S3", match: "등 x3+",
          suggest: ["한 문장 1회"], auto: false, message: "'등' 남용", text: head(strip(x[1]), 90) });
      }
    });
    var short = 0;
    lines.forEach(function (x) {
      var e = classifyEnding(x[1]);
      if (docType === "R" && e === "plain" && len(strip(x[1])) < 18) {
        short++;
        if (short === 3) {
          findings.push({ line: x[0], id: "DOC-3", taxonomy: "J-1", severity: "S3", match: "짧은 문장 3연속",
            suggest: ["문장 결합"], auto: false, message: "보고서 본문은 60~120자 문장이 일반적", text: "" });
        }
      } else {
        short = 0;
      }
    });
    var order = { S1: 0, S2: 1, S3: 2 };
    findings.sort(function (a, b) { return (order[a.severity] - order[b.severity]) || (a.line - b.line); });
    return findings;
  }

  function score(findings, text) {
    var prose = contentLines(text).map(function (x) { return x[1]; }).join("\n");
    var chars = len(prose.replace(WS_RE, ""));
    var units = Math.max(1.0, chars / 500.0);
    var pts = 0; findings.forEach(function (f) { pts += WEIGHT[f.severity]; });
    var density = pts / units;
    var grade = density < 0.5 ? "A" : density < 1.5 ? "B" : density < 3.0 ? "C" : "D";
    var counts = { S1: 0, S2: 0, S3: 0 };
    findings.forEach(function (f) { counts[f.severity]++; });
    return { points: Math.round(pts * 10) / 10, per_500_chars: Math.round(density * 100) / 100, grade: grade, counts: counts };
  }

  function expand(template, m) {
    return template.replace(/\\g<(\d+)>|\\(\d+)/g, function (_, a, b) { var g = m[+(a || b)]; return g == null ? "" : g; });
  }

  function fix(text, docType) {
    var lex = lexicon(), changes = [], out = [];
    markedLines(text).forEach(function (x) {
      var no = x[0], line = x[1];
      if (x[2]) { out.push(line); return; }
      var cur = line;
      lex.entries.forEach(function (e) {
        if (!e.auto || !e.replace) return;
        if (e.types.length && docType && e.types.indexOf(docType) < 0) return;
        e.reAll.lastIndex = 0;
        var m;
        while ((m = e.reAll.exec(cur))) {
          var after = expand(e.replace, m);
          if (m[0] !== after) changes.push({ line: no, id: e.id, before: m[0], after: after });
          if (m[0] === "") e.reAll.lastIndex++;
        }
        cur = cur.replace(e.reAll, function () { return expand(e.replace, arguments); });
      });
      out.push(cur);
    });
    return [out.join(""), changes];
  }

  /* ---------- 수치 대조: scripts/check_values.py를 옮긴 것(결과가 같아야 한다) ---------- */
  // 수치 환산은 하지 않는다. 표기만 동등한 단위와 어휘집의 auto 규칙을 쓴다.
  var VALUE_UNITS = [
    "ℓ/인·일", "m³/일", "m³/min", "m³/s", "㎥/일", "㎥/min", "㎥/s",
    "mm/hr", "mm/h", "km/h", "m/s", "mg/L", "㎎/L", "kg/m³", "kN/m²",
    "MWh/년", "Gcal/년", "TOE/년", "백만원", "억원", "천원", "원",
    "km²", "m²", "m³", "㎢", "㎡", "㎥", "km", "mm", "cm", "m",
    "MPa", "kPa", "Pa", "kN", "N", "MW", "kW", "W", "kV", "V",
    "kg", "mg", "㎎", "g", "ℓ", "L", "ha", "ppm", "℃", "°C", "%p", "%",
    "개소", "개", "기", "대", "명", "인", "년", "개월", "월", "일", "시간", "분", "초"
  ];
  var VALUE_SCOPE = "숫자·인식한 단위·부등호의 출현 개수를 비교함. 숫자 순서와 문장 재배치는 허용함. " +
    "같은 수치가 다른 시설·항목에 옮겨 붙은 경우, 단위 환산, 표 머리글의 단위, " +
    "미지원 단위, 사업명·근거·부정문·계획/완료 변경은 별도 원문 대조가 필요함. " +
    "fenced code는 제외하며 문서 번호·날짜도 숫자로 집계함. 차이 미검출은 사실 검증 통과가 아님.";
  // Python re의 \d는 유니코드 숫자, \s는 PY_WS다.
  var ND = "\\p{Nd}", SP = "[" + PY_WS + "]";
  var VNUMBER = "(?:" + ND + "{1,3}(?:," + ND + "{3})+(?!" + ND + ")|" + ND + "+)(?:\\." + ND + "+)?|\\." + ND + "+";
  var VSYMBOL = "D(?:N)?" + SP + "*=?" + SP + "*|[ΦØφ]" + SP + "*|(?:GL|EL|DL)\\.?" + SP + "*";
  var VREL = "<=|>=|≤|≥|<|>";
  var VUNIT = VALUE_UNITS.slice().sort(function (a, b) { return len(b) - len(a); })
    .map(function (u) { return u.replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&"); }).join("|");
  // Python의 조건부 그룹 (?(symbol)|(?<![A-Za-z0-9_]))은 기호가 있는 갈래와 없는 갈래로 나눠 같은 순서로 시도한다.
  var VTOKEN = new RegExp("(?<![0-9_])(?:(?<symbol>" + VSYMBOL + ")(?<rel>" + VREL + ")?" + SP + "*|(?<rel2>" + VREL + ")?" + SP +
    "*(?<![A-Za-z0-9_]))(?<number>[+−±△-]?" + SP + "*(?:" + VNUMBER + ")(?:[eE][+-]?" + ND + "+)?)" +
    "(?:" + SP + "*(?<unit>(?:" + VUNIT + ")(?![A-Za-z0-9_])))?", "gu");
  var VSTRIP = new RegExp("[" + PY_WS + ",]", "g"), ND1 = new RegExp("^" + ND + "$", "u");

  // 유니코드 숫자 → 0~9. Nd 숫자는 0부터 9까지 연속으로 배정되어 있다.
  function digit(ch) {
    var cp = ch.codePointAt(0), start = cp;
    if (cp >= 48 && cp <= 57) return ch;
    while (ND1.test(String.fromCodePoint(start - 1))) start--;
    return String((cp - start) % 10);
  }

  // Python의 Decimal(value).as_tuple()로 만든 키와 같은 문자열(뒤의 0을 지수로 옮김)
  function numberKey(value) {
    var v = value.replace(VSTRIP, "").replace(/−/g, "-"), prefix = "", sign = "";
    if (v.charAt(0) === "±" || v.charAt(0) === "△") { prefix = v.charAt(0); v = v.slice(1); }
    if (v.charAt(0) === "+" || v.charAt(0) === "-") { sign = v.charAt(0) === "-" ? "-" : ""; v = v.slice(1); }
    v = Array.from(v).map(function (ch) { return ND1.test(ch) ? digit(ch) : ch; }).join("");
    var m = /^(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(v);
    if (!m) throw new Error("수치를 읽지 못함: " + value);
    var frac = m[2] || "", digits = ((m[1] || "") + frac).replace(/^0+/, "");
    if (!digits) return prefix + "0";
    var core = digits.replace(/0+$/, "");
    var exp = (m[3] ? parseInt(m[3], 10) : 0) - frac.length + (digits.length - core.length);
    return prefix + sign + core + "e" + exp;
  }

  function extractValues(text) {
    var rows = [];
    contentLines(fix(text, null)[0]).forEach(function (x) {
      var line = x[1], cps = null, m;
      VTOKEN.lastIndex = 0;
      while ((m = VTOKEN.exec(line))) {
        var g = m.groups, rel = g.rel || g.rel2 || "";
        var start = len(line.slice(0, m.index)), end = start + len(m[0]);
        cps = cps || Array.from(line);
        rows.push({
          key: [rel === "≤" ? "<=" : rel === "≥" ? ">=" : rel, numberKey(g.number), (g.unit || "").normalize("NFKC")],
          line: x[0], value: strip(m[0]), context: strip(cps.slice(Math.max(0, start - 30), end + 30).join(""))
        });
      }
    });
    return rows;
  }

  // 원문과 윤문의 숫자·단위 출현 개수 비교. removed는 원문에서 줄어든 값, added는 윤문에서 늘어난 값.
  function compareValues(original, revised) {
    var before = extractValues(original), after = extractValues(revised);
    function tally(rows) {
      var c = new Map();
      rows.forEach(function (r) { var k = JSON.stringify(r.key); c.set(k, (c.get(k) || 0) + 1); });
      return c;
    }
    function differences(rows, mine, other) {
      var where = new Map(), out = [];
      rows.forEach(function (r) {
        var k = JSON.stringify(r.key);
        if (!where.has(k)) where.set(k, []);
        where.get(k).push({ line: r.line, value: r.value, context: r.context });
      });
      mine.forEach(function (n, k) {
        var d = n - (other.get(k) || 0);
        if (d > 0) out.push({ value: where.get(k)[0].value, count: d, locations: where.get(k) });
      });
      return out;
    }
    var a = tally(before), b = tally(after), removed = differences(before, a, b), added = differences(after, b, a);
    return { needs_review: removed.length > 0 || added.length > 0, original_count: before.length, revised_count: after.length,
      removed: removed, added: added, scope: VALUE_SCOPE };
  }

  return {
    TYPES: TYPES, END_NAME: END_NAME, setLexicon: setLexicon, lexicon: lexicon,
    classifyEnding: classifyEnding, detectType: detectType, check: check, score: score, fix: fix,
    VALUE_UNITS: VALUE_UNITS, VALUE_SCOPE: VALUE_SCOPE, extractValues: extractValues, compareValues: compareValues
  };
});
