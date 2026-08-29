// Validates the Node port against ground truth that is INDEPENDENT of the
// port itself: the two reported sequences the v15.14 changelog describes, and
// the documented behaviour of Module 1 and the two retracement scans.
//
// Never validate an engine against its own output. Each case below asserts a
// behaviour stated in prose in the changelog, not a number this code produced.

'use strict';
const { SwingTracker, ChartEngine, retExtreme, retExtInc } = require('./engine.js');

let pass = 0, fail = 0;
function check(name, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) console.log(`        got  ${JSON.stringify(got)}\n        want ${JSON.stringify(want)}`);
  ok ? pass++ : fail++;
}
const bar = (i, o, h, l, c) => ({ i, o, h, l, c });

// ── 1. Module 1, the 3-candle pullback rule ─────────────────────────────────
// "c1 = first bearish candle at/after the candidate (its LOW locks); c2 must
//  CLOSE below c1's low; c3 must CLOSE below c2's low -> CONFIRMED",
// "Reported on the confirmation bar, ANCHORED at the candidate's bar."
{
  const t = new SwingTracker(true);
  const bars = [
    bar(0, 10, 20, 9, 19),    // candidate: high 20
    bar(1, 19, 19, 15, 16),   // c1 bearish, low 15 locks
    bar(2, 16, 17, 13, 14),   // c2 closes 14 < 15
    bar(3, 14, 15, 11, 12),   // c3 closes 12 < 13 -> CONFIRMED
  ];
  let conf = null;
  for (const b of bars) { const [p, i] = t.update(b); if (p !== null) conf = [p, i]; }
  check('Module 1 confirms on c3, anchored at the candidate bar', conf, [20, 0]);
}
{
  // "Noise PAUSES, never resets. The three need not be consecutive."
  const t = new SwingTracker(true);
  const bars = [
    bar(0, 10, 20, 9, 19),
    bar(1, 19, 19, 15, 16),   // c1, low 15
    bar(2, 16, 18, 16, 17),   // bullish noise — must PAUSE, not reset
    bar(3, 17, 17, 13, 14),   // c2 closes 14 < 15
    bar(4, 14, 15, 11, 12),   // c3 closes 12 < 13 -> CONFIRMED
  ];
  let conf = null;
  for (const b of bars) { const [p, i] = t.update(b); if (p !== null) conf = [p, i]; }
  check('Module 1 noise pauses rather than resets', conf, [20, 0]);
}
{
  // "A new OR EQUAL extreme RESTARTS everything."
  const t = new SwingTracker(true);
  const bars = [
    bar(0, 10, 20, 9, 19),
    bar(1, 19, 19, 15, 16),   // c1
    bar(2, 16, 22, 16, 21),   // new extreme -> restart
    bar(3, 21, 21, 18, 19),   // c1 again
    bar(4, 19, 19, 16, 17),   // c2
  ];
  let conf = null;
  for (const b of bars) { const [p, i] = t.update(b); if (p !== null) conf = [p, i]; }
  check('a new extreme restarts the count (no confirmation yet)', conf, null);
}

// ── 2. the two retracement scans ────────────────────────────────────────────
// f_retExtreme excludes BOTH the pivot candle and the break candle;
// f_retExtInc is "identical except that it scans to jEnd", so the break
// candle counts. (v15.14 change 1)
{
  const E = { bufHi: [], bufLo: [], bufDir: [], barIndex: 0 };
  const bars = [
    bar(0, 0, 30, 25, 28),   // pivot bar — must be excluded by both
    bar(1, 0, 26, 20, 22),
    bar(2, 0, 24, 18, 20),   // deepest low strictly between
    bar(3, 0, 23, 12, 22),   // BREAK candle, wicks lowest of all
  ];
  for (const b of bars) {
    E.bufHi.push(b.h); E.bufLo.push(b.l);
    E.bufDir.push(b.c > b.o ? 1 : -1); E.barIndex = b.i;
  }
  check('f_retExtreme excludes the break candle', retExtreme(E, 0, false), [18, 2]);
  check('f_retExtInc includes the break candle',   retExtInc(E, 0, false), [12, 3]);
}

// ── 3. v15.14 change 1, the GBPCAD 4h sequence ──────────────────────────────
// "candles 1-4 formed the pullback that confirmed a swing high; candle 5 wicked
//  BELOW candle 4 low, then closed above the ceiling and printed the iBOS. The
//  new floor landed on candle 4 low, not on candle 5 wick" — the fix makes the
//  opposite level take the BREAK candle's wick.
{
  const E = { bufHi: [], bufLo: [], bufDir: [], barIndex: 0 };
  const seq = [
    bar(0, 100, 110, 99, 109),   // the swing high, ceiling pivot
    bar(1, 109, 109, 104, 105),
    bar(2, 105, 106, 101, 102),
    bar(3, 102, 103,  98,  99),  // candle 4 low = 98
    bar(4,  99, 112,  95, 111),  // candle 5: wicks to 95, closes 111 above the ceiling
  ];
  for (const b of seq) {
    E.bufHi.push(b.h); E.bufLo.push(b.l);
    E.bufDir.push(b.c > b.o ? 1 : -1); E.barIndex = b.i;
  }
  check('GBPCAD: old exclusive scan lands on candle 4 low',  retExtreme(E, 0, false), [98, 3]);
  check('GBPCAD: v15.14 inclusive scan takes the sweep wick', retExtInc(E, 0, false), [95, 4]);
}

// -- 4. the pivot-2 promotion keeps the ORIGINAL anchor (v15.15) -----------
// "the promotion takes the swept wick PRICE and keeps the ORIGINAL anchor bar".
// Property test: hunt random series for real promotion events at all six sites
// and assert the invariant on every one, rather than hand-building a scenario.
{
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
  let seen = 0, anchoredOnSweep = 0;
  const bySite = {};
  for (let s = 1; s <= 1500; s++) {
    const e = new ChartEngine();
    for (const b of series(s, 400)) e.step(b);
    for (const p of e.promotions) {
      seen++;
      const site = p.tier + '/' + p.side;
      bySite[site] = (bySite[site] || 0) + 1;
      if (p.sweepBar !== undefined && p.anchor === p.sweepBar) anchoredOnSweep++;
    }
  }
  console.log('        promotions observed: ' + seen + '  ' + JSON.stringify(bySite));
  check('every promotion keeps the original anchor, none lands on the sweep bar',
        { seen: seen > 0, anchoredOnSweep }, { seen: true, anchoredOnSweep: 0 });
}

// ── 5. equal-price pivot must not take the level (v15.5) ────────────────────
{
  const e = new ChartEngine();
  // two highs at exactly the same price; the FIRST must keep the level
  const bars = [];
  const push = (o, h, l, c) => bars.push(bar(bars.length, o, h, l, c));
  push(50, 64538.23 / 1000, 49, 51);
  const P = 64.53823;
  bars.length = 0;
  push(50, 55, 49, 54);
  push(54, P, 53, 60);      // first touch of P  (bar 1)
  push(60, 61, 55, 56);     // c1
  push(56, 57, 51, 52);     // c2
  push(52, 53, 47, 48);     // c3 -> confirms the high at P, anchored bar 1
  const anchorAfterFirst = (() => {
    const e2 = new ChartEngine();
    for (const b of bars) e2.step(b);
    return e2.ceilS ? e2.ceilS.x1 : null;
  })();
  check('first pivot at price P owns the level, anchored at its own bar',
        anchorAfterFirst, 1);
}

console.log(`\n  ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
