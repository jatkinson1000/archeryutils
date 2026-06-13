import { describe, it, expect } from 'vitest';
import {
  outdoorClassificationScores,
  calculateOutdoorClassification,
  coaxOutdoorGroup,
} from './outdoor.js';
import { Gender, Age, Bowstyle } from './data.js';
import { waOutdoorRounds, agbOutdoorImperialRounds, agbOutdoorMetricRounds, atTarget, type Round } from '../rounds.js';
import { ScoringSystem, cm, metres } from '../targets.js';

// ---- helpers ----

function outdoorRound(name: string): Round {
  return (
    waOutdoorRounds().get(name) ??
    agbOutdoorImperialRounds().get(name) ??
    agbOutdoorMetricRounds().get(name)!
  );
}

// ---- outdoorClassificationScores: ages ----

describe('outdoorClassificationScores ages', () => {
  const cases: [string, Age, number[]][] = [
    ['wa1440_90', Age.Adult,   [1320, 1266, 1197, 1110,  999, 866, 717, 566, 426]],
    ['wa720_70',  Age.Adult,   [ 659,  631,  597,  552,  496, 425, 343, 259, 185]],
    ['wa1440_70', Age.Over50,  [1305, 1247, 1173, 1079,  960, 817, 659, 503, 364]],
    ['wa1440_90', Age.Under21, [1270, 1203, 1117, 1008,  877, 728, 577, 435, 313]],
    ['wa1440_70', Age.Under18, [1252, 1179, 1086,  969,  828, 671, 514, 373, 259]],
    ['wa1440_60', Age.Under16, [1241, 1165, 1068,  946,  799, 635, 474, 335, 227]],
    ['metric_iii', Age.Under15, [1261, 1191, 1101,  988,  849, 693, 534, 389, 270]],
    ['metric_iv',  Age.Under14, [1301, 1242, 1166, 1070,  952, 814, 666, 524, 396]],
    ['metric_v',   Age.Under12, [1317, 1263, 1193, 1104,  992, 858, 706, 550, 406]],
  ];
  for (const [roundName, age, want] of cases) {
    it(`${roundName} ${age}`, () => {
      const scores = outdoorClassificationScores(
        outdoorRound(roundName), Bowstyle.Recurve, Gender.Male, age, true, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- outdoorClassificationScores: genders ----

describe('outdoorClassificationScores genders (female)', () => {
  const cases: [string, Age, number[]][] = [
    ['wa1440_70',  Age.Adult,   [1316, 1261, 1191, 1101,  988, 849, 693, 536, 392]],
    ['metric_iii', Age.Under16, [1274, 1207, 1122, 1014,  881, 727, 567, 418, 293]],
    ['metric_iii', Age.Under15, [1261, 1191, 1101,  988,  849, 693, 534, 389, 270]],
    ['metric_v',   Age.Under12, [1317, 1263, 1193, 1104,  992, 858, 706, 550, 406]],
  ];
  for (const [roundName, age, want] of cases) {
    it(`${roundName} female ${age}`, () => {
      const scores = outdoorClassificationScores(
        outdoorRound(roundName), Bowstyle.Recurve, Gender.Female, age, true, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- outdoorClassificationScores: bowstyles ----

describe('outdoorClassificationScores bowstyles', () => {
  const cases: [string, Bowstyle, Gender, number[]][] = [
    ['wa1440_90', Bowstyle.Compound, Gender.Male,   [1389, 1362, 1327, 1283, 1229, 1162, 1081, 982, 866]],
    ['wa1440_70', Bowstyle.Compound, Gender.Female, [1392, 1364, 1330, 1286, 1233, 1167, 1086, 988, 870]],
    ['wa1440_90', Bowstyle.Barebow,  Gender.Male,   [1124, 1042,  945,  835,  717,  598,  484, 380, 290]],
    ['wa1440_70', Bowstyle.Barebow,  Gender.Female, [1108, 1023,  921,  806,  682,  558,  441, 338, 252]],
    ['wa1440_90', Bowstyle.Longbow,  Gender.Male,   [ 825,  696,  566,  445,  337,  248,  177, 124,  85]],
    ['wa1440_70', Bowstyle.Longbow,  Gender.Female, [ 761,  625,  493,  373,  274,  195,  136,  94,  64]],
  ];
  for (const [roundName, bowstyle, gender, want] of cases) {
    it(`${roundName} ${bowstyle} ${gender}`, () => {
      const scores = outdoorClassificationScores(
        outdoorRound(roundName), bowstyle, gender, Age.Adult, true, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- small face ----

describe('outdoorClassificationScores small face', () => {
  it('wa1440_90_small compound same as wa1440_90', () => {
    const want = [1389, 1362, 1327, 1283, 1229, 1162, 1081, 982, 866];
    const scores = outdoorClassificationScores(
      outdoorRound('wa1440_90_small'), Bowstyle.Compound, Gender.Male, Age.Adult, true, true,
    );
    expect(scores).toEqual(want);
  });
});

// ---- non-strict round ----

describe('outdoorClassificationScores non-strict round', () => {
  const cases: [string, Bowstyle, Gender, Age, number[]][] = [
    ['st_george',   Bowstyle.Compound, Gender.Male, Age.Adult,
      [961, 947, 924, 891, 848, 795, 729, 651, 562]],
    ['wa720_70',    Bowstyle.Recurve,  Gender.Male, Age.Adult,
      [-9999, -9999, -9999, -9999, 496, 425, 343, 259, 185]],
    ['wa720_50_c',  Bowstyle.Barebow,  Gender.Male, Age.Adult,
      [-9999, -9999, -9999, -9999, -9999, -9999, 212, 159, 117]],
  ];
  for (const [roundName, bowstyle, gender, age, want] of cases) {
    it(`${roundName} ${bowstyle} non-strict-round`, () => {
      const scores = outdoorClassificationScores(
        outdoorRound(roundName), bowstyle, gender, age, false, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- non-strict distance ----

describe('outdoorClassificationScores non-strict distance', () => {
  const cases: [string, Bowstyle, Gender, Age, number[]][] = [
    ['st_george',  Bowstyle.Compound, Gender.Male, Age.Adult,
      [-9999, -9999, -9999, 891, 848, 795, 729, 651, 562]],
    ['wa720_70',   Bowstyle.Recurve,  Gender.Male, Age.Adult,
      [659, 631, 597, 552, 496, 425, 343, 259, 185]],
    ['wa720_50_c', Bowstyle.Barebow,  Gender.Male, Age.Adult,
      [-9999, -9999, -9999, 406, 341, 274, 212, 159, 117]],
  ];
  for (const [roundName, bowstyle, gender, age, want] of cases) {
    it(`${roundName} ${bowstyle} non-strict-dist`, () => {
      const scores = outdoorClassificationScores(
        outdoorRound(roundName), bowstyle, gender, age, true, false,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- errors ----

describe('outdoorClassificationScores errors', () => {
  it('throws for invalid bowstyle (Traditional)', () => {
    expect(() => outdoorClassificationScores(
      outdoorRound('wa1440_90'), Bowstyle.Traditional, Gender.Male, Age.Adult, true, true,
    )).toThrow();
  });
  it('throws for unrecognised round', () => {
    const customRound = {
      name: 'Custom', codename: 'custom_round_xyz',
      passes: [atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), false)],
      nArrows: 36,
    };
    expect(() => outdoorClassificationScores(
      customRound, Bowstyle.Recurve, Gender.Male, Age.Adult, true, true,
    )).toThrow();
  });
});

// ---- calculateOutdoorClassification ----

describe('calculateOutdoorClassification', () => {
  const cases: [string, number, Age, Bowstyle, string][] = [
    ['wa1440_90', 1390, Age.Adult,   Bowstyle.Compound, 'EMB'],
    ['wa1440_70', 1382, Age.Over50,  Bowstyle.Compound, 'GMB'],
    ['wa1440_90',  900, Age.Under21, Bowstyle.Barebow,  'MB'],
    ['wa1440_70', 1269, Age.Under18, Bowstyle.Compound, 'B1'],
    ['wa1440_70',  969, Age.Under18, Bowstyle.Recurve,  'B1'],
    ['metric_v',   992, Age.Under12, Bowstyle.Recurve,  'B2'],
    ['metric_v',   222, Age.Under12, Bowstyle.Longbow,  'A1'],
    ['metric_v',    91, Age.Under12, Bowstyle.Longbow,  'UC'],
    ['metric_v',     1, Age.Under12, Bowstyle.Longbow,  'UC'],
    ['metric_v',   250, Age.Under12, Bowstyle.Longbow,  'A1'],
  ];
  for (const [roundName, score, age, bowstyle, want] of cases) {
    it(`${roundName} score=${score} ${bowstyle} ${age} → ${want}`, () => {
      const cls = calculateOutdoorClassification(
        score, outdoorRound(roundName), bowstyle, Gender.Male, age, true, true,
      );
      expect(cls).toBe(want);
    });
  }
});

describe('calculateOutdoorClassification invalid score', () => {
  it('throws for negative score', () => {
    expect(() => calculateOutdoorClassification(
      -1, outdoorRound('wa1440_90'), Bowstyle.Recurve, Gender.Male, Age.Adult, true, true,
    )).toThrow();
  });
  it('throws for score over max', () => {
    expect(() => calculateOutdoorClassification(
      99999, outdoorRound('wa1440_90'), Bowstyle.Recurve, Gender.Male, Age.Adult, true, true,
    )).toThrow();
  });
});

// ---- coaxOutdoorGroup ----

describe('coaxOutdoorGroup', () => {
  const cases: [Bowstyle, Bowstyle][] = [
    [Bowstyle.Flatbow,        Bowstyle.Barebow],
    [Bowstyle.Traditional,    Bowstyle.Barebow],
    [Bowstyle.CompoundLimited, Bowstyle.Compound],
    [Bowstyle.CompoundBarebow, Bowstyle.Compound],
    [Bowstyle.Recurve,        Bowstyle.Recurve],
  ];
  for (const [input, wantBowstyle] of cases) {
    it(`${input} → ${wantBowstyle}`, () => {
      const cat = coaxOutdoorGroup(input, Gender.Male, Age.Adult);
      expect(cat.bowstyle).toBe(wantBowstyle);
    });
  }
});
