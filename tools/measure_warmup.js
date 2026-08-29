// Is the data-window error curable?
//
// The engine's opening state depends on the first bar it sees: the trendDir==0
// branch adopts against allHi/allLo, the all-time extreme OF THE LOADED WINDOW.
// But every confirmed main event resets the ranges, so the simulation should
// FORGET its start once enough events have gone by.
//
// If that is true, disagreement is a function of how many main events the
// truncated run has produced — not of how many bars it has — and a warm-up
// gate on the event count is a principled fix rather than a fudge.

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
  const bars = [];
  let px = 100, drift = 0;
  for (let i = 0; i < n; i++) {
    if (i % 40 === 0) drift = (rnd() - 0.5) * 0.35;
    const o = px;
    const c = o + (rnd() - 0.5) * 1.6 + drift;
    const wick = rnd() * 0.9 + 0.05;
    bars.push({ i,
      o: +o.toFixed(5),
      h: +(Math.max(o, c) + wick * rnd()).toFixed(5),
      l: +(Math.min(o, c) - wick * rnd()).toFixed(5),
      c: +c.toFixed(5) });
    px = c;
  }
  return bars;
}

function runCounting(bars) {
  const e = new ChartEngine();
  let mainEvents = 0;
  for (const b of bars) {
    const ev = e.step(b);
    if (ev.bosUp || ev.bosDn || ev.choUp || ev.choDn) mainEvents++;
  }
  return { readout: e.readout(), mainEvents };
}

const N = 900, RUNS = 500;
// bucket by how many MAIN events the truncated run saw
const buckets = new Map();
for (let s = 1; s <= RUNS; s++) {
  const bars = series(s, N);
  const truth = runCounting(bars).readout;
  for (const W of [30, 50, 80, 120, 180, 260, 360, 500, 700]) {
    const tail = bars.slice(-W).map((b, k) => ({ ...b, i: k }));
    const r = runCounting(tail);
    const agree = r.readout[0] === truth[0] && r.readout[1] === truth[1] && r.readout[2] === truth[2];
    const key = Math.min(r.mainEvents, 12);
    if (!buckets.has(key)) buckets.set(key, { n: 0, ok: 0 });
    const b = buckets.get(key);
    b.n++; if (agree) b.ok++;
  }
}

console.log('Agreement with full-history truth, bucketed by MAIN EVENTS seen');
console.log('(all three columns must match)\n');
console.log('  main events   samples   agree');
const keys = [...buckets.keys()].sort((a, b) => a - b);
for (const k of keys) {
  const b = buckets.get(k);
  const label = k === 12 ? '12+' : String(k);
  const pct = (100 * b.ok / b.n).toFixed(1);
  const bar = '#'.repeat(Math.round(b.ok / b.n * 40));
  console.log(`  ${label.padStart(11)}   ${String(b.n).padStart(7)}   ${pct.padStart(5)}%  ${bar}`);
}
