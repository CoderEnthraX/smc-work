// Faithful Node port of the v15.15 chart engine and of f_tfPack's per-timeframe
// engine, so the two can be run over identical bars and compared.
//
// Ported from current/Market_Structure_SMC_v15.15_OPT.txt. Bars are
// {o,h,l,c} and bar_index is the array position, exactly as Pine sees them.

'use strict';

// ─── Module 1: the 3-candle pullback rule ────────────────────────────────────
class SwingTracker {
  constructor(isHigh) {
    this.isHigh = isHigh;
    this.potential = null;
    this.potentialBar = null;
    this.count = 0;
    this.refLevel = null;
  }
  // method update(SwingTracker t)
  update(b) {
    let confP = null, confB = null;
    const bearC = b.c < b.o, bullC = b.c > b.o;
    const pb = this.isHigh ? bearC : bullC;
    const newExt = this.potential === null ||
      (this.isHigh ? b.h >= this.potential : b.l <= this.potential);
    if (newExt) {
      this.potential = this.isHigh ? b.h : b.l;
      this.potentialBar = b.i;
      this.count = pb ? 1 : 0;
      this.refLevel = pb ? (this.isHigh ? b.l : b.h) : null;
    } else if (pb) {
      if (this.count === 0) {
        this.count = 1;
        this.refLevel = this.isHigh ? b.l : b.h;
      } else if (this.count === 1 &&
                 (this.isHigh ? b.c < this.refLevel : b.c > this.refLevel)) {
        this.count = 2;
        this.refLevel = this.isHigh ? b.l : b.h;
      } else if (this.count === 2 &&
                 (this.isHigh ? b.c < this.refLevel : b.c > this.refLevel)) {
        confP = this.potential;
        confB = this.potentialBar;
        this.potential = this.isHigh ? b.h : b.l;
        this.potentialBar = b.i;
        this.count = 1;
        this.refLevel = this.isHigh ? b.l : b.h;
      }
    }
    return [confP, confB];
  }
  armHere(b) {
    this.potential = this.isHigh ? b.h : b.l;
    this.potentialBar = b.i;
    const pb = this.isHigh ? b.c < b.o : b.c > b.o;
    this.count = pb ? 1 : 0;
    this.refLevel = pb ? (this.isHigh ? b.l : b.h) : null;
  }
  // method rearm(t, p, b) — reads the price buffers
  rearm(p, bar, E) {
    this.potential = p;
    this.potentialBar = bar;
    const sz = E.bufHi.length;
    const idx = bar - E.barIndex + sz - 1;
    const ok = bar !== null && idx >= 0 && idx <= sz - 1;
    const dir = ok ? E.bufDir[idx] : 0;
    const pb = this.isHigh ? dir === -1 : dir === 1;
    this.count = pb ? 1 : 0;
    this.refLevel = pb ? (this.isHigh ? E.bufLo[idx] : E.bufHi[idx]) : null;
  }
}

// ─── the retracement-extreme scans ───────────────────────────────────────────
// exclusive of both the pivot candle and the break candle
function retExtreme(E, fromBar, findHigh) {
  const sz = E.bufLo.length, jEnd = sz - 1;
  let p = null, b = null;
  if (jEnd > 0) {
    const j0 = Math.max(0, Math.min(fromBar - E.barIndex + sz, jEnd - 1));
    const src = findHigh ? E.bufHi : E.bufLo;
    const base = E.barIndex - sz + 1;
    for (let j = j0; j <= jEnd - 1; j++) {
      const v = src[j];
      if (p === null || (findHigh ? v >= p : v <= p)) { p = v; b = base + j; }
    }
  }
  return [p, b];
}
// identical but scans to jEnd, so the BREAK candle counts (v15.14)
function retExtInc(E, fromBar, findHigh) {
  const sz = E.bufLo.length, jEnd = sz - 1;
  let p = null, b = null;
  if (jEnd >= 0) {
    const j0 = Math.max(0, Math.min(fromBar - E.barIndex + sz, jEnd));
    const src = findHigh ? E.bufHi : E.bufLo;
    const base = E.barIndex - sz + 1;
    for (let j = j0; j <= jEnd; j++) {
      const v = src[j];
      if (p === null || (findHigh ? v >= p : v <= p)) { p = v; b = base + j; }
    }
  }
  return [p, b];
}
function isSwing(E, pb, isHigh, k) {
  const sz = E.bufHi.length;
  const idx = pb - E.barIndex + sz - 1;
  let ok = pb !== null && idx - k >= 0 && idx <= sz - 1;
  if (ok) {
    const p = isHigh ? E.bufHi[idx] : E.bufLo[idx];
    for (let j = 1; j <= k; j++) {
      const v = isHigh ? E.bufHi[idx - j] : E.bufLo[idx - j];
      if (isHigh ? v > p : v < p) ok = false;
    }
  }
  return ok;
}
function lastMinor(E, wantLow, beforeBar) {
  const arrB = wantLow ? E.msLoB : E.msHiB;
  const arrP = wantLow ? E.msLoP : E.msHiP;
  for (let i = arrB.length - 1; i >= 0; i--) {
    if (arrB[i] < beforeBar) return [arrP[i], arrB[i]];
  }
  return [null, null];
}

