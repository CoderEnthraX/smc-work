const fs = require('fs');
function codeLines(path) {
  return fs.readFileSync(path, 'utf8').split(/\r?\n/).map(line => {
    let inStr = false, quote = '', cut = -1;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (inStr) { if (c === '\\') { i++; continue; } if (c === quote) inStr = false; }
      else {
        if (c === '"' || c === "'") { inStr = true; quote = c; continue; }
        if (c === '/' && line[i + 1] === '/') { cut = i; break; }
      }
    }
    return (cut >= 0 ? line.slice(0, cut) : line);
  });
}
const [basePath, optPath] = process.argv.slice(2);
const base = codeLines(basePath), opt = codeLines(optPath);
const ids = ['mainRetBorn','intRetBorn','nnRetBorn','iCeilSwpB','iFlorSwpB','nCeilSwpB','nFlorSwpB','f_confExt'];

console.log('=== In BASE: is each occurrence a WRITE or a READ? ===');
for (const id of ids) {
  const re = new RegExp(`\\b${id}\\b`);
  let writes = 0, reads = [];
  base.forEach((l, i) => {
    if (!re.test(l)) return;
    const t = l.trim();
    // a write is: "var <type> id = ..." declaration, or "id := ..." assignment, or the function definition itself
    const isDecl = new RegExp(`^var\\s+\\w+\\s+${id}\\s*=`).test(t);
    const isAssign = new RegExp(`^${id}\\s*:=`).test(t);
    const isDef = new RegExp(`^${id}\\s*\\(`).test(t);
    if (isDecl || isAssign || isDef) writes++;
    else reads.push(`      line ${i + 1}: ${t.slice(0, 110)}`);
  });
  console.log(`  ${id.padEnd(12)} writes/defs: ${String(writes).padStart(2)}   READS: ${reads.length}`);
  reads.forEach(r => console.log(r));
}

console.log('\n=== In OPT: any surviving reference to a removed identifier? ===');
let dangling = 0;
for (const id of ids) {
  const re = new RegExp(`\\b${id}\\b`);
  opt.forEach((l, i) => { if (re.test(l)) { console.log(`  !! ${id} still at OPT line ${i + 1}: ${l.trim().slice(0,110)}`); dangling++; } });
}
console.log(dangling === 0 ? '  none — clean' : `  ${dangling} DANGLING REFERENCES`);

// Undefined-identifier scan: every identifier assigned with := in OPT must be declared somewhere in OPT
console.log('\n=== OPT: assigned-but-never-declared scan ===');
const declared = new Set();
const declRe = /^\s*(?:var\s+)?(?:\w+(?:<[^>]*>)?\s+)?([A-Za-z_]\w*)\s*(?::=|=)/;
opt.forEach(l => { const m = l.match(declRe); if (m) declared.add(m[1]); });
opt.forEach(l => { const m = l.match(/^\s*\[([^\]]+)\]\s*=/); if (m) m[1].split(',').forEach(v => declared.add(v.trim())); });
const undef = new Set();
opt.forEach((l, i) => {
  const m = l.match(/^\s*([A-Za-z_]\w*)\s*:=/);
  if (m && !declared.has(m[1])) undef.add(`${m[1]} (line ${i + 1})`);
});
console.log(undef.size === 0 ? '  none — every := target is declared' : '  ' + [...undef].join('\n  '));
