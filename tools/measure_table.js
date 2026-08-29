// Measures why the MTF table disagrees with the chart.
//
// Two independent causes are separated here:
//   A. RULE DRIFT   — f_tfPack implements an older rulebook than the chart
//                     engine. Run both over the SAME bars; any disagreement
//                     is ours and is fixable.
//   B. DATA WINDOW  — request.security on a higher timeframe only sees as many
//                     HTF bars as the chart's loaded history yields. Run the
//                     SAME engine over a truncated window; any disagreement is
//                     TradingView's data limit, not the code.

'use strict';
const { ChartEngine, TfPackEngine } = require('./engine.js');
const { TfPackV2 } = require('./tfpack_v2.js');

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// A random walk with trends and the occasional sweep, so structure actually forms.
function series(seed, n) {
  const rnd = mulberry32(seed);
  const bars = [];
  let px = 100, drift = 0;
  for (let i = 0; i < n; i++) {
    if (i % 40 === 0) drift = (rnd() - 0.5) * 0.35;
    const o = px;
    const body = (rnd() - 0.5) * 1.6 + drift;
    const c = o + body;
    const wick = rnd() * 0.9 + 0.05;
    const h = Math.max(o, c) + wick * rnd();
    const l = Math.min(o, c) - wick * rnd();
    bars.push({ i, o: +o.toFixed(5), h: +h.toFixed(5), l: +l.toFixed(5), c: +c.toFixed(5) });
    px = c;
  }
  return bars;
}

const N = +(process.argv[2] || 600);
const RUNS = +(process.argv[3] || 400);

// ── A. rule drift, identical bars ────────────────────────────────────────────
let disTrend = 0, disInt = 0, disInner = 0, anyDis = 0, total = 0;
const examples = [];
for (let s = 1; s <= RUNS; s++) {
  const bars = series(s, N);
  const ce = new ChartEngine(), te = new TfPackEngine();
  for (const b of bars) { ce.step(b); te.step(b); }
  const [ct, ci, cn] = ce.readout();
  const [tt, ti, tn] = te.readout();
  total++;
  const dT = ct !== tt, dI = ci !== ti, dN = cn !== tn;
  if (dT) disTrend++;
  if (dI) disInt++;
  if (dN) disInner++;
  if (dT || dI || dN) {
    anyDis++;
    if (examples.length < 5)
      examples.push(`    seed ${s}: chart [${ct},${ci},${cn}]  table [${tt},${ti},${tn}]`);
  }
}
const pc = x => (100 * x / total).toFixed(1) + '%';
console.log('A. RULE DRIFT — chart engine vs f_tfPack over IDENTICAL bars');
console.log(`   series: ${total} x ${N} bars`);
console.log(`   TREND    column wrong: ${disTrend} (${pc(disTrend)})`);
console.log(`   INTERNAL column wrong: ${disInt} (${pc(disInt)})`);
console.log(`   INNER    column wrong: ${disInner} (${pc(disInner)})`);
console.log(`   at least one wrong:    ${anyDis} (${pc(anyDis)})`);
examples.forEach(e => console.log(e));

// ── A2. the SAME comparison against the REBUILT f_tfPack (v15.16) ───────────
for (const alt of [false, true]) {
  let dT = 0, dI = 0, dN = 0, any = 0, tot = 0;
  const ex = [];
  for (let s = 1; s <= RUNS; s++) {
    const bars = series(s, N);
    const ce = new ChartEngine({ altMode: alt });
    const te = new TfPackV2({ altMode: alt });
    for (const b of bars) { ce.step(b); te.step(b); }
    const c = ce.readout(), t = te.readout();
    tot++;
    if (c[0] !== t[0]) dT++;
    if (c[1] !== t[1]) dI++;
    if (c[2] !== t[2]) dN++;
    if (c[0] !== t[0] || c[1] !== t[1] || c[2] !== t[2]) {
      any++;
      if (ex.length < 3) ex.push(`    seed ${s}: chart [${c}]  table [${t}]`);
    }
  }
  console.log(`\nA2. REBUILT f_tfPack vs chart engine, identical bars, altMode ${alt ? 'ON ' : 'OFF'}`);
  console.log(`   TREND ${dT}   INTERNAL ${dI}   INNER ${dN}   any ${any}/${tot}` +
              (any ? '' : '   -- exact agreement'));
  ex.forEach(e => console.log(e));
}

// ── B. data window, identical rules ──────────────────────────────────────────
// The same chart engine, run over the full series vs over only the last W bars,
// which is what a security() call gets when the chart timeframe is small.
console.log('\nB. DATA WINDOW — same engine, full history vs a truncated window');
for (const W of [40, 80, 150, 300]) {
  let dis = 0, tot = 0;
  for (let s = 1; s <= RUNS; s++) {
    const bars = series(s, N);
    const full = new ChartEngine();
    for (const b of bars) full.step(b);
    const cut = new ChartEngine();
    // re-index so bar_index starts at 0, exactly as a short history behaves
    const tail = bars.slice(-W).map((b, k) => ({ ...b, i: k }));
    for (const b of tail) cut.step(b);
    const a = full.readout(), c = cut.readout();
    tot++;
    if (a[0] !== c[0] || a[1] !== c[1] || a[2] !== c[2]) dis++;
  }
  console.log(`   last ${String(W).padStart(3)} bars only: ${dis}/${tot} disagree (${(100 * dis / tot).toFixed(1)}%)`);
}