// ─── the chart engine (v15.15), all three tiers ──────────────────────────────
class ChartEngine {
  constructor(opts = {}) {
    this.inPivK = opts.inPivK || 1;
    this.altMode = !!opts.altMode;
    this.bufHi = []; this.bufLo = []; this.bufDir = [];
    this.msLoB = []; this.msLoP = []; this.msHiB = []; this.msHiP = [];
    this.barIndex = -1;
    this.hiT = new SwingTracker(true);
    this.loT = new SwingTracker(false);
    this.aHiT = new SwingTracker(true);
    this.aLoT = new SwingTracker(false);
    this.huntHi = true; this.huntLo = true;
    this.lastAHiP = null; this.lastALoP = null;
    this.trendDir = 0;
    this.ceilS = null; this.florS = null;   // {x1, price, sid, born, swpP, swpB, refP, idmP, idmHit}
    this.allHi = null; this.allLo = null;
    this.pvHiP = []; this.pvHiB = []; this.pvLoP = []; this.pvLoB = [];
    this.iTrend = 0; this.iAncB = null;
    this.iCeilP = null; this.iCeilB = null; this.iCeilBorn = null;
    this.iCeilSwp = null; this.iCeilSwpB = null; this.iCeilRef = null;
    this.iCeilIdmP = null; this.iCeilIdmHit = false; this.iCeilPriceB = null;
    this.iFlorP = null; this.iFlorB = null; this.iFlorBorn = null;
    this.iFlorSwp = null; this.iFlorSwpB = null; this.iFlorRef = null;
    this.iFlorIdmP = null; this.iFlorIdmHit = false; this.iFlorPriceB = null;
    this.nTrend = 0; this.nAncB = null;
    this.nCeilP = null; this.nCeilB = null; this.nCeilBorn = null;
    this.nCeilSwp = null; this.nCeilSwpB = null; this.nCeilRef = null;
    this.nCeilIdmP = null; this.nCeilIdmHit = false; this.nCeilPriceB = null;
    this.nFlorP = null; this.nFlorB = null; this.nFlorBorn = null;
    this.nFlorSwp = null; this.nFlorSwpB = null; this.nFlorRef = null;
    this.nFlorIdmP = null; this.nFlorIdmHit = false; this.nFlorPriceB = null;
    this.marks = [];       // every mark drawn, for the anchor audit
    this.promotions = [];  // every pivot-2 promotion, for the anchor audit
  }

  mkSLine(p, b, sid, priceBar) {
    return { x1: b, price: p, sid, born: this.barIndex, swpP: null, swpB: null,
             refP: null, idmP: null, idmB: null, idmHit: false,
             priceBar: priceBar === undefined ? b : priceBar };
  }
  armIdm(s) {
    if (!s) return;
    const isCeil = s.sid === 0 || s.sid === 2;
    const [ip, ib] = lastMinor(this, isCeil, s.x1);
    s.idmP = ip; s.idmB = ib; s.idmHit = false;
    if (ip !== null) {
      const [xp] = retExtreme(this, s.x1, !isCeil);
      const takenPast = xp !== null && (isCeil ? xp < ip : xp > ip);
      const takenNow = isCeil ? this.b.l < ip : this.b.h > ip;
      if (takenPast || takenNow) s.idmHit = true;
    }
  }
  intArmIdm(pivB, isCeil) {
    const [ip] = lastMinor(this, isCeil, pivB);
    let hit = false;
    if (ip !== null) {
      const [xp] = retExtreme(this, pivB, !isCeil);
      const takenPast = xp !== null && (isCeil ? xp < ip : xp > ip);
      const takenNow = isCeil ? this.b.l < ip : this.b.h > ip;
      hit = takenPast || takenNow;
    }
    return [ip, hit];
  }

