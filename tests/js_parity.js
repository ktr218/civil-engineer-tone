// 웹 검사기(docs/tonecheck.js)의 판정을 JSON으로 낸다. tests/test_site.py가 Python 검사기와 대조한다.
// 실행: node tests/js_parity.js <파일>...   (파일 목록이 길면 @목록파일 한 개)
"use strict";
const fs = require("fs");
const path = require("path");
const TC = require(path.join(__dirname, "..", "docs", "tonecheck.js"));

let files = process.argv.slice(2);
if (files.length === 1 && files[0].startsWith("@")) {
  files = fs.readFileSync(files[0].slice(1), "utf8").split(/\r?\n/).filter(Boolean);
}
const out = files.map((file) => {
  const text = fs.readFileSync(file, "utf8");
  const type = TC.detectType(text)[0];
  const found = TC.check(text, type);
  const s = TC.score(found, text);
  const [fixed, changes] = TC.fix(text, null);
  return {
    file, type, grade: s.grade, per500: s.per_500_chars, fixed, nchanges: changes.length,
    findings: found.map((f) => [f.line, f.id, f.severity, f.match]),
  };
});
process.stdout.write(JSON.stringify(out));
