// TfPackV2 — transcribed BACK from the shipped Pine (tools/f_tfPack_v1516.pine),
// not forward from ChartEngine. Round-tripping it this way is what catches a
// transcription error in the Pine that is actually going to TradingView.
//
// Deliberate, behaviour-neutral differences from the chart engine:
//   * no drawing, so no SLine / labels / lines
//   * IDM is computed only when altMode is on. With altMode off, idmP stays na,
//     `na(idmP)` satisfies every break gate and idmHit gates nothing, so IDM
//     cannot affect the trend readout - the only thing the table shows.

'use strict';
const { SwingTracker, retExtreme, retExtInc, isSwing } = require('./engine.js');

// f_retExtB(bH, bL, fromBar, findHigh, incl)
function retExtB(E, fromBar, findHigh, incl) {
  return incl ? retExtInc(E, fromBar, findHigh) : retExtreme(E, fromBar, findHigh);
}
function lastMinorB(arrB, arrP, beforeBar) {
  for (let i = arrB.length - 1; i >= 0; i--)
    if (arrB[i] < beforeBar) return [arrP[i], arrB[i]];
  return [null, null];
}

class TfPackV2 {
  constructor(opts = {}) {
    this.inPivK = opts.inPivK || 1;
    this.altMode = !!opts.altMode;
    this.bufHi = []; this.bufLo = []; this.bufDir = [];   // _bH / _bL / _bD
    this.msLoB = []; this.msLoP = []; this.msHiB = []; this.msHiP = [];
    this.barIndex = -1;
    this.tkHi = new SwingTracker(true); this.tkLo = new SwingTracker(false);
    this.tkAH = new SwingTracker(true); this.tkAL = new SwingTracker(false);
    this.hntH = true; this.hntL = true; this.lHiP = null; this.lLoP = null;
    this.tAllHi = null; this.tAllLo = null;
    this.tTrend = 0; this.mCount = 0;
    this.tCeP = null; this.tCeX = null; this.tCeBorn = null;
    this.tCeSwp = null; this.tCeSwpB = null; this.tCeRef = null;
    this.tCeIdmP = null; this.tCeIdmHit = false;
    this.tFlP = null; this.tFlX = null; this.tFlBorn = null;
    this.tFlSwp = null; this.tFlSwpB = null; this.tFlRef = null;
    this.tFlIdmP = null; this.tFlIdmHit = false;
    this.qHiP = []; this.qHiB = []; this.qLoP = []; this.qLoB = [];
    this.iTr = 0; this.iAncB = null;
    this.iCeP = null; this.iCeB = null; this.iCeBorn = null;
    this.iCeSwp = null; this.iCeRef = null; this.iCeIdmP = null; this.iCeIdmHit = false;
    this.iFlP = null; this.iFlB = null; this.iFlBorn = null;
    this.iFlSwp = null; this.iFlRef = null; this.iFlIdmP = null; this.iFlIdmHit = false;
    this.nTr = 0; this.nAncB = null;
    this.nCeP = null; this.nCeB = null; this.nCeBorn = null;
    this.nCeSwp = null; this.nCeRef = null; this.nCeIdmP = null; this.nCeIdmHit = false;
    this.nFlP = null; this.nFlB = null; this.nFlBorn = null;
    this.nFlSwp = null; this.nFlRef = null; this.nFlIdmP = null; this.nFlIdmHit = false;
  }

  armIdmB(pivB, isCeil) {
    const [ip] = lastMinorB(isCeil ? this.msLoB : this.msHiB,
                            isCeil ? this.msLoP : this.msHiP, pivB);
    let hit = false;
    if (ip !== null) {
      const [xp] = retExtB(this, pivB, !isCeil, false);
      const takenPast = xp !== null && (isCeil ? xp < ip : xp > ip);
      const takenNow = isCeil ? this.b.l < ip : this.b.h > ip;
      hit = takenPast || takenNow;
    }
    return [ip, hit];
  }

