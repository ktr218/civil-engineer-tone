// 웹 검사기의 수치 대조(docs/tonecheck.js의 compareValues)를 JSON으로 낸다.
// tests/test_site.py가 check_values.py와 대조한다.
// 실행: node tests/js_values.js < 쌍.json      (쌍.json = [[원문, 윤문], ...])
"use strict";
const fs = require("fs");
const path = require("path");
const TC = require(path.join(__dirname, "..", "docs", "tonecheck.js"));

const pairs = JSON.parse(fs.readFileSync(0, "utf8"));
const results = pairs.map(([original, revised]) => TC.compareValues(original, revised));
process.stdout.write(JSON.stringify({ units: TC.VALUE_UNITS, results }));
