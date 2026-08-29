// Declaration-order check.
//
// Pine resolves identifiers textually: a function, method, type, input or
// variable must appear BEFORE the line that uses it. Nothing else in this
// toolchain catches a use-before-declaration, and it is the most likely way a
// hand-written patch fails to compile.
//
// Usage: node declorder.js <file> [ident ...]
// With no idents, every identifier introduced by the build is checked.

'use strict';
const fs = require('fs');

const path = process.argv[2];
const raw = fs.readFileSync(path, 'utf8');
const lines = raw.split(/\r?\n/).map(line => {
  let inStr = false, quote = '', cut = -1;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inStr) { if (c === '\\') { i++; continue; } if (c === quote) inStr = false; }
    else {
      if (c === '"' || c === "'") { inStr = true; quote = c; continue; }
      if (c === '/' && line[i + 1] === '/') { cut = i; break; }
    }
  }
  return cut >= 0 ? line.slice(0, cut) : line;
});

const idents = process.argv.slice(3).length ? process.argv.slice(3) : [
  // P1 / P2
  'drawB', 'setDraw',
  'iCeilSwpB', 'iFlorSwpB', 'nCeilSwpB', 'nFlorSwpB',
  'iCeilDrawB', 'iFlorDrawB', 'nCeilDrawB', 'nFlorDrawB',
  // P4
  'f_retExtB', 'rearmB', 'f_isSwingB', 'f_lastMinorB', 'f_armIdmB',
  // P6
  'tblWarm', 'f_tfRow',
  // pre-existing things the new f_tfPack leans on
  'SwingTracker', 'altMode', 'inPivK', 'trendDir', 'iTrend', 'nTrend', 'gTbl',
];

function declLine(id) {
  const pats = [
    new RegExp(`^\\s*(?:var\\s+)?(?:[\\w<>]+\\s+)?${id}\\s*=[^=]`),   // assignment / input
    new RegExp(`^${id}\\s*\\(`),                                       // function
    new RegExp(`^method\\s+${id}\\s*\\(`),                             // method
    new RegExp(`^type\\s+${id}\\b`),                                   // type
    new RegExp(`^\\s{4}\\w[\\w<>]*\\s+${id}\\s*$`),                    // type field
  ];
  for (let i = 0; i < lines.length; i++) {
    if (pats.some(p => p.test(lines[i]))) return i + 1;
  }
  return null;
}
function firstUse(id, declAt) {
  const use = new RegExp(`\\b${id}\\b`);
  for (let i = 0; i < lines.length; i++) {
    if (i + 1 === declAt) continue;
    if (use.test(lines[i])) return i + 1;
  }
  return null;
}

let bad = 0;
console.log(`  ${'identifier'.padEnd(16)} ${'declared'.padStart(9)} ${'first use'.padStart(10)}   status`);
for (const id of idents) {
  const d = declLine(id);
  const u = firstUse(id, d);
  let status;
  if (d === null) { status = 'NOT DECLARED'; bad++; }
  else if (u !== null && u < d) { status = `USE BEFORE DECLARATION (line ${u} < ${d})`; bad++; }
  else status = 'ok';
  console.log(`  ${id.padEnd(16)} ${String(d ?? '-').padStart(9)} ${String(u ?? '-').padStart(10)}   ${status}`);
}
console.log(bad ? `\n  ${bad} PROBLEM(S)` : '\n  all identifiers declared before first use');
process.exit(bad ? 1 : 0);
