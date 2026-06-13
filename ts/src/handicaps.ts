import { type FaceSpec } from './targets.js';
import { type Round, roundMaxScore, passMaxScore } from './rounds.js';

// ---- Scheme interface ----

export interface Scheme {
  sigmaT(handicap: number, dist: number): number;
  descending(): boolean;
  scaleBounds(): [number, number];
  maxScoreRoundingLim(): number;
  arrowDiameter(indoor: boolean): number;
  roundScore(score: number): number;
  name(): string;
}

// ---- Concrete schemes ----

export class HandicapAGB implements Scheme {
  private readonly datum = 6.0;
  private readonly step = 3.5;
  private readonly ang0 = 5e-4;
  private readonly kd = 0.00365;

  name() { return 'AGB'; }
  descending() { return true; }
  scaleBounds(): [number, number] { return [-75, 300]; }
  maxScoreRoundingLim() { return 1.0; }
  arrowDiameter(indoor: boolean) { return indoor ? 9.3e-3 : 5.5e-3; }
  roundScore(score: number) { return Math.ceil(score); }

  sigmaT(handicap: number, _dist: number): number {
    return this.ang0 * Math.pow(1.0 + this.step / 100.0, handicap + this.datum) * Math.exp(this.kd * _dist);
  }
}

export class HandicapAGBold implements Scheme {
  private readonly datum = 12.9;
  private readonly step = 3.6;
  private readonly ang0 = 5e-4;
  private readonly k1 = 1.429e-6;
  private readonly k2 = 1.07;
  private readonly k3 = 4.3;
  private readonly p1 = 2.0;

  name() { return 'AGBold'; }
  descending() { return true; }
  scaleBounds(): [number, number] { return [-75, 300]; }
  maxScoreRoundingLim() { return 0.5; }
  arrowDiameter(_indoor: boolean) { return 7.14e-3; }
  roundScore(score: number) { return Math.round(score); }

  sigmaT(handicap: number, dist: number): number {
    const kFactor = this.k1 * Math.pow(this.k2, handicap + this.k3);
    const fFactor = 1.0 + kFactor * Math.pow(dist, this.p1);
    return this.ang0 * Math.pow(1.0 + this.step / 100.0, handicap + this.datum) * fFactor;
  }
}

export class HandicapAA implements Scheme {
  private readonly ang0 = 1e-3;
  private readonly k0 = 2.37;
  private readonly ks = 0.027;
  private readonly kd = 0.004;

  name() { return 'AA'; }
  descending() { return false; }
  scaleBounds(): [number, number] { return [-250, 175]; }
  maxScoreRoundingLim() { return 0.5; }
  arrowDiameter(indoor: boolean) { return indoor ? 9.3e-3 : 5.0e-3; }
  roundScore(score: number) { return Math.round(score); }

  sigmaT(handicap: number, dist: number): number {
    return Math.SQRT2 * this.ang0 * Math.exp(this.k0 - this.ks * handicap + this.kd * dist);
  }
}

export class HandicapAA2 implements Scheme {
  private readonly ang0 = 1e-3;
  private readonly k0 = 2.57;
  private readonly ks = 0.027;
  private readonly f1 = 0.815;
  private readonly f2 = 0.185;
  private readonly d0 = 50.0;

  name() { return 'AA2'; }
  descending() { return false; }
  scaleBounds(): [number, number] { return [-250, 175]; }
  maxScoreRoundingLim() { return 0.5; }
  arrowDiameter(indoor: boolean) { return indoor ? 9.3e-3 : 5.0e-3; }
  roundScore(score: number) { return Math.round(score); }

  sigmaT(handicap: number, _dist: number): number {
    return Math.SQRT2 * this.ang0 * Math.exp(this.k0 - this.ks * handicap) * (this.f1 + this.f2 * _dist / this.d0);
  }
}

export function newScheme(name: string): Scheme {
  switch (name) {
    case 'AGB':    return new HandicapAGB();
    case 'AGBold': return new HandicapAGBold();
    case 'AA':     return new HandicapAA();
    case 'AA2':    return new HandicapAA2();
    default: throw new Error(`Unknown handicap scheme "${name}". Valid: AGB, AGBold, AA, AA2`);
  }
}

// ---- Core math ----

export function sigmaR(s: Scheme, handicap: number, dist: number): number {
  return dist * s.sigmaT(handicap, dist);
}

function arrowDiam(s: Scheme, indoor: boolean, arwD: number): number {
  return arwD > 0 ? arwD : s.arrowDiameter(indoor);
}

function sBar(spec: FaceSpec, arwRad: number, sigR: number): number {
  const keys = [...spec.keys()].sort((a, b) => a - b);
  const ringScores = keys.map(k => spec.get(k)!);
  ringScores.push(0);
  const maxScore = ringScores[0];
  let total = 0;
  for (let i = 0; i < keys.length; i++) {
    const scoreDrop = ringScores[i] - ringScores[i + 1];
    const ratio = (arwRad + keys[i] / 2) / sigR;
    total += scoreDrop * Math.exp(-(ratio * ratio));
  }
  return maxScore - total;
}

export function arrowScore(s: Scheme, handicap: number, target: import('./targets.js').Target, arwD: number): number {
  const d = arrowDiam(s, target.indoor, arwD);
  const sr = sigmaR(s, handicap, target.distance);
  return sBar(target.faceSpec, d / 2, sr);
}

