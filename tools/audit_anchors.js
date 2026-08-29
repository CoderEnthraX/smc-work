// Anchor audit — ask 3, "make it mark the right anchor point".
//
// A mark is drawn as line.new(anchorBar, price, breakBar, price). For that line
// to sit on the swing a trader sees, the ANCHOR BAR must actually have traded
// the marked PRICE: a ceiling mark's anchor bar must have that high, a floor
// mark's anchor bar must have that low.
//
// Any mark failing that is drawn at a price its own anchor candle never
// reached, which is exactly the "the mark is not on the swing I see" report.

'use strict';
const { ChartEngine } = require('./engine.js');

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function series(seed, n) {
  const rnd = mulberry32(seed);
  const out = []; let px = 100, drift = 0;
  for (let i = 0; i < n; i++) {
    if (i % 35 === 0) drift = (rnd() - 0.5) * 0.4;
    const o = px, c = o + (rnd() - 0.5) * 1.7 + drift, w = rnd() * 1.1 + 0.05;
    out.push({ i, o: +o.toFixed(4),
               h: +(Math.max(o, c) + w * rnd()).toFixed(4),
               l: +(Math.min(o, c) - w * rnd()).toFixed(4),
               c: +c.toFixed(4) });
    px = c;
  }
  return out;
}

const RUNS = +(process.argv[2] || 2000);
const N = +(process.argv[3] || 400);

const stats = {};
const samples = [];
let totalMarks = 0;

for (let s = 1; s <= RUNS; s++) {
  const bars = series(s, N);
  const e = new ChartEngine();
  for (const b of bars) e.step(b);
  for (const m of e.marks) {
    totalMarks++;
    const key = m.tier + ' ' + m.kind;
    stats[key] = stats[key] || { n: 0, offAnchor: 0, notBefore: 0, explained: 0 };
    stats[key].n++;

    // is the marked price actually present on the anchor bar?
    const ab = bars[m.anchor];
    const isCeil = m.dir === 'up';       // an up-break breaks a CEILING
    const onBar = ab && (isCeil ? ab.h === m.price : ab.l === m.price);
    if (!onBar) {
      stats[key].offAnchor++;
      // hypothesis: the anchor is a PROMOTED level, so the price came from the
      // sweep bar rather than from the anchor bar.
      const pb = m.priceBar;
      const pbBar = pb !== undefined && pb !== null ? bars[pb] : null;
      const explained = pbBar && (isCeil ? pbBar.h === m.price : pbBar.l === m.price) && pb !== m.anchor;
      stats[key].explained = (stats[key].explained || 0) + (explained ? 1 : 0);
      if (samples.length < 12) {
        samples.push({
          seed: s, tier: m.tier, kind: m.kind, dir: m.dir,
          price: m.price, anchor: m.anchor, breakBar: m.breakBar,
          anchorBar: ab ? { h: ab.h, l: ab.l } : null,
          // where DOES that price live?
          foundAt: bars.findIndex(b => (isCeil ? b.h : b.l) === m.price),
        });
      }
    }
    if (!(m.anchor < m.breakBar)) stats[key].notBefore++;
  }
}

// ---- after P1/P2: the DRAW bar is what the line starts from. Every mark must
// ---- now begin on a bar that actually traded the marked price.
{
  let n = 0, bad = 0;
  const badBy = {};
  for (let s = 1; s <= RUNS; s++) {
    const bars = series(s, N);
    const e = new ChartEngine();
    for (const b of bars) e.step(b);
    for (const m of e.marks) {
      n++;
      const isCeil = m.dir === 'up';
      const db = m.priceBar;
      const dbBar = db !== undefined && db !== null ? bars[db] : null;
      const ok = dbBar && (isCeil ? dbBar.h === m.price : dbBar.l === m.price);
      if (!ok) { bad++; const k = m.tier + ' ' + m.kind; badBy[k] = (badBy[k] || 0) + 1; }
    }
  }
  console.log(`AFTER THE FIX - marks whose DRAW bar lacks the marked price: ${bad}/${n}` +
              (bad ? '  ' + JSON.stringify(badBy) : '  (none)'));
  console.log();
}

console.log(`marks audited: ${totalMarks} over ${RUNS} series x ${N} bars\n`);
console.log('  tier / kind          count   anchor bar lacks the marked price   anchor not before break');
for (const k of Object.keys(stats).sort()) {
  const v = stats[k];
  console.log(`  ${k.padEnd(20)} ${String(v.n).padStart(6)}   ` +
              `${String(v.offAnchor).padStart(10)} (${(100 * v.offAnchor / v.n).toFixed(1)}%)` +
              `${String(v.notBefore).padStart(18)}` +
              `     explained by a promotion: ${v.explained}/${v.offAnchor}`);
}
if (samples.length) {
  console.log('\nsamples where the anchor bar never traded the marked price:');
  samples.forEach(s => console.log('  ' + JSON.stringify(s)));
}