  step(bar) {
    this.barIndex = bar.i;
    this.b = bar;
    const ev = { bosUp: false, bosDn: false, choUp: false, choDn: false,
                 iBosUp: false, iBosDn: false, iChoUp: false, iChoDn: false,
                 nBosUp: false, nBosDn: false, nChoUp: false, nChoDn: false };

    this.bufHi.push(bar.h); this.bufLo.push(bar.l);
    this.bufDir.push(bar.c > bar.o ? 1 : bar.c < bar.o ? -1 : 0);
    this.allHi = this.allHi === null ? bar.h : Math.max(this.allHi, bar.h);
    this.allLo = this.allLo === null ? bar.l : Math.min(this.allLo, bar.l);

    // minor swings, for IDM
    if (bar.i >= 2) {
      const n = this.bufHi.length;
      const l1 = this.bufLo[n - 2], l2 = this.bufLo[n - 3];
      const h1 = this.bufHi[n - 2], h2 = this.bufHi[n - 3];
      if (l1 < l2 && l1 < bar.l) { this.msLoB.push(bar.i - 1); this.msLoP.push(l1); }
      if (h1 > h2 && h1 > bar.h) { this.msHiB.push(bar.i - 1); this.msHiP.push(h1); }
    }

    const [phP, phB] = this.hiT.update(bar);
    const [plP, plB] = this.loT.update(bar);

    // alternating stream
    let aPhP = null, aPhB = null, aPlP = null, aPlB = null;
    if (this.huntHi) { const r = this.aHiT.update(bar); aPhP = r[0]; aPhB = r[1]; }
    if (this.huntLo) { const r = this.aLoT.update(bar); aPlP = r[0]; aPlB = r[1]; }
    if (aPhP !== null) {
      this.huntHi = false; this.huntLo = true; this.lastAHiP = aPhP;
      const [rlp, rlb] = retExtreme(this, aPhB, false);
      const useNow = rlp === null || bar.l <= rlp;
      this.aLoT.rearm(useNow ? bar.l : rlp, useNow ? bar.i : rlb, this);
    }
    if (aPlP !== null) {
      this.huntLo = false; this.huntHi = true; this.lastALoP = aPlP;
      const [rhp, rhb] = retExtreme(this, aPlB, true);
      const useNowH = rhp === null || bar.h >= rhp;
      this.aHiT.rearm(useNowH ? bar.h : rhp, useNowH ? bar.i : rhb, this);
    }
    if (!this.huntHi && this.lastAHiP !== null && bar.h >= this.lastAHiP) {
      this.huntHi = true; this.huntLo = false; this.aHiT.armHere(bar);
    } else if (!this.huntLo && this.lastALoP !== null && bar.l <= this.lastALoP) {
      this.huntLo = true; this.huntHi = false; this.aLoT.armHere(bar);
    }
    if (aPhP !== null) { this.pvHiP.push(aPhP); this.pvHiB.push(aPhB); }
    if (aPlP !== null) { this.pvLoP.push(aPlP); this.pvLoB.push(aPlB); }

    // ── main tier: adopt ──
    if (phP !== null) {
      let cSwept = false, cEq = false;
      if (this.ceilS) { cSwept = this.ceilS.swpP !== null; cEq = phP === this.ceilS.price; }
      const adoptC = this.trendDir === 0
        ? (phP >= this.allHi && !cSwept && !cEq) : this.ceilS === null;
      if (adoptC) {
        this.ceilS = this.mkSLine(phP, phB, this.trendDir === -1 ? 2 : 0);
        this.armIdm(this.ceilS);
      }
    }
    if (plP !== null) {
      let fSwept = false, fEq = false;
      if (this.florS) { fSwept = this.florS.swpP !== null; fEq = plP === this.florS.price; }
      const adoptF = this.trendDir === 0
        ? (plP <= this.allLo && !fSwept && !fEq) : this.florS === null;
      if (adoptF) {
        this.florS = this.mkSLine(plP, plB, this.trendDir === 1 ? 3 : 1);
        this.armIdm(this.florS);
      }
    }
    if (this.ceilS && !this.ceilS.idmHit && this.ceilS.idmP !== null && bar.l < this.ceilS.idmP)
      this.ceilS.idmHit = true;
    if (this.florS && !this.florS.idmHit && this.florS.idmP !== null && bar.h > this.florS.idmP)
      this.florS.idmHit = true;

    // ── main tier: ceiling break / sweep / promotion ──
    if (this.ceilS && bar.i > this.ceilS.born) {
      const s = this.ceilS;
      if (bar.c > s.price && (this.trendDir === -1 || !this.altMode || s.idmHit || s.idmP === null)) {
        const isCho = this.trendDir === -1;
        if (isCho) ev.choUp = true; else ev.bosUp = true;
        this.marks.push({ tier: 'main', kind: isCho ? 'CHOCH' : 'BOS', dir: 'up',
                          price: s.price, anchor: s.x1, breakBar: bar.i,
                          priceBar: s.priceBar });
        const srcC = s.x1;
        const [rpC, rbC] = retExtInc(this, srcC, false);
        if (rpC !== null) { this.florS = this.mkSLine(rpC, rbC, 3); this.armIdm(this.florS); }
        this.trendDir = 1;
        this.ceilS = null;
      } else {
        if (bar.h > s.price) {
          if (s.swpP === null || bar.h > s.swpP) { s.swpP = bar.h; s.swpB = bar.i; }
          if (this.altMode && !s.idmHit && s.idmP !== null && bar.c > s.price && s.swpP !== null) {
            // ALT-mode migration, as patched in v15.16: the scope anchor stays
            // latched on the pivot; only the DRAW bar moves to the sweep.
            const mpC = s.swpP, mbC = s.x1, mdC = s.sid, maC = s.swpB;
            this.ceilS = this.mkSLine(mpC, mbC, mdC, maC);
            this.armIdm(this.ceilS);
          }
        }
        if (this.ceilS && this.ceilS.swpP !== null && this.ceilS.refP === null) {
          const [refPc] = retExtreme(this, this.ceilS.x1, false);
          this.ceilS.refP = refPc;
        }
        const t = this.ceilS;
        if (t && this.trendDir === 1 && t.swpP !== null && t.refP !== null && bar.l < t.refP) {
          const spC = t.swpP, sbC = t.x1, sdC = t.sid;   // v15.15: keep the original anchor
          if (spC !== null) {
            this.promotions.push({ tier: 'main', side: 'ceil', bar: bar.i,
                                   price: spC, anchor: sbC, sweepBar: t.swpB, origAnchor: t.x1 });
            this.ceilS = this.mkSLine(spC, sbC, sdC, t.swpB); this.armIdm(this.ceilS);
          }
        }
      }
    }
    // ── main tier: floor break / sweep / promotion ──
    if (this.florS && bar.i > this.florS.born) {
      const s = this.florS;
      if (bar.c < s.price && (this.trendDir === 1 || !this.altMode || s.idmHit || s.idmP === null)) {
        const isCho = this.trendDir === 1;
        if (isCho) ev.choDn = true; else ev.bosDn = true;
        this.marks.push({ tier: 'main', kind: isCho ? 'CHOCH' : 'BOS', dir: 'dn',
                          price: s.price, anchor: s.x1, breakBar: bar.i,
                          priceBar: s.priceBar });
        const srcF = s.x1;
        const [rpF, rbF] = retExtInc(this, srcF, true);
        if (rpF !== null) { this.ceilS = this.mkSLine(rpF, rbF, 2); this.armIdm(this.ceilS); }
        this.trendDir = -1;
        this.florS = null;
      } else {
        if (bar.l < s.price) {
          if (s.swpP === null || bar.l < s.swpP) { s.swpP = bar.l; s.swpB = bar.i; }
          if (this.altMode && !s.idmHit && s.idmP !== null && bar.c < s.price && s.swpP !== null) {
            const mpF = s.swpP, mbF = s.x1, mdF = s.sid, maF = s.swpB;
            this.florS = this.mkSLine(mpF, mbF, mdF, maF);
            this.armIdm(this.florS);
          }
        }
        if (this.florS && this.florS.swpP !== null && this.florS.refP === null) {
          const [refPf] = retExtreme(this, this.florS.x1, true);
          this.florS.refP = refPf;
        }
        const t = this.florS;
        if (t && this.trendDir === -1 && t.swpP !== null && t.refP !== null && bar.h > t.refP) {
          const spF = t.swpP, sbF = t.x1, sdF = t.sid;
          if (spF !== null) {
            this.promotions.push({ tier: 'main', side: 'flor', bar: bar.i,
                                   price: spF, anchor: sbF, sweepBar: t.swpB, origAnchor: t.x1 });
            this.florS = this.mkSLine(spF, sbF, sdF, t.swpB); this.armIdm(this.florS);
          }
        }
      }
    }

    const mainEvt = ev.bosUp || ev.bosDn || ev.choUp || ev.choDn;

    // ── internal tier ──
    let iAnchor = null;
    if (this.trendDir === 1) { if (this.ceilS) iAnchor = this.ceilS.x1; }
    else if (this.trendDir === -1) { if (this.florS) iAnchor = this.florS.x1; }
    if (mainEvt) {
      this.iTrend = 0; this.iAncB = null;
      this.iCeilP = this.iCeilB = this.iCeilBorn = null;
      this.iCeilSwp = this.iCeilRef = this.iCeilIdmP = null; this.iCeilIdmHit = false;
      this.iFlorP = this.iFlorB = this.iFlorBorn = null;
      this.iFlorSwp = this.iFlorRef = this.iFlorIdmP = null; this.iFlorIdmHit = false;
    }
    if (this.iAncB === null && iAnchor !== null) {
      this.iAncB = iAnchor;
      if (this.iCeilP === null) {
        for (let s = 0; s < this.pvHiB.length; s++) {
          const sb = this.pvHiB[s];
          if (sb > this.iAncB && bar.c < this.pvHiP[s] &&
              (this.inPivK <= 1 || isSwing(this, sb, true, this.inPivK))) {
            this.iCeilP = this.pvHiP[s]; this.iCeilB = sb; this.iCeilBorn = bar.i; this.iCeilPriceB = sb;
            const [p, h] = this.intArmIdm(sb, true);
            this.iCeilIdmP = p; this.iCeilIdmHit = h;
            break;
          }
        }
      }
      if (this.iFlorP === null) {
        for (let s = 0; s < this.pvLoB.length; s++) {
          const sb = this.pvLoB[s];
          if (sb > this.iAncB && bar.c > this.pvLoP[s] &&
              (this.inPivK <= 1 || isSwing(this, sb, false, this.inPivK))) {
            this.iFlorP = this.pvLoP[s]; this.iFlorB = sb; this.iFlorBorn = bar.i; this.iFlorPriceB = sb;
            const [p, h] = this.intArmIdm(sb, false);
            this.iFlorIdmP = p; this.iFlorIdmHit = h;
            break;
          }
        }
      }
    }
    if (!mainEvt && this.iAncB !== null) {
      if (aPhP !== null && aPhB > this.iAncB && bar.c < aPhP &&
          (this.inPivK <= 1 || isSwing(this, aPhB, true, this.inPivK)) && this.iCeilP === null) {
        this.iCeilP = aPhP; this.iCeilB = aPhB; this.iCeilBorn = bar.i; this.iCeilPriceB = aPhB;
        this.iCeilSwp = null; this.iCeilRef = null;
        const [p, h] = this.intArmIdm(aPhB, true);
        this.iCeilIdmP = p; this.iCeilIdmHit = h;
      }
      if (aPlP !== null && aPlB > this.iAncB && bar.c > aPlP &&
          (this.inPivK <= 1 || isSwing(this, aPlB, false, this.inPivK)) && this.iFlorP === null) {
        this.iFlorP = aPlP; this.iFlorB = aPlB; this.iFlorBorn = bar.i; this.iFlorPriceB = aPlB;
        this.iFlorSwp = null; this.iFlorRef = null;
        const [p, h] = this.intArmIdm(aPlB, false);
        this.iFlorIdmP = p; this.iFlorIdmHit = h;
      }
      if (this.iCeilP !== null && !this.iCeilIdmHit && this.iCeilIdmP !== null && bar.l < this.iCeilIdmP)
        this.iCeilIdmHit = true;
      if (this.iFlorP !== null && !this.iFlorIdmHit && this.iFlorIdmP !== null && bar.h > this.iFlorIdmP)
        this.iFlorIdmHit = true;

      if (this.iCeilP !== null && this.iCeilBorn !== null && bar.i > this.iCeilBorn) {
        if (bar.c > this.iCeilP) {
          const isChoU = this.iTrend !== 1;
          if (isChoU) ev.iChoUp = true; else ev.iBosUp = true;
          this.marks.push({ tier: 'int', kind: isChoU ? 'iCHOCH' : 'iBOS', dir: 'up',
                            price: this.iCeilP, anchor: this.iCeilB, breakBar: bar.i, priceBar: this.iCeilPriceB });
          const [iRpU, iRbU] = retExtInc(this, this.iCeilB, false);
          if (iRpU !== null) {
            this.iFlorP = iRpU; this.iFlorB = iRbU; this.iFlorBorn = bar.i; this.iFlorPriceB = iRbU;
            this.iFlorSwp = null; this.iFlorRef = null;
            const [p, h] = this.intArmIdm(iRbU, false);
            this.iFlorIdmP = p; this.iFlorIdmHit = h;
          }
          this.iTrend = 1;
          this.iCeilP = this.iCeilB = this.iCeilBorn = null;
          this.iCeilSwp = this.iCeilRef = this.iCeilIdmP = null; this.iCeilIdmHit = false;
        } else {
          if (bar.h > this.iCeilP) {
            if (this.iCeilRef === null) {
              const [r] = retExtreme(this, this.iCeilB, false); this.iCeilRef = r;
            }
            if (this.iCeilSwp === null || bar.h > this.iCeilSwp) { this.iCeilSwp = bar.h; this.iCeilSwpB = bar.i; }
          }
          if (this.iTrend === 1 && this.iCeilSwp !== null && this.iCeilRef !== null &&
              bar.l < this.iCeilRef) {
            const ipC = this.iCeilSwp, ibC = this.iCeilB;   // v15.15: original anchor kept
            if (ipC !== null) {
              this.promotions.push({ tier: 'int', side: 'ceil', bar: bar.i,
                                     price: ipC, anchor: ibC, origAnchor: this.iCeilB });
              this.iCeilP = ipC; this.iCeilB = ibC; this.iCeilBorn = bar.i;
              this.iCeilPriceB = this.iCeilSwpB;
              this.iCeilSwp = null; this.iCeilSwpB = null; this.iCeilRef = null;
              const [p, h] = this.intArmIdm(ibC, true);
              this.iCeilIdmP = p; this.iCeilIdmHit = h;
            }
          }
        }
      }
      if (this.iFlorP !== null && this.iFlorBorn !== null && bar.i > this.iFlorBorn) {
        if (bar.c < this.iFlorP) {
          const isChoD = this.iTrend !== -1;
          if (isChoD) ev.iChoDn = true; else ev.iBosDn = true;
          this.marks.push({ tier: 'int', kind: isChoD ? 'iCHOCH' : 'iBOS', dir: 'dn',
                            price: this.iFlorP, anchor: this.iFlorB, breakBar: bar.i, priceBar: this.iFlorPriceB });
          const [iRpD, iRbD] = retExtInc(this, this.iFlorB, true);
          if (iRpD !== null) {
            this.iCeilP = iRpD; this.iCeilB = iRbD; this.iCeilBorn = bar.i; this.iCeilPriceB = iRbD;
            this.iCeilSwp = null; this.iCeilRef = null;
            const [p, h] = this.intArmIdm(iRbD, true);
            this.iCeilIdmP = p; this.iCeilIdmHit = h;
          }
          this.iTrend = -1;
          this.iFlorP = this.iFlorB = this.iFlorBorn = null;
          this.iFlorSwp = this.iFlorRef = this.iFlorIdmP = null; this.iFlorIdmHit = false;
        } else {
          if (bar.l < this.iFlorP) {
            if (this.iFlorRef === null) {
              const [r] = retExtreme(this, this.iFlorB, true); this.iFlorRef = r;
            }
            if (this.iFlorSwp === null || bar.l < this.iFlorSwp) { this.iFlorSwp = bar.l; this.iFlorSwpB = bar.i; }
          }
          if (this.iTrend === -1 && this.iFlorSwp !== null && this.iFlorRef !== null &&
              bar.h > this.iFlorRef) {
            const ipF = this.iFlorSwp, ibF = this.iFlorB;
            if (ipF !== null) {
              this.promotions.push({ tier: 'int', side: 'flor', bar: bar.i,
                                     price: ipF, anchor: ibF, origAnchor: this.iFlorB });
              this.iFlorP = ipF; this.iFlorB = ibF; this.iFlorBorn = bar.i;
              this.iFlorPriceB = this.iFlorSwpB;
              this.iFlorSwp = null; this.iFlorSwpB = null; this.iFlorRef = null;
              const [p, h] = this.intArmIdm(ibF, false);
              this.iFlorIdmP = p; this.iFlorIdmHit = h;
            }
          }
        }
      }
    }

    const intEvt = ev.iBosUp || ev.iBosDn || ev.iChoUp || ev.iChoDn;

    // ── inner tier ──
    let nAnchor = null;
    if (this.iTrend === 1) { if (this.iCeilB !== null) nAnchor = this.iCeilB; }
    else if (this.iTrend === -1) { if (this.iFlorB !== null) nAnchor = this.iFlorB; }
    if (mainEvt || intEvt) {
      this.nTrend = 0; this.nAncB = null;
      this.nCeilP = this.nCeilB = this.nCeilBorn = null;
      this.nCeilSwp = this.nCeilRef = this.nCeilIdmP = null; this.nCeilIdmHit = false;
      this.nFlorP = this.nFlorB = this.nFlorBorn = null;
      this.nFlorSwp = this.nFlorRef = this.nFlorIdmP = null; this.nFlorIdmHit = false;
    }
    if (this.nAncB === null && nAnchor !== null) {
      this.nAncB = nAnchor;
      if (this.nCeilP === null) {
        for (let s = 0; s < this.pvHiB.length; s++) {
          const nb = this.pvHiB[s];
          if (nb > this.nAncB && bar.c < this.pvHiP[s] &&
              (this.inPivK <= 1 || isSwing(this, nb, true, this.inPivK))) {
            this.nCeilP = this.pvHiP[s]; this.nCeilB = nb; this.nCeilBorn = bar.i; this.nCeilPriceB = nb;
            const [p, h] = this.intArmIdm(nb, true);
            this.nCeilIdmP = p; this.nCeilIdmHit = h; break;
          }
        }
      }
      if (this.nFlorP === null) {
        for (let s = 0; s < this.pvLoB.length; s++) {
          const nb = this.pvLoB[s];
          if (nb > this.nAncB && bar.c > this.pvLoP[s] &&
              (this.inPivK <= 1 || isSwing(this, nb, false, this.inPivK))) {
            this.nFlorP = this.pvLoP[s]; this.nFlorB = nb; this.nFlorBorn = bar.i; this.nFlorPriceB = nb;
            const [p, h] = this.intArmIdm(nb, false);
            this.nFlorIdmP = p; this.nFlorIdmHit = h; break;
          }
        }
      }
    }
    if (!mainEvt && !intEvt && this.nAncB !== null) {
      if (aPhP !== null && aPhB > this.nAncB && bar.c < aPhP &&
          (this.inPivK <= 1 || isSwing(this, aPhB, true, this.inPivK)) && this.nCeilP === null) {
        this.nCeilP = aPhP; this.nCeilB = aPhB; this.nCeilBorn = bar.i; this.nCeilPriceB = aPhB;
        this.nCeilSwp = null; this.nCeilRef = null;
        const [p, h] = this.intArmIdm(aPhB, true);
        this.nCeilIdmP = p; this.nCeilIdmHit = h;
      }
      if (aPlP !== null && aPlB > this.nAncB && bar.c > aPlP &&
          (this.inPivK <= 1 || isSwing(this, aPlB, false, this.inPivK)) && this.nFlorP === null) {
        this.nFlorP = aPlP; this.nFlorB = aPlB; this.nFlorBorn = bar.i; this.nFlorPriceB = aPlB;
        this.nFlorSwp = null; this.nFlorRef = null;
        const [p, h] = this.intArmIdm(aPlB, false);
        this.nFlorIdmP = p; this.nFlorIdmHit = h;
      }
      if (this.nCeilP !== null && !this.nCeilIdmHit && this.nCeilIdmP !== null && bar.l < this.nCeilIdmP)
        this.nCeilIdmHit = true;
      if (this.nFlorP !== null && !this.nFlorIdmHit && this.nFlorIdmP !== null && bar.h > this.nFlorIdmP)
        this.nFlorIdmHit = true;

      if (this.nCeilP !== null && this.nCeilBorn !== null && bar.i > this.nCeilBorn) {
        if (bar.c > this.nCeilP) {
          const isNChoU = this.nTrend !== 1;
          if (isNChoU) ev.nChoUp = true; else ev.nBosUp = true;
          this.marks.push({ tier: 'inner', kind: isNChoU ? 'nCHOCH' : 'nBOS', dir: 'up',
                            price: this.nCeilP, anchor: this.nCeilB, breakBar: bar.i, priceBar: this.nCeilPriceB });
          const [nRpU, nRbU] = retExtInc(this, this.nCeilB, false);
          if (nRpU !== null) {
            this.nFlorP = nRpU; this.nFlorB = nRbU; this.nFlorBorn = bar.i; this.nFlorPriceB = nRbU;
            this.nFlorSwp = null; this.nFlorRef = null;
            const [p, h] = this.intArmIdm(nRbU, false);
            this.nFlorIdmP = p; this.nFlorIdmHit = h;
          }
          this.nTrend = 1;
          this.nCeilP = this.nCeilB = this.nCeilBorn = null;
          this.nCeilSwp = this.nCeilRef = this.nCeilIdmP = null; this.nCeilIdmHit = false;
        } else {
          if (bar.h > this.nCeilP) {
            if (this.nCeilRef === null) { const [r] = retExtreme(this, this.nCeilB, false); this.nCeilRef = r; }
            if (this.nCeilSwp === null || bar.h > this.nCeilSwp) { this.nCeilSwp = bar.h; this.nCeilSwpB = bar.i; }
          }
          if (this.nTrend === 1 && this.nCeilSwp !== null && this.nCeilRef !== null && bar.l < this.nCeilRef) {
            const npC = this.nCeilSwp, nbC = this.nCeilB;
            if (npC !== null) {
              this.promotions.push({ tier: 'inner', side: 'ceil', bar: bar.i,
                                     price: npC, anchor: nbC, origAnchor: this.nCeilB });
              this.nCeilP = npC; this.nCeilB = nbC; this.nCeilBorn = bar.i;
              this.nCeilPriceB = this.nCeilSwpB;
              this.nCeilSwp = null; this.nCeilSwpB = null; this.nCeilRef = null;
              const [p, h] = this.intArmIdm(nbC, true);
              this.nCeilIdmP = p; this.nCeilIdmHit = h;
            }
          }
        }
      }
      if (this.nFlorP !== null && this.nFlorBorn !== null && bar.i > this.nFlorBorn) {
        if (bar.c < this.nFlorP) {
          const isNChoD = this.nTrend !== -1;
          if (isNChoD) ev.nChoDn = true; else ev.nBosDn = true;
          this.marks.push({ tier: 'inner', kind: isNChoD ? 'nCHOCH' : 'nBOS', dir: 'dn',
                            price: this.nFlorP, anchor: this.nFlorB, breakBar: bar.i, priceBar: this.nFlorPriceB });
          const [nRpD, nRbD] = retExtInc(this, this.nFlorB, true);
          if (nRpD !== null) {
            this.nCeilP = nRpD; this.nCeilB = nRbD; this.nCeilBorn = bar.i; this.nCeilPriceB = nRbD;
            this.nCeilSwp = null; this.nCeilRef = null;
            const [p, h] = this.intArmIdm(nRbD, true);
            this.nCeilIdmP = p; this.nCeilIdmHit = h;
          }
          this.nTrend = -1;
          this.nFlorP = this.nFlorB = this.nFlorBorn = null;
          this.nFlorSwp = this.nFlorRef = this.nFlorIdmP = null; this.nFlorIdmHit = false;
        } else {
          if (bar.l < this.nFlorP) {
            if (this.nFlorRef === null) { const [r] = retExtreme(this, this.nFlorB, true); this.nFlorRef = r; }
            if (this.nFlorSwp === null || bar.l < this.nFlorSwp) { this.nFlorSwp = bar.l; this.nFlorSwpB = bar.i; }
          }
          if (this.nTrend === -1 && this.nFlorSwp !== null && this.nFlorRef !== null && bar.h > this.nFlorRef) {
            const npF = this.nFlorSwp, nbF = this.nFlorB;
            if (npF !== null) {
              this.promotions.push({ tier: 'inner', side: 'flor', bar: bar.i,
                                     price: npF, anchor: nbF, origAnchor: this.nFlorB });
              this.nFlorP = npF; this.nFlorB = nbF; this.nFlorBorn = bar.i;
              this.nFlorPriceB = this.nFlorSwpB;
              this.nFlorSwp = null; this.nFlorSwpB = null; this.nFlorRef = null;
              const [p, h] = this.intArmIdm(nbF, false);
              this.nFlorIdmP = p; this.nFlorIdmHit = h;
            }
          }
        }
      }
    }
    return ev;
  }
  readout() { return [this.trendDir, this.iTrend, this.nTrend]; }
}

