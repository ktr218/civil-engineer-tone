/* 토목 실무 문체 검사기 — skills/civil-engineer-tone/scripts/tonelib.py를 브라우저용으로 옮긴 것.
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

  var LEXICON = {"version":"1.3.0","entries":[{"id":"U-01","pattern":"(\\d)\\s*(?:m3|m³|M3)\\s*/\\s*(?:day|d|DAY|일)(?![A-Za-z])","replace":"\\1㎥/일","suggest":["㎥/일"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":"유량(일) 단위"},{"id":"U-02","pattern":"(\\d)\\s*㎥\\s*/\\s*(?:day|d|DAY)(?![A-Za-z])","replace":"\\1㎥/일","suggest":["㎥/일"],"types":[],"severity":"S3","taxonomy":"G-1","auto":true,"note":"산식 안의 ㎥/d는 허용, 본문은 ㎥/일"},{"id":"U-03","pattern":"(\\d)\\s*CMD(?![A-Za-z])","replace":"\\1㎥/일","suggest":["㎥/일"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":"CMD 표기"},{"id":"U-04","pattern":"(\\d)\\s*(?:m3|m³)\\s*/\\s*(?:min|분)(?![A-Za-z])","replace":"\\1㎥/min","suggest":["㎥/min"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":""},{"id":"U-05","pattern":"(\\d)\\s*(?:m3|m³)\\s*/\\s*(?:s|sec|초)(?![A-Za-z])","replace":"\\1㎥/s","suggest":["㎥/s"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":""},{"id":"U-06","pattern":"(\\d)\\s*(?:m3|m³)(?!\\s*/)(?![A-Za-z0-9])","replace":"\\1㎥","suggest":["㎥"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":"체적"},{"id":"U-07","pattern":"(\\d)\\s*km2(?![A-Za-z0-9])","replace":"\\1㎢","suggest":["㎢"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":""},{"id":"U-08","pattern":"(\\d)\\s*m2(?![A-Za-z0-9])","replace":"\\1㎡","suggest":["㎡"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":""},{"id":"U-09","pattern":"지름\\s*(\\d[\\d,]*)\\s*mm(?=\\s*(?:의\\s*)?(?:관|하수|상수|오수|우수|배수|송수|도수|급수|차집))","replace":"D\\1mm","suggest":["D○○○mm"],"types":[],"severity":"S2","taxonomy":"G-1","auto":true,"note":"뒤에 관로가 올 때만 교정. 철근·안지름 등 일반 치수의 '지름'은 유지"},{"id":"U-11","pattern":"(\\d)\\s*(?:L|ℓ|리터)\\s*/\\s*(?:인|명)\\s*/\\s*일|(\\d)\\s*리터\\s*/\\s*(?:인|명)\\s*[·/]\\s*일","replace":"\\1\\2ℓ/인·일","suggest":["ℓ/인·일","Lpcd"],"types":[],"severity":"S3","taxonomy":"G-3","auto":true,"note":"원단위"},{"id":"U-12","pattern":"(\\d)\\s*(억|백만|천)\\s+원","replace":"\\1\\2원","suggest":["억원","백만원","천원"],"types":[],"severity":"S3","taxonomy":"G-2","auto":true,"note":"금액 단위 붙여쓰기 (실무 문서에도 띄어쓴 사례가 있어 S3)"},{"id":"U-13","pattern":"(\\d)\\s*퍼센트\\s*포인트","replace":"\\1%p","suggest":["%p"],"types":[],"severity":"S3","taxonomy":"G-2","auto":true,"note":""},{"id":"U-14","pattern":"(\\d)\\s*%\\s*포인트","replace":"\\1%p","suggest":["%p"],"types":[],"severity":"S3","taxonomy":"G-2","auto":true,"note":""},{"id":"U-15","pattern":"(\\d)\\s*퍼센트","replace":"\\1%","suggest":["%"],"types":[],"severity":"S3","taxonomy":"G-2","auto":true,"note":""},{"id":"U-17","pattern":"(?:BOD|COD|SS|T-N|T-P|TOC|수질|방류수|유입수|처리수|원수|하수)[^\\n]{0,25}?(\\d)\\s*ppm(?![A-Za-z])","replace":null,"suggest":["㎎/L"],"types":[],"severity":"S3","taxonomy":"G-1","auto":false,"note":"수질 농도는 ㎎/L로 통일. 대기질·시험 조건의 ppm은 그대로 둔다"},{"id":"U-18","pattern":"지(?:면|표)\\s*(?:아래|하)\\s*(\\d+(?:\\.\\d+)?)\\s*m","replace":"GL-\\1m","suggest":["GL-○.○m"],"types":[],"severity":"S3","taxonomy":"G-1","auto":true,"note":"지하수위·심도"},{"id":"U-19","pattern":"(\\d+)\\s*개\\s*곳(?![가-힣])","replace":"\\1개소","suggest":["개소"],"types":[],"severity":"S3","taxonomy":"G-1","auto":true,"note":""},{"id":"U-20","pattern":"(\\d+)\\s*곳(?![가-힣])","replace":null,"suggest":["○개소"],"types":["R","S","B","C","A"],"severity":"S3","taxonomy":"G-1","auto":false,"note":"시설 개수는 개소"},{"id":"T-01","pattern":"(?<!옥상)(?<!옥상\\s)물\\s*탱크(?!\\s*(?:받침|기초))","replace":null,"suggest":["배수지","정수지","저수조"],"types":[],"severity":"S3","taxonomy":"K-9","auto":false,"note":"공급용이면 배수지, 정수장 내 저류면 정수지, 건축물 내면 저수조. 건축·설비 문서의 옥상물탱크·받침대는 유지"},{"id":"T-02","pattern":"하수\\s*파이프|하수도\\s*파이프","replace":null,"suggest":["하수관로","오수관로","우수관로"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-03","pattern":"(?:수도|물)\\s*파이프","replace":null,"suggest":["상수관로","배수관로","급수관"],"types":["R","S","B","C","A"],"severity":"S2","taxonomy":"K-9","auto":false,"note":"파이프 대신 관로. '수도관'·'노후 수도관'은 시방·지침 용어로 허용"},{"id":"T-04","pattern":"(?<![상가-힣·ㆍ․･])하수도관(?![로망리련])","replace":null,"suggest":["하수관로"],"types":[],"severity":"S3","taxonomy":"K-9","auto":false,"note":"'상·하수도관'처럼 지장물 나열은 유지"},{"id":"T-05","pattern":"물\\s*새는|새는\\s*물","replace":null,"suggest":["누수","누수량"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-06","pattern":"땅을\\s*파(?:고|서|는|기)","replace":null,"suggest":["터파기","굴착"],"types":["R","S","B","C","A"],"severity":"S2","taxonomy":"K-9","auto":false,"note":"'땅파기'는 표준시방서 용어로 허용"},{"id":"T-07","pattern":"흙(?:을)?\\s*다시\\s*(?:덮|채우)","replace":null,"suggest":["되메우기"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-08","pattern":"(?:물이|빗물이)\\s*(?:잘\\s*)?안\\s*빠지","replace":null,"suggest":["내수배제 불량","통수능 부족"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-09","pattern":"오래된\\s*(?:관|파이프|수도관|하수관)","replace":null,"suggest":["노후관","노후관로"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-10","pattern":"새로\\s*(?:설치|만들|깔)","replace":null,"suggest":["신설"],"types":["R","B","C","A"],"severity":"S3","taxonomy":"K-9","auto":false,"note":""},{"id":"T-11","pattern":"(?:관|파이프)(?:을|를)?\\s*바꾸","replace":null,"suggest":["교체","개량"],"types":[],"severity":"S3","taxonomy":"K-9","auto":false,"note":""},{"id":"T-12","pattern":"방해물|걸리는\\s*시설","replace":null,"suggest":["지장물"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-13","pattern":"국가\\s*지원금|정부\\s*지원금","replace":null,"suggest":["국비","국고보조금"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-14","pattern":"설계\\s*결과물","replace":null,"suggest":["성과품","설계도서"],"types":[],"severity":"S3","taxonomy":"K-9","auto":false,"note":""},{"id":"T-17","pattern":"빗물\\s*펌프(?!장)","replace":null,"suggest":["빗물펌프장"],"types":[],"severity":"S3","taxonomy":"K-9","auto":false,"note":"시설을 가리키면 펌프장"},{"id":"T-18","pattern":"(?:정수|하수)\\s*공장","replace":null,"suggest":["정수장","공공하수처리시설","물재생센터"],"types":[],"severity":"S2","taxonomy":"K-9","auto":false,"note":""},{"id":"T-19","pattern":"프로젝트","replace":null,"suggest":["사업","과업","용역"],"types":["R","S","C","A"],"severity":"S3","taxonomy":"K-7","auto":false,"note":"공사·사업은 사업, 설계는 과업/용역. 내부 메일·폴더명에서는 허용"},{"id":"T-20","pattern":"(?<![가-힣])원래(?:는)?(?![가-힣])","replace":null,"suggest":["당초","기존"],"types":["R","B","C","A"],"severity":"S3","taxonomy":"C-2","auto":false,"note":"계획 변경 대비면 당초, 현존 시설이면 기존"},{"id":"T-21","pattern":"(^|\\s)이번\\s*(?=사업|과업|용역|계획|검토|설계)","replace":null,"suggest":["금회","본"],"types":["R","S","B","C","A"],"severity":"S3","taxonomy":"C-1","auto":false,"note":""},{"id":"T-22","pattern":"이미\\s*승인(?:된|받은)","replace":null,"suggest":["기승인"],"types":[],"severity":"S3","taxonomy":"C-3","auto":false,"note":""},{"id":"T-25","pattern":"되어지","replace":null,"suggest":["되"],"types":[],"severity":"S3","taxonomy":"K-10","auto":false,"note":""},{"id":"K-01","pattern":"혁신적|획기적|놀라운|탁월한|최첨단|완벽한|압도적","replace":null,"suggest":["삭제","정량 표현"],"types":[],"severity":"S2","taxonomy":"K-1","auto":false,"note":"P 유형에서 '기록적인 강우'처럼 사실 묘사는 허용"},{"id":"K-02","pattern":"중요한\\s*역할을\\s*(?:합니다|한다|하고)","replace":null,"suggest":["~에 기여한다","~기능을 한다"],"types":[],"severity":"S1","taxonomy":"K-2","auto":false,"note":""},{"id":"K-03","pattern":"아무리\\s*강조해도","replace":null,"suggest":["삭제"],"types":[],"severity":"S1","taxonomy":"K-2","auto":false,"note":""},{"id":"K-04","pattern":"다양한\\s*측면에서|종합적으로\\s*살펴보면|결론적으로|요약하자면","replace":null,"suggest":["따라서","검토결과"],"types":[],"severity":"S1","taxonomy":"K-2","auto":false,"note":""},{"id":"K-05","pattern":"이를\\s*통해[^.\\n]{0,40}수\\s*있(?:습니다|다|을 것)","replace":null,"suggest":["~것으로 판단된다","~효과가 있는 것으로 분석되었다"],"types":[],"severity":"S1","taxonomy":"K-2","auto":false,"note":""},{"id":"K-06","pattern":"라고\\s*할\\s*수\\s*있(?:습니다|다)","replace":null,"suggest":["~이다","~것으로 판단된다"],"types":[],"severity":"S1","taxonomy":"K-2","auto":false,"note":""},{"id":"K-07","pattern":"기대됩니다|기대된다","replace":null,"suggest":["~것으로 판단된다","~것으로 예상된다"],"types":["R","S","B","C","A"],"severity":"S3","taxonomy":"K-2","auto":false,"note":"실무 보고서에도 쓰임. 한 문서에서 반복될 때만 줄인다"},{"id":"K-08","pattern":"(?<![0-9A-Za-z*])(?<!\\[ )\\*\\*[^*\\s,][^*\\n,]{0,30}[^*\\s,]\\*\\*(?!\\*)|[✅✔✨❌⭐\\U0001F300-\\U0001FAFF]","replace":null,"suggest":["□ ○ - · 기호 위계"],"types":[],"severity":"S1","taxonomy":"K-4","auto":false,"note":"마크다운 굵게와 이모지. HWP·PPT로 옮기면 기호가 그대로 남는다"},{"id":"K-09","pattern":"정말|엄청|굉장히|너무나|매우\\s*매우","replace":null,"suggest":["삭제"],"types":["R","S","B","C","A","V"],"severity":"S1","taxonomy":"K-5","auto":false,"note":""},{"id":"K-10","pattern":"많은\\s*양의|상당한\\s*양|여러\\s*곳|대부분의\\s*지역","replace":null,"suggest":["수치","○○개소","[수치 확인 필요]"],"types":[],"severity":"S2","taxonomy":"K-6","auto":false,"note":""},{"id":"K-11","pattern":"(?<![가-힣A-Za-z㈜)○])(?:솔루션|인사이트|퍼포먼스|임팩트(?!식))","replace":null,"suggest":["개선방안","시사점","성능","효과","연계효과","추진계획"],"types":[],"severity":"S2","taxonomy":"K-7","auto":false,"note":"'로드맵'·'시너지(동반상승)'는 정책 문서에서 쓰여 제외"},{"id":"K-12","pattern":"지속\\s*가능한|친환경적이고|스마트한","replace":null,"suggest":["구체 목표로 대체"],"types":["R","C","A"],"severity":"S3","taxonomy":"K-8","auto":false,"note":"'스마트 정수장'처럼 사업명·정책명은 허용"},{"id":"K-13","pattern":"살펴보겠습니다|알아보겠습니다|소개하겠습니다","replace":null,"suggest":["보고 드리겠습니다(P)","검토하였다(R)"],"types":["R","S","B","C","A","P"],"severity":"S2","taxonomy":"K-2","auto":false,"note":""},{"id":"K-14","pattern":"도움이\\s*되(?:셨|었|었으)?(?:으면|길|기를)|궁금한\\s*점이\\s*있으시면|필요하시면\\s*(?:말씀|알려|언제든)|원하시면\\s*(?:말씀|알려|추가로)|추가로\\s*도와\\s*드릴|언제든지\\s*(?:말씀|문의)","replace":null,"suggest":["삭제"],"types":[],"severity":"S1","taxonomy":"K-2","auto":false,"note":"AI 대화체 맺음말. 문서 본문에 넣지 않는다"}]};

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

  return {
    TYPES: TYPES, END_NAME: END_NAME, setLexicon: setLexicon, lexicon: lexicon,
    classifyEnding: classifyEnding, detectType: detectType, check: check, score: score, fix: fix
  };
});
