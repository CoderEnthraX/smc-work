const fs = require('fs');
const path = process.argv[2];
const raw = fs.readFileSync(path, 'utf8');
const lines = raw.split(/\r?\n/);
console.log(`### ${path.split('/').pop()}`);

// 1. string-literal lexer: an unterminated " on a line is a v15.6.1-class fault
let strBad = 0;
lines.forEach((line, i) => {
  let inStr = false, quote = '';
  for (let j = 0; j < line.length; j++) {
    const c = line[j];
    if (inStr) { if (c === '\\') { j++; continue; } if (c === quote) inStr = false; }
    else {
      if (c === '/' && line[j + 1] === '/') break;
      if (c === '"' || c === "'") { inStr = true; quote = c; }
    }
  }
  if (inStr) { console.log(`  UNTERMINATED STRING line ${i + 1}: ${line.trim().slice(0, 100)}`); strBad++; }
});
console.log(`  unterminated string literals: ${strBad}`);

// 2. bracket balance over code (strings/comments excluded)
let par = 0, brk = 0, bad = 0;
lines.forEach((line, i) => {
  let inStr = false, quote = '';
  for (let j = 0; j < line.length; j++) {
    const c = line[j];
    if (inStr) { if (c === '\\') { j++; continue; } if (c === quote) inStr = false; continue; }
    if (c === '"' || c === "'") { inStr = true; quote = c; continue; }
    if (c === '/' && line[j + 1] === '/') break;
    if (c === '(') par++; else if (c === ')') par--;
    else if (c === '[') brk++; else if (c === ']') brk--;
  }
  if (par < 0 || brk < 0) { console.log(`  NEGATIVE depth at line ${i + 1}`); bad++; par = Math.max(0, par); brk = Math.max(0, brk); }
});
console.log(`  bracket balance: parens ${par}, brackets ${brk} ${par === 0 && brk === 0 && bad === 0 ? '(OK)' : '(FAIL)'}`);

// 3. code-only view for structural checks
const code = lines.map(line => {
  let inStr = false, quote = '', cut = -1;
  for (let j = 0; j < line.length; j++) {
    const c = line[j];
    if (inStr) { if (c === '\\') { j++; continue; } if (c === quote) inStr = false; }
    else { if (c === '"' || c === "'") { inStr = true; quote = c; continue; } if (c === '/' && line[j + 1] === '/') { cut = j; break; } }
  }
  return (cut >= 0 ? line.slice(0, cut) : line).replace(/\s+$/, '');
});

// 4. empty blocks: a line ending in "=>" or an if/else/for whose next code line is not deeper
let empties = 0;
for (let i = 0; i < code.length; i++) {
  const t = code[i].trim();
  if (t === '') continue;
  const opens = /=>$/.test(t) || /^(if|else if|else|for|while|switch)\b.*$/.test(t) && !/=>/.test(t) && /:$|^else$|^(if|for|while|else if|switch)\b/.test(t);
  if (!opens) continue;
  const ind = code[i].match(/^\s*/)[0].length;
  let j = i + 1;
  while (j < code.length && code[j].trim() === '') j++;
  if (j >= code.length) { console.log(`  EMPTY BLOCK at end, line ${i + 1}: ${t.slice(0,80)}`); empties++; continue; }
  const nind = code[j].match(/^\s*/)[0].length;
  if (nind <= ind) { console.log(`  EMPTY BLOCK line ${i + 1}: ${t.slice(0, 80)}`); empties++; }
}
console.log(`  empty blocks: ${empties}`);

// 5. comma-separated declarations (Pine has none)
let commaDecl = 0;
code.forEach((l, i) => {
  const t = l.trim();
  if (/^(var\s+)?(float|int|bool|string|color|line|label|box|table)\s+\w+\s*=\s*[^,]*,\s*\w+\s*=/.test(t)) { console.log(`  COMMA DECL line ${i + 1}: ${t.slice(0,90)}`); commaDecl++; }
});
console.log(`  comma-separated declarations: ${commaDecl}`);

// 6. indentation: every indent must be a multiple of 4 and never a lone stray
let indBad = 0;
code.forEach((l, i) => {
  if (l.trim() === '') return;
  const ind = l.match(/^ */)[0].length;
  if (ind % 4 !== 0) { console.log(`  ODD INDENT (${ind}) line ${i + 1}: ${l.trim().slice(0, 80)}`); indBad++; }
});
console.log(`  non-multiple-of-4 indents: ${indBad}`);

// 7. emoji present in CODE (not comments)
const emo = code.filter(l => /[\u{1F300}-\u{1FAFF}]/u.test(l));
console.log(`  emoji in code lines: ${emo.length}`);
emo.forEach(l => console.log(`      ${l.trim().slice(0, 100)}`));