// ─── f_tfPack's engine, as it stands in v15.15-opt ───────────────────────────
class TfPackEngine {
  constructor() {
    this.tkHi = new SwingTracker(true); this.tkLo = new SwingTracker(false);
    this.tkAH = new SwingTracker(true); this.tkAL = new SwingTracker(false);
    this.tCeil = null; this.tCeilB = null; this.tFlor = null; this.tFlorB = null;
    this.tRunLo = null; this.tRunHi = null; this.tTrend = 0;
    this.tAllHi = null; this.tAllLo = null;
    this.hntH = true; this.hntL = true; this.lHiP = null; this.lLoP = null;
    this.rmLoP = null; this.rmLoB = null; this.rmLoDir = 0; this.rmLoHi = null;
    this.rmHiP = null; this.rmHiB = null; this.rmHiDir = 0; this.rmHiLo = null;
    this.iTr = 0; this.iAnc = null; this.iCe = null; this.iCeB = null;
    this.iFl = null; this.iFlB = null; this.iRLo = null; this.iRHi = null;
    this.qHiP = []; this.qHiB = []; this.qLoP = []; this.qLoB = [];
    this.nTr = 0; this.nAnc = null; this.nCe = null; this.nCeB = null;
    this.nFl = null; this.nFlB = null; this.nRLo = null; this.nRHi = null;
  }
  step(b) {
    this.tAllHi = this.tAllHi === null ? b.h : Math.max(this.tAllHi, b.h);
    this.tAllLo = this.tAllLo === null ? b.l : Math.min(this.tAllLo, b.l);
    this.tRunLo = this.tRunLo === null ? b.l : Math.min(this.tRunLo, b.l);
    this.tRunHi = this.tRunHi === null ? b.h : Math.max(this.tRunHi, b.h);
    if (this.rmLoP === null || b.l <= this.rmLoP) {
      this.rmLoP = b.l; this.rmLoB = b.i;
      this.rmLoDir = b.c > b.o ? 1 : b.c < b.o ? -1 : 0; this.rmLoHi = b.h;
    }
    if (this.rmHiP === null || b.h >= this.rmHiP) {
      this.rmHiP = b.h; this.rmHiB = b.i;
      this.rmHiDir = b.c > b.o ? 1 : b.c < b.o ? -1 : 0; this.rmHiLo = b.l;
    }
    const [cfH] = this.tkHi.update(b);
    const [cfL] = this.tkLo.update(b);
    const hPot0 = this.tkAH.potentialBar, lPot0 = this.tkAL.potentialBar;
    let afH = null, afHb = null, afL = null, afLb = null;
    if (this.hntH) { const r = this.tkAH.update(b); afH = r[0]; afHb = r[1]; }
    if (this.hntL) { const r = this.tkAL.update(b); afL = r[0]; afLb = r[1]; }
    if (afH !== null) {
      this.hntH = false; this.hntL = true; this.lHiP = afH;
      this.tkAL.potential = this.rmLoP; this.tkAL.potentialBar = this.rmLoB;
      const pbL = this.rmLoDir === 1;
      this.tkAL.count = pbL ? 1 : 0;
      this.tkAL.refLevel = pbL ? this.rmLoHi : null;
    }
    if (afL !== null) {
      this.hntL = false; this.hntH = true; this.lLoP = afL;
      this.tkAH.potential = this.rmHiP; this.tkAH.potentialBar = this.rmHiB;
      const pbH = this.rmHiDir === -1;
      this.tkAH.count = pbH ? 1 : 0;
      this.tkAH.refLevel = pbH ? this.rmHiLo : null;
    }
    if (!this.hntH && this.lHiP !== null && b.h >= this.lHiP) {
      this.hntH = true; this.hntL = false; this.tkAH.armHere(b);
    } else if (!this.hntL && this.lLoP !== null && b.l <= this.lLoP) {
      this.hntL = true; this.hntH = false; this.tkAL.armHere(b);
    }
    if (this.tkAH.potentialBar !== hPot0) { this.rmLoP = b.l; this.rmLoB = b.i; }
    if (this.tkAL.potentialBar !== lPot0) { this.rmHiP = b.h; this.rmHiB = b.i; }

    if (cfH !== null) {
      const adoptH = this.tTrend === 0 ? cfH >= this.tAllHi : this.tCeil === null;
      if (adoptH || (this.tCeil !== null && cfH === this.tCeil)) {
        this.tCeil = cfH; this.tCeilB = b.i; this.tRunLo = b.l;
      }
    }
    if (cfL !== null) {
      const adoptL = this.tTrend === 0 ? cfL <= this.tAllLo : this.tFlor === null;
      if (adoptL || (this.tFlor !== null && cfL === this.tFlor)) {
        this.tFlor = cfL; this.tFlorB = b.i; this.tRunHi = b.h;
      }
    }
    let mEvt = false;
    if (this.tCeil !== null && this.tCeilB !== null && b.i > this.tCeilB && b.c > this.tCeil) {
      this.tTrend = 1; mEvt = true;
      this.tFlor = this.tRunLo; this.tFlorB = b.i; this.tRunHi = b.h;
      this.tCeil = null; this.tCeilB = null;
    } else if (this.tFlor !== null && this.tFlorB !== null && b.i > this.tFlorB && b.c < this.tFlor) {
      this.tTrend = -1; mEvt = true;
      this.tCeil = this.tRunHi; this.tCeilB = b.i; this.tRunLo = b.l;
      this.tFlor = null; this.tFlorB = null;
    }
    if (afH !== null) { this.qHiP.push(afH); this.qHiB.push(afHb); }
    if (afL !== null) { this.qLoP.push(afL); this.qLoB.push(afLb); }
    this.iRLo = this.iRLo === null ? b.l : Math.min(this.iRLo, b.l);
    this.iRHi = this.iRHi === null ? b.h : Math.max(this.iRHi, b.h);
    const anc = this.tTrend === 1 ? this.tCeilB : this.tTrend === -1 ? this.tFlorB : null;
    let iEvt = false;
    if (mEvt) { this.iTr = 0; this.iAnc = null; this.iCe = null; this.iCeB = null; this.iFl = null; this.iFlB = null; }
    if (this.iAnc === null && anc !== null && anc !== undefined) {
      this.iAnc = anc;
      if (this.iCe === null) for (let q = 0; q < this.qHiB.length; q++)
        if (this.qHiB[q] > this.iAnc && b.c < this.qHiP[q]) { this.iCe = this.qHiP[q]; this.iCeB = b.i; this.iRLo = b.l; break; }
      if (this.iFl === null) for (let q = 0; q < this.qLoB.length; q++)
        if (this.qLoB[q] > this.iAnc && b.c > this.qLoP[q]) { this.iFl = this.qLoP[q]; this.iFlB = b.i; this.iRHi = b.h; break; }
    }
    if (!mEvt && this.iAnc !== null) {
      if (afH !== null && afHb > this.iAnc && b.c < afH && (this.iCe === null || afH === this.iCe)) {
        this.iCe = afH; this.iCeB = b.i; this.iRLo = b.l;
      }
      if (afL !== null && afLb > this.iAnc && b.c > afL && (this.iFl === null || afL === this.iFl)) {
        this.iFl = afL; this.iFlB = b.i; this.iRHi = b.h;
      }
      if (this.iCe !== null && this.iCeB !== null && b.i > this.iCeB && b.c > this.iCe) {
        this.iTr = 1; iEvt = true; this.iFl = this.iRLo; this.iFlB = b.i; this.iRHi = b.h;
        this.iCe = null; this.iCeB = null;
      } else if (this.iFl !== null && this.iFlB !== null && b.i > this.iFlB && b.c < this.iFl) {
        this.iTr = -1; iEvt = true; this.iCe = this.iRHi; this.iCeB = b.i; this.iRLo = b.l;
        this.iFl = null; this.iFlB = null;
      }
    }
    this.nRLo = this.nRLo === null ? b.l : Math.min(this.nRLo, b.l);
    this.nRHi = this.nRHi === null ? b.h : Math.max(this.nRHi, b.h);
    const nanc = this.iTr === 1 ? this.iCeB : this.iTr === -1 ? this.iFlB : null;
    if (mEvt || iEvt) { this.nTr = 0; this.nAnc = null; this.nCe = null; this.nCeB = null; this.nFl = null; this.nFlB = null; }
    if (this.nAnc === null && nanc !== null && nanc !== undefined) {
      this.nAnc = nanc;
      if (this.nCe === null) for (let q = 0; q < this.qHiB.length; q++)
        if (this.qHiB[q] > this.nAnc && b.c < this.qHiP[q]) { this.nCe = this.qHiP[q]; this.nCeB = b.i; this.nRLo = b.l; break; }
      if (this.nFl === null) for (let q = 0; q < this.qLoB.length; q++)
        if (this.qLoB[q] > this.nAnc && b.c > this.qLoP[q]) { this.nFl = this.qLoP[q]; this.nFlB = b.i; this.nRHi = b.h; break; }
    }
    if (!mEvt && !iEvt && this.nAnc !== null) {
      if (afH !== null && afHb > this.nAnc && b.c < afH && (this.nCe === null || afH === this.nCe)) {
        this.nCe = afH; this.nCeB = b.i; this.nRLo = b.l;
      }
      if (afL !== null && afLb > this.nAnc && b.c > afL && (this.nFl === null || afL === this.nFl)) {
        this.nFl = afL; this.nFlB = b.i; this.nRHi = b.h;
      }
      if (this.nCe !== null && this.nCeB !== null && b.i > this.nCeB && b.c > this.nCe) {
        this.nTr = 1; this.nFl = this.nRLo; this.nFlB = b.i; this.nRHi = b.h; this.nCe = null; this.nCeB = null;
      } else if (this.nFl !== null && this.nFlB !== null && b.i > this.nFlB && b.c < this.nFl) {
        this.nTr = -1; this.nCe = this.nRHi; this.nCeB = b.i; this.nRLo = b.l; this.nFl = null; this.nFlB = null;
      }
    }
  }
  readout() { return [this.tTrend, this.iTr, this.nTr]; }
}

module.exports = { SwingTracker, ChartEngine, TfPackEngine, retExtreme, retExtInc, isSwing, lastMinor };
