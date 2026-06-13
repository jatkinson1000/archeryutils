import { describe, it, expect } from 'vitest';
import {
  newScheme, scoreForRound, handicapFromScore,
  HandicapAGB, HandicapAGBold, HandicapAA, HandicapAA2,
  type Scheme,
} from './handicaps.js';
import { atTarget, type Round } from './rounds.js';
import { ScoringSystem, cm, metres, yards, type FaceSpec, Target } from './targets.js';

// ---- helpers ----

function makeRound(name: string, passes: ReturnType<typeof atTarget>[]): Round {
  return {
    name, codename: name.toLowerCase().replace(/\s+/g, '_'),
    passes, nArrows: passes.reduce((s, p) => s + p.nArrows, 0),
  };
}

const york = makeRound('York', [
  atTarget(72, ScoringSystem.FiveZone, cm(122), { value: 100, units: 'yard' }, false),
  atTarget(48, ScoringSystem.FiveZone, cm(122), { value: 80, units: 'yard' }, false),
  atTarget(24, ScoringSystem.FiveZone, cm(122), { value: 60, units: 'yard' }, false),
]);

const wa720 = makeRound('WA 720 70m', [
  atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), false),
  atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), false),
]);

const wa1440 = makeRound('WA1440 90m', [
  atTarget(36, ScoringSystem.TenZone, cm(122), metres(90), false),
  atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), false),
  atTarget(36, ScoringSystem.TenZone, cm(80), metres(50), false),
  atTarget(36, ScoringSystem.TenZone, cm(80), metres(30), false),
]);

const metric122_30 = makeRound('Metric 122-30', [
  atTarget(36, ScoringSystem.TenZone, cm(122), metres(30), false),
  atTarget(36, ScoringSystem.TenZone, cm(122), metres(30), false),
]);

const western = makeRound('Western', [
  atTarget(48, ScoringSystem.FiveZone, cm(122), { value: 60, units: 'yard' }, false),
  atTarget(48, ScoringSystem.FiveZone, cm(122), { value: 50, units: 'yard' }, false),
]);

const vegas300 = makeRound('Vegas 300', [
  atTarget(30, ScoringSystem.TenZone, cm(40), { value: 20, units: 'yard' }, true),
]);

function makeKings900(): Round {
  const spec: FaceSpec = new Map([[0.08, 10], [0.12, 8], [0.16, 7], [0.20, 6]]);
  const tgt = Target.fromFaceSpec(spec, cm(40), metres(18), true);
  const p = { nArrows: 30, target: tgt };
  return { name: 'Kings 900', codename: 'kings_900', passes: [p, p, p], nArrows: 90 };
}

// ---- newScheme ----

describe('newScheme', () => {
  it('creates AGB scheme with correct name', () => {
    expect(newScheme('AGB').name()).toBe('AGB');
  });
  it('creates AGBold scheme', () => {
    expect(newScheme('AGBold').name()).toBe('AGBold');
  });
  it('creates AA scheme', () => {
    expect(newScheme('AA').name()).toBe('AA');
  });
  it('creates AA2 scheme', () => {
    expect(newScheme('AA2').name()).toBe('AA2');
  });
  it('throws for invalid scheme name', () => {
    expect(() => newScheme('InvalidSystem')).toThrow('Unknown handicap scheme');
  });
});

// ---- sigmaT ----

describe('sigmaT', () => {
  const cases: [string, number, number, number][] = [
    ['AGB',    25.46, 100.0, 0.002125743],
    ['AGBold', 25.46, 100.0, 0.002149455],
    ['AA',     25.46, 100.0, 0.011349271],
    ['AA2',    25.46, 100.0, 0.011011017],
    ['AGB',    -12.0, 100.0, 0.000585929],
    ['AGBold', -12.0, 100.0, 0.000520552],
    ['AA',     -12.0, 100.0, 0.031204851],
    ['AA2',    -12.0, 100.0, 0.030274820],
    ['AGB',    200.0,  10.0, 0.620202925],
    ['AGBold', 200.0,  10.0, 134.960599745],
    ['AA',     200.0,  10.0, 7.111717503e-5],
    ['AA2',    200.0,  10.0, 7.110517486e-5],
  ];
  for (const [name, hc, dist, want] of cases) {
    it(`${name} hc=${hc} dist=${dist}`, () => {
      const s = newScheme(name);
      expect(s.sigmaT(hc, dist)).toBeCloseTo(want, 6);
    });
  }
});

// ---- scoreForRound ----

