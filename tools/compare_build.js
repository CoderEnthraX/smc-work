const fs = require('fs');

// Strip comments the way Pine sees them: a // outside a string literal starts a comment.
// Returns { code: [lines], inputs: [decls] }
function parse(path) {
  const raw = fs.readFileSync(path, 'utf8');
  const lines = raw.split(/\r?\n/);
  const code = [];
  const inputs = [];
  for (const line of lines) {
    let inStr = false, quote = '', cut = -1;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (inStr) {
        if (c === '\\') { i++; continue; }
        if (c === quote) inStr = false;
      } else {
        if (c === '"' || c === "'") { inStr = true; quote = c; continue; }
        if (c === '/' && line[i + 1] === '/') { cut = i; break; }
      }
    }
    const stripped = (cut >= 0 ? line.slice(0, cut) : line).replace(/\s+$/, '');
    if (stripped.trim() === '') continue;
    code.push(stripped);
    const m = stripped.match(/^(\s*)([A-Za-z_]\w*)\s*=\s*(input\.\w+)\s*\((.*)$/);
    if (m) inputs.push({ name: m[2], fn: m[3], rest: m[4] });
  }
  return { code, inputs };
}

// First positional arg of an input.*() call = its default value.
function defaultOf(rest) {
  let depth = 0, inStr = false, quote = '';
  for (let i = 0; i < rest.length; i++) {
    const c = rest[i];
    if (inStr) {
      if (c === '\\') { i++; continue; }
      if (c === quote) inStr = false;
      continue;
    }
    if (c === '"' || c === "'") { inStr = true; quote = c; continue; }
    if (c === '(' || c === '[') depth++;
    else if (c === ')' || c === ']') { if (depth === 0) return rest.slice(0, i).trim(); depth--; }
    else if (c === ',' && depth === 0) return rest.slice(0, i).trim();
  }
  return rest.trim();
}

const [a, b, label] = process.argv.slice(2);
const A = parse(a), B = parse(b);

console.log(`## ${label}`);
console.log(`executable lines:  base ${A.code.length}   opt ${B.code.length}   delta ${B.code.length - A.code.length}`);
console.log(`inputs:            base ${A.inputs.length}   opt ${B.inputs.length}`);

// --- inputs by POSITION: name, type, default ---
let bad = 0;
const n = Math.max(A.inputs.length, B.inputs.length);
for (let i = 0; i < n; i++) {
  const x = A.inputs[i], y = B.inputs[i];
  if (!x || !y) { console.log(`  [${i}] MISSING  ${x ? x.name : '-'} / ${y ? y.name : '-'}`); bad++; continue; }
  const dx = defaultOf(x.rest), dy = defaultOf(y.rest);
  if (x.name !== y.name || x.fn !== y.fn || dx !== dy) {
    console.log(`  [${i}] DIFF  ${x.name}:${x.fn}=${dx}   ->   ${y.name}:${y.fn}=${dy}`);
    bad++;
  }
}
console.log(`inputs differing by position/name/type/default: ${bad}`);

// --- multiset diff of executable lines (position-independent) ---
const bag = m => { const o = new Map(); for (const l of m) { const k = l.trim(); o.set(k, (o.get(k) || 0) + 1); } return o; };
const ba = bag(A.code), bb = bag(B.code);
const onlyA = [], onlyB = [];
for (const [k, v] of ba) { const d = v - (bb.get(k) || 0); if (d > 0) onlyA.push([k, d]); }
for (const [k, v] of bb) { const d = v - (ba.get(k) || 0); if (d > 0) onlyB.push([k, d]); }
console.log(`\nonly in BASE (${onlyA.reduce((s, x) => s + x[1], 0)} lines):`);
for (const [k, d] of onlyA) console.log(`  -${d > 1 ? ' x' + d : '  '} ${k.slice(0, 150)}`);
console.log(`\nonly in OPT (${onlyB.reduce((s, x) => s + x[1], 0)} lines):`);
for (const [k, d] of onlyB) console.log(`  +${d > 1 ? ' x' + d : '  '} ${k.slice(0, 150)}`);