export function scoreForPassRaw(s: Scheme, handicap: number, pass: import('./rounds.js').Pass, arwD: number): number {
  return pass.nArrows * arrowScore(s, handicap, pass.target, arwD);
}

export function scoreForRound(s: Scheme, handicap: number, rnd: Round, arwD: number, rounded: boolean): number {
  let total = 0;
  for (const p of rnd.passes) total += scoreForPassRaw(s, handicap, p, arwD);
  return rounded ? s.roundScore(total) : total;
}

export function scoreForPasses(s: Scheme, handicap: number, rnd: Round, arwD: number, rounded: boolean): number[] {
  return rnd.passes.map(p => {
    const raw = scoreForPassRaw(s, handicap, p, arwD);
    return rounded ? s.roundScore(raw) : raw;
  });
}

export function handicapFromScore(s: Scheme, score: number, rnd: Round, arwD: number, intPrec: boolean): number {
  const maxScore = roundMaxScore(rnd);
  if (score > maxScore) {
    throw new Error(
      `The score of ${score} provided is greater than the maximum of ${maxScore} for a ${rnd.name}.`
    );
  }
  if (score <= 0) {
    throw new Error(
      `The score of ${score} provided is less than or equal to zero so cannot have a handicap.`
    );
  }

  if (score === maxScore) {
    return getMaxScoreHandicap(s, rnd, arwD, intPrec);
  }

  let handicap = rootfindScoreHandicap(s, score, rnd, arwD);

  if (intPrec) {
    if (s.descending()) {
      handicap = Math.ceil(handicap);
    } else {
      handicap = Math.floor(handicap);
    }
    const hstep = s.descending() ? 1 : -1;
    while (true) {
      handicap += hstep;
      const sc = scoreForRound(s, handicap, rnd, arwD, true);
      if (sc < score) { handicap -= hstep; break; }
    }
  }
  return handicap;
}

function getMaxScoreHandicap(s: Scheme, rnd: Round, arwD: number, intPrec: boolean): number {
  const maxScore = roundMaxScore(rnd);
  const [lo, hi] = s.scaleBounds();
  const target = maxScore - s.maxScoreRoundingLim();

  let handicap: number;
  let deltaHC: number;
  if (s.descending()) {
    handicap = lo; deltaHC = 1.0;
  } else {
    handicap = hi; deltaHC = -1.0;
  }

  while (scoreForRound(s, handicap, rnd, arwD, false) > target) handicap += deltaHC;
  handicap -= 1.01 * deltaHC;
  deltaHC /= 100;
  while (scoreForRound(s, handicap, rnd, arwD, false) > target) handicap += deltaHC;
  handicap -= deltaHC;

  if (intPrec) {
    return s.descending() ? Math.floor(handicap) : Math.ceil(handicap);
  }
  return handicap;
}

function sign(x: number): number {
  if (x < 0) return -1;
  if (x > 0) return 1;
  return 0;
}

function rootfindScoreHandicap(s: Scheme, score: number, rnd: Round, arwD: number): number {
  const [lo, hi] = s.scaleBounds();
  const fRoot = (hc: number) => scoreForRound(s, hc, rnd, arwD, false) - score;

  const f0 = fRoot(lo);
  const f1 = fRoot(hi);
  const XTOL = 1e-16;

  let xpre: number, xcur: number, fpre: number, fcur: number;
  if (Math.abs(f1) <= Math.abs(f0)) {
    [xcur, xpre] = [hi, lo];
    [fcur, fpre] = [f1, f0];
  } else {
    [xpre, xcur] = [hi, lo];
    [fpre, fcur] = [f1, f0];
  }

  let xblk = 0, fblk = 0, scur = 0, spre = 0;
  let handicap = xcur;

  for (let iter = 0; iter < 25; iter++) {
    if (fpre !== 0 && fcur !== 0 && sign(fpre) !== sign(fcur)) {
      xblk = xpre; fblk = fpre;
      spre = xcur - xpre;
      scur = xcur - xpre;
    }
    if (Math.abs(fblk) < Math.abs(fcur)) {
      [xpre, xcur, xblk] = [xcur, xblk, xcur];
      [fpre, fcur, fblk] = [fcur, fblk, fcur];
    }
    const delta = (XTOL + 0.0 * Math.abs(xcur)) / 2.0;
    const sbis = (xblk - xcur) / 2.0;

    if (fcur === 0 || Math.abs(sbis) < delta) { handicap = xcur; break; }

    if (Math.abs(spre) > delta && Math.abs(fcur) < Math.abs(fpre)) {
      let stry: number;
      if (xpre === xblk) {
        const denom = fcur - xpre; // note: same as Go — likely fpre typo but kept faithful
        stry = -fcur * (xcur - xpre) / (denom === 0 ? XTOL : denom);
      } else {
        const dpre = (fpre - fcur) / (xpre - xcur);
        const dblk = (fblk - fcur) / (xblk - xcur);
        stry = -fcur * (fblk - fpre) / (fblk * dpre - fpre * dblk);
      }
      if (2 * Math.abs(stry) < Math.min(Math.abs(spre), 3 * Math.abs(sbis) - delta)) {
        spre = scur; scur = stry;
      } else {
        spre = sbis; scur = sbis;
      }
    } else {
      spre = sbis; scur = sbis;
    }

    xpre = xcur; fpre = fcur;
    if (Math.abs(scur) > delta) xcur += scur;
    else if (sbis > 0) xcur += delta;
    else xcur -= delta;

    fcur = fRoot(xcur);
    handicap = xcur;
  }
  return handicap;
}