describe('scoreForRound', () => {
  it('AGB hc=10 wa1440 rounded = 1356', () => {
    expect(scoreForRound(newScheme('AGB'), 10, wa1440, 0, true)).toBe(1356);
  });
  it('AGBold hc=10 wa1440 rounded ≈ 1352', () => {
    expect(scoreForRound(newScheme('AGBold'), 10, wa1440, 0, true)).toBeCloseTo(1352, 0);
  });
  it('AGB hc=20 mixed round = 244', () => {
    const rnd = makeRound('MyRound', [
      atTarget(10, ScoringSystem.TenZone, cm(122), metres(100), false),
      atTarget(10, ScoringSystem.TenZone, cm(80), metres(80), false),
      atTarget(10, ScoringSystem.FiveZone, cm(122), metres(60), false),
    ]);
    expect(scoreForRound(newScheme('AGB'), 20, rnd, 0, true)).toBe(244);
  });
  it('AGBold hc=20 mixed round = 243', () => {
    const rnd = makeRound('MyRound', [
      atTarget(10, ScoringSystem.TenZone, cm(122), metres(100), false),
      atTarget(10, ScoringSystem.TenZone, cm(80), metres(80), false),
      atTarget(10, ScoringSystem.FiveZone, cm(122), metres(60), false),
    ]);
    expect(scoreForRound(newScheme('AGBold'), 20, rnd, 0, true)).toBe(243);
  });
  it('AGB hc=20 kings_900 = 896', () => {
    expect(scoreForRound(newScheme('AGB'), 20, makeKings900(), 0, true)).toBe(896);
  });
});

// ---- handicapFromScore ----

describe('handicapFromScore errors', () => {
  const simpleRound = makeRound('R', [atTarget(10, ScoringSystem.TenZone, cm(122), metres(50), false)]);
  it('throws for score over max', () => {
    expect(() => handicapFromScore(newScheme('AGB'), 9999, simpleRound, 0, true))
      .toThrow('greater than the maximum');
  });
  it('throws for zero score', () => {
    expect(() => handicapFromScore(newScheme('AGB'), 0, simpleRound, 0, true)).toThrow();
  });
  it('throws for negative score', () => {
    expect(() => handicapFromScore(newScheme('AGB'), -100, simpleRound, 0, true)).toThrow();
  });
});

describe('handicapFromScore max score', () => {
  const cases: [string, () => Round, number, number][] = [
    ['AGB',    () => metric122_30, 720, 11],
    ['AA',     () => metric122_30, 720, 107],
    ['AGB',    () => western,      864, 9],
    ['AGBold', () => western,      864, 6],
    ['AGB',    () => vegas300,     300, 3],
    ['AA',     () => vegas300,     300, 119],
  ];
  for (const [scheme, rndFn, maxScore, want] of cases) {
    it(`${scheme} maxScore=${maxScore} → hc≈${want}`, () => {
      const h = handicapFromScore(newScheme(scheme), maxScore, rndFn(), 0, true);
      expect(h).toBeCloseTo(want, 0);
    });
  }
});

describe('handicapFromScore integer precision', () => {
  const cases: [string, () => Round, number, number][] = [
    ['AGB',    () => wa720, 700, 1],
    ['AGBold', () => wa720, 700, 1],
    ['AA',     () => wa720, 700, 119],
    ['AGB',    () => wa720, 500, 44],
    ['AGBold', () => wa720, 500, 40],
    ['AA',     () => wa720, 500, 64],
    ['AGB',    () => wa720, 283, 63],
    ['AGBold', () => wa720, 286, 53],
    ['AA',     () => wa720, 280, 39],
    ['AGB',    () => wa720, 710, -5],
    ['AGBold', () => wa720, 710, -5],
    ['AGB',    () => wa1440, 850, 52],
    ['AGBold', () => wa1440, 850, 46],
    ['AA',     () => wa1440, 850, 53],
  ];
  for (const [scheme, rndFn, score, want] of cases) {
    it(`${scheme} score=${score} → hc≈${want}`, () => {
      const h = handicapFromScore(newScheme(scheme), score, rndFn(), 0, true);
      expect(h).toBeCloseTo(want, 0);
    });
  }
});

describe('handicapFromScore decimal precision', () => {
  const cases: [string, () => Round, number, number][] = [
    ['AGB',    () => wa720,  500, 43.474880980],
    ['AGBold', () => wa720,  500, 39.056931372],
    ['AA',     () => wa720,  500, 64.197993398],
    ['AGB',    () => wa1440, 850, 51.775514610],
    ['AGBold', () => wa1440, 850, 45.303733163],
    ['AA',     () => wa1440, 850, 53.545592683],
  ];
  for (const [scheme, rndFn, score, want] of cases) {
    it(`${scheme} score=${score} decimal → hc≈${want}`, () => {
      const h = handicapFromScore(newScheme(scheme), score, rndFn(), 0, false);
      expect(h).toBeCloseTo(want, 5);
    });
  }
});

describe('handicapFromScore custom scoring', () => {
  it('kings_900 score=896 → hc≈20', () => {
    const h = handicapFromScore(newScheme('AGB'), 896, makeKings900(), 0, true);
    expect(h).toBeCloseTo(20, 0);
  });
});