  step(bar) {
    this.barIndex = bar.i; this.b = bar;
    const A = this.altMode;

    this.bufHi.push(bar.h); this.bufLo.push(bar.l);
    this.bufDir.push(bar.c > bar.o ? 1 : bar.c < bar.o ? -1 : 0);
    this.tAllHi = this.tAllHi === null ? bar.h : Math.max(this.tAllHi, bar.h);
    this.tAllLo = this.tAllLo === null ? bar.l : Math.min(this.tAllLo, bar.l);

    if (bar.i >= 2) {
      const n = this.bufHi.length;
      const l1 = this.bufLo[n - 2], l2 = this.bufLo[n - 3];
      const h1 = this.bufHi[n - 2], h2 = this.bufHi[n - 3];
      if (l1 < l2 && l1 < bar.l) { this.msLoB.push(bar.i - 1); this.msLoP.push(l1); }
      if (h1 > h2 && h1 > bar.h) { this.msHiB.push(bar.i - 1); this.msHiP.push(h1); }
    }

    const [phP, phB] = this.tkHi.update(bar);
    const [plP, plB] = this.tkLo.update(bar);

    let aPhP = null, aPhB = null, aPlP = null, aPlB = null;
    if (this.hntH) { const r = this.tkAH.update(bar); aPhP = r[0]; aPhB = r[1]; }
    if (this.hntL) { const r = this.tkAL.update(bar); aPlP = r[0]; aPlB = r[1]; }
    if (aPhP !== null) {
      this.hntH = false; this.hntL = true; this.lHiP = aPhP;
      const [rlp, rlb] = retExtB(this, aPhB, false, false);
      const useNow = rlp === null || bar.l <= rlp;
      this.tkAL.rearm(useNow ? bar.l : rlp, useNow ? bar.i : rlb, this);
    }
    if (aPlP !== null) {
      this.hntL = false; this.hntH = true; this.lLoP = aPlP;
      const [rhp, rhb] = retExtB(this, aPlB, true, false);
      const useNowH = rhp === null || bar.h >= rhp;
      this.tkAH.rearm(useNowH ? bar.h : rhp, useNowH ? bar.i : rhb, this);
    }
    if (!this.hntH && this.lHiP !== null && bar.h >= this.lHiP) {
      this.hntH = true; this.hntL = false; this.tkAH.armHere(bar);
    } else if (!this.hntL && this.lLoP !== null && bar.l <= this.lLoP) {
      this.hntL = true; this.hntH = false; this.tkAL.armHere(bar);
    }
    if (aPhP !== null) { this.qHiP.push(aPhP); this.qHiB.push(aPhB); }
    if (aPlP !== null) { this.qLoP.push(aPlP); this.qLoB.push(aPlB); }

    // ── main adopt ──
    if (phP !== null) {
      const cSwept = this.tCeSwp !== null;
      const cEq = this.tCeP !== null && phP === this.tCeP;
      const adoptC = this.tTrend === 0
        ? (phP >= this.tAllHi && !cSwept && !cEq) : this.tCeP === null;
      if (adoptC) {
        this.tCeP = phP; this.tCeX = phB; this.tCeBorn = bar.i;
        this.tCeSwp = null; this.tCeSwpB = null; this.tCeRef = null;
        if (A) { const [p, h] = this.armIdmB(phB, true); this.tCeIdmP = p; this.tCeIdmHit = h; }
      }
    }
    if (plP !== null) {
      const fSwept = this.tFlSwp !== null;
      const fEq = this.tFlP !== null && plP === this.tFlP;
      const adoptF = this.tTrend === 0
        ? (plP <= this.tAllLo && !fSwept && !fEq) : this.tFlP === null;
      if (adoptF) {
        this.tFlP = plP; this.tFlX = plB; this.tFlBorn = bar.i;
        this.tFlSwp = null; this.tFlSwpB = null; this.tFlRef = null;
        if (A) { const [p, h] = this.armIdmB(plB, false); this.tFlIdmP = p; this.tFlIdmHit = h; }
      }
    }
    if (this.tCeP !== null && !this.tCeIdmHit && this.tCeIdmP !== null && bar.l < this.tCeIdmP)
      this.tCeIdmHit = true;
    if (this.tFlP !== null && !this.tFlIdmHit && this.tFlIdmP !== null && bar.h > this.tFlIdmP)
      this.tFlIdmHit = true;

    // ── main ceiling ──
    let mEvt = false;
    if (this.tCeP !== null && this.tCeBorn !== null && bar.i > this.tCeBorn) {
      if (bar.c > this.tCeP && (this.tTrend === -1 || !A || this.tCeIdmHit || this.tCeIdmP === null)) {
        mEvt = true;
        const [rpC, rbC] = retExtB(this, this.tCeX, false, true);
        if (rpC !== null) {
          this.tFlP = rpC; this.tFlX = rbC; this.tFlBorn = bar.i;
          this.tFlSwp = null; this.tFlSwpB = null; this.tFlRef = null;
          if (A) { const [p, h] = this.armIdmB(rbC, false); this.tFlIdmP = p; this.tFlIdmHit = h; }
        }
        this.tTrend = 1;
        this.tCeP = this.tCeX = this.tCeBorn = null;
        this.tCeSwp = this.tCeSwpB = this.tCeRef = this.tCeIdmP = null;
        this.tCeIdmHit = false;
      } else {
        if (bar.h > this.tCeP) {
          if (this.tCeSwp === null || bar.h > this.tCeSwp) { this.tCeSwp = bar.h; this.tCeSwpB = bar.i; }
          if (A && !this.tCeIdmHit && this.tCeIdmP !== null && bar.c > this.tCeP && this.tCeSwp !== null) {
            this.tCeP = this.tCeSwp; this.tCeBorn = bar.i;
            this.tCeSwp = null; this.tCeSwpB = null; this.tCeRef = null;
            const [p, h] = this.armIdmB(this.tCeX, true); this.tCeIdmP = p; this.tCeIdmHit = h;
          }
        }
        if (this.tCeSwp !== null && this.tCeRef === null) {
          const [r] = retExtB(this, this.tCeX, false, false); this.tCeRef = r;
        }
        if (this.tTrend === 1 && this.tCeSwp !== null && this.tCeRef !== null && bar.l < this.tCeRef) {
          this.tCeP = this.tCeSwp; this.tCeBorn = bar.i;
          this.tCeSwp = null; this.tCeSwpB = null; this.tCeRef = null;
          if (A) { const [p, h] = this.armIdmB(this.tCeX, true); this.tCeIdmP = p; this.tCeIdmHit = h; }
        }
      }
    }
    // ── main floor ──
    if (this.tFlP !== null && this.tFlBorn !== null && bar.i > this.tFlBorn) {
      if (bar.c < this.tFlP && (this.tTrend === 1 || !A || this.tFlIdmHit || this.tFlIdmP === null)) {
        mEvt = true;
        const [rpF, rbF] = retExtB(this, this.tFlX, true, true);
        if (rpF !== null) {
          this.tCeP = rpF; this.tCeX = rbF; this.tCeBorn = bar.i;
          this.tCeSwp = null; this.tCeSwpB = null; this.tCeRef = null;
          if (A) { const [p, h] = this.armIdmB(rbF, true); this.tCeIdmP = p; this.tCeIdmHit = h; }
        }
        this.tTrend = -1;
        this.tFlP = this.tFlX = this.tFlBorn = null;
        this.tFlSwp = this.tFlSwpB = this.tFlRef = this.tFlIdmP = null;
        this.tFlIdmHit = false;
      } else {
        if (bar.l < this.tFlP) {
          if (this.tFlSwp === null || bar.l < this.tFlSwp) { this.tFlSwp = bar.l; this.tFlSwpB = bar.i; }
          if (A && !this.tFlIdmHit && this.tFlIdmP !== null && bar.c < this.tFlP && this.tFlSwp !== null) {
            this.tFlP = this.tFlSwp; this.tFlBorn = bar.i;
            this.tFlSwp = null; this.tFlSwpB = null; this.tFlRef = null;
            const [p, h] = this.armIdmB(this.tFlX, false); this.tFlIdmP = p; this.tFlIdmHit = h;
          }
        }
        if (this.tFlSwp !== null && this.tFlRef === null) {
          const [r] = retExtB(this, this.tFlX, true, false); this.tFlRef = r;
        }
        if (this.tTrend === -1 && this.tFlSwp !== null && this.tFlRef !== null && bar.h > this.tFlRef) {
          this.tFlP = this.tFlSwp; this.tFlBorn = bar.i;
          this.tFlSwp = null; this.tFlSwpB = null; this.tFlRef = null;
          if (A) { const [p, h] = this.armIdmB(this.tFlX, false); this.tFlIdmP = p; this.tFlIdmHit = h; }
        }
      }
    }
    if (mEvt) this.mCount++;

    // ── internal ──
    let iAnchor = null;
    if (this.tTrend === 1) { if (this.tCeX !== null) iAnchor = this.tCeX; }
    else if (this.tTrend === -1) { if (this.tFlX !== null) iAnchor = this.tFlX; }
    if (mEvt) {
      this.iTr = 0; this.iAncB = null;
      this.iCeP = this.iCeB = this.iCeBorn = this.iCeSwp = this.iCeRef = this.iCeIdmP = null;
      this.iCeIdmHit = false;
      this.iFlP = this.iFlB = this.iFlBorn = this.iFlSwp = this.iFlRef = this.iFlIdmP = null;
      this.iFlIdmHit = false;
    }
    if (this.iAncB === null && iAnchor !== null) {
      this.iAncB = iAnchor;
      if (this.iCeP === null) for (let s = 0; s < this.qHiB.length; s++) {
        const sb = this.qHiB[s];
        if (sb > this.iAncB && bar.c < this.qHiP[s] && (this.inPivK <= 1 || isSwing(this, sb, true, this.inPivK))) {
          this.iCeP = this.qHiP[s]; this.iCeB = sb; this.iCeBorn = bar.i;
          if (A) { const [p, h] = this.armIdmB(sb, true); this.iCeIdmP = p; this.iCeIdmHit = h; }
          break;
        }
      }
      if (this.iFlP === null) for (let s = 0; s < this.qLoB.length; s++) {
        const sb = this.qLoB[s];
        if (sb > this.iAncB && bar.c > this.qLoP[s] && (this.inPivK <= 1 || isSwing(this, sb, false, this.inPivK))) {
          this.iFlP = this.qLoP[s]; this.iFlB = sb; this.iFlBorn = bar.i;
          if (A) { const [p, h] = this.armIdmB(sb, false); this.iFlIdmP = p; this.iFlIdmHit = h; }
          break;
        }
      }
    }
    let iEvt = false;
    if (!mEvt && this.iAncB !== null) {
      if (aPhP !== null && aPhB > this.iAncB && bar.c < aPhP &&
          (this.inPivK <= 1 || isSwing(this, aPhB, true, this.inPivK)) && this.iCeP === null) {
        this.iCeP = aPhP; this.iCeB = aPhB; this.iCeBorn = bar.i;
        this.iCeSwp = null; this.iCeRef = null;
        if (A) { const [p, h] = this.armIdmB(aPhB, true); this.iCeIdmP = p; this.iCeIdmHit = h; }
      }
      if (aPlP !== null && aPlB > this.iAncB && bar.c > aPlP &&
          (this.inPivK <= 1 || isSwing(this, aPlB, false, this.inPivK)) && this.iFlP === null) {
        this.iFlP = aPlP; this.iFlB = aPlB; this.iFlBorn = bar.i;
        this.iFlSwp = null; this.iFlRef = null;
        if (A) { const [p, h] = this.armIdmB(aPlB, false); this.iFlIdmP = p; this.iFlIdmHit = h; }
      }
      if (this.iCeP !== null && !this.iCeIdmHit && this.iCeIdmP !== null && bar.l < this.iCeIdmP)
        this.iCeIdmHit = true;
      if (this.iFlP !== null && !this.iFlIdmHit && this.iFlIdmP !== null && bar.h > this.iFlIdmP)
        this.iFlIdmHit = true;

      if (this.iCeP !== null && this.iCeBorn !== null && bar.i > this.iCeBorn) {
        if (bar.c > this.iCeP) {
          iEvt = true;
          const [rpU, rbU] = retExtB(this, this.iCeB, false, true);
          if (rpU !== null) {
            this.iFlP = rpU; this.iFlB = rbU; this.iFlBorn = bar.i;
            this.iFlSwp = null; this.iFlRef = null;
            if (A) { const [p, h] = this.armIdmB(rbU, false); this.iFlIdmP = p; this.iFlIdmHit = h; }
          }
          this.iTr = 1;
          this.iCeP = this.iCeB = this.iCeBorn = this.iCeSwp = this.iCeRef = this.iCeIdmP = null;
          this.iCeIdmHit = false;
        } else {
          if (bar.h > this.iCeP) {
            if (this.iCeRef === null) { const [r] = retExtB(this, this.iCeB, false, false); this.iCeRef = r; }
            if (this.iCeSwp === null || bar.h > this.iCeSwp) this.iCeSwp = bar.h;
          }
          if (this.iTr === 1 && this.iCeSwp !== null && this.iCeRef !== null && bar.l < this.iCeRef) {
            this.iCeP = this.iCeSwp; this.iCeBorn = bar.i;
            this.iCeSwp = null; this.iCeRef = null;
            if (A) { const [p, h] = this.armIdmB(this.iCeB, true); this.iCeIdmP = p; this.iCeIdmHit = h; }
          }
        }
      }
      if (this.iFlP !== null && this.iFlBorn !== null && bar.i > this.iFlBorn) {
        if (bar.c < this.iFlP) {
          iEvt = true;
          const [rpD, rbD] = retExtB(this, this.iFlB, true, true);
          if (rpD !== null) {
            this.iCeP = rpD; this.iCeB = rbD; this.iCeBorn = bar.i;
            this.iCeSwp = null; this.iCeRef = null;
            if (A) { const [p, h] = this.armIdmB(rbD, true); this.iCeIdmP = p; this.iCeIdmHit = h; }
          }
          this.iTr = -1;
          this.iFlP = this.iFlB = this.iFlBorn = this.iFlSwp = this.iFlRef = this.iFlIdmP = null;
          this.iFlIdmHit = false;
        } else {
          if (bar.l < this.iFlP) {
            if (this.iFlRef === null) { const [r] = retExtB(this, this.iFlB, true, false); this.iFlRef = r; }
            if (this.iFlSwp === null || bar.l < this.iFlSwp) this.iFlSwp = bar.l;
          }
          if (this.iTr === -1 && this.iFlSwp !== null && this.iFlRef !== null && bar.h > this.iFlRef) {
            this.iFlP = this.iFlSwp; this.iFlBorn = bar.i;
            this.iFlSwp = null; this.iFlRef = null;
            if (A) { const [p, h] = this.armIdmB(this.iFlB, false); this.iFlIdmP = p; this.iFlIdmHit = h; }
          }
        }
      }
    }

    // ── inner ──
    let nAnchor = null;
    if (this.iTr === 1) { if (this.iCeB !== null) nAnchor = this.iCeB; }
    else if (this.iTr === -1) { if (this.iFlB !== null) nAnchor = this.iFlB; }
    if (mEvt || iEvt) {
      this.nTr = 0; this.nAncB = null;
      this.nCeP = this.nCeB = this.nCeBorn = this.nCeSwp = this.nCeRef = this.nCeIdmP = null;
      this.nCeIdmHit = false;
      this.nFlP = this.nFlB = this.nFlBorn = this.nFlSwp = this.nFlRef = this.nFlIdmP = null;
      this.nFlIdmHit = false;
    }
    if (this.nAncB === null && nAnchor !== null) {
      this.nAncB = nAnchor;
      if (this.nCeP === null) for (let s = 0; s < this.qHiB.length; s++) {
        const nb = this.qHiB[s];
        if (nb > this.nAncB && bar.c < this.qHiP[s] && (this.inPivK <= 1 || isSwing(this, nb, true, this.inPivK))) {
          this.nCeP = this.qHiP[s]; this.nCeB = nb; this.nCeBorn = bar.i;
          if (A) { const [p, h] = this.armIdmB(nb, true); this.nCeIdmP = p; this.nCeIdmHit = h; }
          break;
        }
      }
      if (this.nFlP === null) for (let s = 0; s < this.qLoB.length; s++) {
        const nb = this.qLoB[s];
        if (nb > this.nAncB && bar.c > this.qLoP[s] && (this.inPivK <= 1 || isSwing(this, nb, false, this.inPivK))) {
          this.nFlP = this.qLoP[s]; this.nFlB = nb; this.nFlBorn = bar.i;
          if (A) { const [p, h] = this.armIdmB(nb, false); this.nFlIdmP = p; this.nFlIdmHit = h; }
          break;
        }
      }
    }
    if (!mEvt && !iEvt && this.nAncB !== null) {
      if (aPhP !== null && aPhB > this.nAncB && bar.c < aPhP &&
          (this.inPivK <= 1 || isSwing(this, aPhB, true, this.inPivK)) && this.nCeP === null) {
        this.nCeP = aPhP; this.nCeB = aPhB; this.nCeBorn = bar.i;
        this.nCeSwp = null; this.nCeRef = null;
        if (A) { const [p, h] = this.armIdmB(aPhB, true); this.nCeIdmP = p; this.nCeIdmHit = h; }
      }
      if (aPlP !== null && aPlB > this.nAncB && bar.c > aPlP &&
          (this.inPivK <= 1 || isSwing(this, aPlB, false, this.inPivK)) && this.nFlP === null) {
        this.nFlP = aPlP; this.nFlB = aPlB; this.nFlBorn = bar.i;
        this.nFlSwp = null; this.nFlRef = null;
        if (A) { const [p, h] = this.armIdmB(aPlB, false); this.nFlIdmP = p; this.nFlIdmHit = h; }
      }
      if (this.nCeP !== null && !this.nCeIdmHit && this.nCeIdmP !== null && bar.l < this.nCeIdmP)
        this.nCeIdmHit = true;
      if (this.nFlP !== null && !this.nFlIdmHit && this.nFlIdmP !== null && bar.h > this.nFlIdmP)
        this.nFlIdmHit = true;

      if (this.nCeP !== null && this.nCeBorn !== null && bar.i > this.nCeBorn) {
        if (bar.c > this.nCeP) {
          const [rpU, rbU] = retExtB(this, this.nCeB, false, true);
          if (rpU !== null) {
            this.nFlP = rpU; this.nFlB = rbU; this.nFlBorn = bar.i;
            this.nFlSwp = null; this.nFlRef = null;
            if (A) { const [p, h] = this.armIdmB(rbU, false); this.nFlIdmP = p; this.nFlIdmHit = h; }
          }
          this.nTr = 1;
          this.nCeP = this.nCeB = this.nCeBorn = this.nCeSwp = this.nCeRef = this.nCeIdmP = null;
          this.nCeIdmHit = false;
        } else {
          if (bar.h > this.nCeP) {
            if (this.nCeRef === null) { const [r] = retExtB(this, this.nCeB, false, false); this.nCeRef = r; }
            if (this.nCeSwp === null || bar.h > this.nCeSwp) this.nCeSwp = bar.h;
          }
          if (this.nTr === 1 && this.nCeSwp !== null && this.nCeRef !== null && bar.l < this.nCeRef) {
            this.nCeP = this.nCeSwp; this.nCeBorn = bar.i;
            this.nCeSwp = null; this.nCeRef = null;
            if (A) { const [p, h] = this.armIdmB(this.nCeB, true); this.nCeIdmP = p; this.nCeIdmHit = h; }
          }
        }
      }
      if (this.nFlP !== null && this.nFlBorn !== null && bar.i > this.nFlBorn) {
        if (bar.c < this.nFlP) {
          const [rpD, rbD] = retExtB(this, this.nFlB, true, true);
          if (rpD !== null) {
            this.nCeP = rpD; this.nCeB = rbD; this.nCeBorn = bar.i;
            this.nCeSwp = null; this.nCeRef = null;
            if (A) { const [p, h] = this.armIdmB(rbD, true); this.nCeIdmP = p; this.nCeIdmHit = h; }
          }
          this.nTr = -1;
          this.nFlP = this.nFlB = this.nFlBorn = this.nFlSwp = this.nFlRef = this.nFlIdmP = null;
          this.nFlIdmHit = false;
        } else {
          if (bar.l < this.nFlP) {
            if (this.nFlRef === null) { const [r] = retExtB(this, this.nFlB, true, false); this.nFlRef = r; }
            if (this.nFlSwp === null || bar.l < this.nFlSwp) this.nFlSwp = bar.l;
          }
          if (this.nTr === -1 && this.nFlSwp !== null && this.nFlRef !== null && bar.h > this.nFlRef) {
            this.nFlP = this.nFlSwp; this.nFlBorn = bar.i;
            this.nFlSwp = null; this.nFlRef = null;
            if (A) { const [p, h] = this.armIdmB(this.nFlB, false); this.nFlIdmP = p; this.nFlIdmHit = h; }
          }
        }
      }
    }
  }
  readout() { return [this.tTrend, this.iTr, this.nTr]; }
}

module.exports = { TfPackV2 };
