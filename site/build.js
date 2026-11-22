// 랜딩페이지 빌드. 외부 패키지 없이 Node만 있으면 된다.
//   node site/build.js            → docs/index.html, docs/tonecheck.js
//   node site/build.js <출력폴더>  → 그 폴더에 같은 두 파일(시험용)
// index.tpl.html의 {{TbXxx}}는 icons.json(Tabler Icons, MIT)의 SVG로, {{MQ1}}·{{MQ2}}는 아래 예시로 채운다.
// tonecheck.js에는 스킬의 references/lexicon.json을 넣는다. 검사 규칙의 원본은 스킬 쪽이다.
"use strict";
const fs = require("fs");
const path = require("path");

const SITE = __dirname;
const ROOT = path.join(SITE, "..");
const OUT = process.argv[2] ? path.resolve(process.argv[2]) : path.join(ROOT, "docs");
const LEXICON = path.join(ROOT, "skills", "civil-engineer-tone", "references", "lexicon.json");

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const pair = ([a, b]) =>
  `<span class="pair"><span class="f">${esc(a)}</span><span class="ar" aria-hidden="true">→</span><span class="t">${esc(b)}</span></span>`;

// 지침(prompts/universal.md)의 변환 규칙에서 고른 예
const ROW1 = [
  ["반영할게요!", "반영하겠음"], ["이번 사업", "금회 사업"], ["원래 계획", "당초 계획"],
  ["650 m3/day", "Q=650㎥/일"], ["지름 400mm 관", "D400mm 관"], ["길이 13km", "L=13.0km"],
  ["2억 원", "2억원"], ["3곳", "3개소"], ["~것 같아요", "~것으로 판단됨"],
];
const ROW2 = [
  ["물탱크", "배수지"], ["다리", "교량"], ["둑", "제방"], ["오래된 관", "노후관로"],
  ["새로 설치", "신설"], ["땅을 파다", "터파기"], ["방해물", "지장물"], ["설계사", "과업수행사"],
  ["해결책", "개선방안"], ["그래서", "따라서"],
];
const chips = (rows) => rows.concat(rows).map(pair).join("");

function build() {
  const icons = JSON.parse(fs.readFileSync(path.join(SITE, "icons.json"), "utf8"));
  let html = fs.readFileSync(path.join(SITE, "index.tpl.html"), "utf8");
  html = html.split("{{MQ1}}").join(chips(ROW1)).split("{{MQ2}}").join(chips(ROW2));
  html = html.replace(/\{\{(Tb\w+)\}\}/g, (_, n) => {
    if (!icons[n]) throw new Error("icons.json에 없는 아이콘: " + n);
    return icons[n];
  });
  if (html.includes("{{")) throw new Error("채우지 못한 자리표시자: " + html.match(/\{\{[^}]*\}\}/)[0]);

  const lex = JSON.parse(fs.readFileSync(LEXICON, "utf8"));
  const slim = {
    version: lex.version,
    entries: lex.entries.map((e) => ({
      id: e.id, pattern: e.pattern, replace: e.replace, suggest: e.suggest, types: e.types,
      severity: e.severity, taxonomy: e.taxonomy, auto: e.auto, note: e.note,
    })),
  };
  const src = fs.readFileSync(path.join(SITE, "tonecheck.js"), "utf8");
  if (!src.includes("/*@LEXICON*/ null")) throw new Error("tonecheck.js에 어휘집 자리가 없습니다");
  const js = src.replace("/*@LEXICON*/ null", JSON.stringify(slim));

  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, "index.html"), html);
  fs.writeFileSync(path.join(OUT, "tonecheck.js"), js);
  return { html: html.length, js: js.length };
}

if (require.main === module) {
  const r = build();
  console.log(`wrote ${path.join(OUT, "index.html")} (${r.html} chars), tonecheck.js (${r.js} chars)`);
}
module.exports = { build };
