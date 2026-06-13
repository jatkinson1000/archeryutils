import { describe, it, expect } from 'vitest';
import {
  indoorClassificationScores,
  calculateIndoorClassification,
  coaxIndoorGroup,
} from './indoor.js';
import { Gender, Age, Bowstyle } from './data.js';
import { agbIndoorRounds, waIndoorRounds, type Round, atTarget } from '../rounds.js';
import { ScoringSystem, cm, metres } from '../targets.js';

// ---- helpers ----

function indoorRound(name: string): Round {
  return (agbIndoorRounds().get(name) ?? waIndoorRounds().get(name))!;
}

// ---- indoorClassificationScores: ages ----

describe('indoorClassificationScores ages (portsmouth recurve male)', () => {
  const cases: [Age, number[]][] = [
    [Age.Adult,   [593, 582, 566, 546, 518, 483, 437, 378]],
    [Age.Over50,  [583, 569, 549, 522, 488, 444, 387, 316]],
    [Age.Under21, [583, 569, 549, 522, 488, 444, 387, 316]],
    [Age.Under18, [571, 552, 526, 493, 450, 395, 326, 250]],
    [Age.Under16, [555, 530, 498, 457, 403, 336, 260, 187]],
    [Age.Under15, [534, 503, 463, 411, 346, 271, 196, 134]],
    [Age.Under14, [508, 469, 419, 355, 281, 206, 141,  92]],
    [Age.Under12, [475, 426, 364, 291, 215, 149,  98,  62]],
  ];
  for (const [age, want] of cases) {
    it(age, () => {
      const scores = indoorClassificationScores(
        indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Male, age, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- indoorClassificationScores: genders ----

describe('indoorClassificationScores genders (portsmouth recurve female)', () => {
  const cases: [Age, number[]][] = [
    [Age.Adult,   [586, 572, 553, 528, 496, 454, 399, 331]],
    [Age.Under16, [539, 510, 472, 423, 360, 286, 211, 145]],
    [Age.Under15, [534, 503, 463, 411, 346, 271, 196, 134]],
    [Age.Under12, [475, 426, 364, 291, 215, 149,  98,  62]],
  ];
  for (const [age, want] of cases) {
    it(`female ${age}`, () => {
      const scores = indoorClassificationScores(
        indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Female, age, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- indoorClassificationScores: bowstyles ----

describe('indoorClassificationScores bowstyles (portsmouth male adult)', () => {
  const cases: [Bowstyle, number[]][] = [
    [Bowstyle.Compound, [594, 583, 571, 560, 549, 532, 508, 472]],
    [Bowstyle.Barebow,  [565, 549, 528, 503, 472, 433, 387, 331]],
    [Bowstyle.Longbow,  [501, 466, 423, 369, 306, 240, 178, 127]],
  ];
  for (const [bowstyle, want] of cases) {
    it(bowstyle, () => {
      const scores = indoorClassificationScores(
        indoorRound('portsmouth'), bowstyle, Gender.Male, Age.Adult, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- triple faces / spot variants ----

describe('indoorClassificationScores triple faces', () => {
  const cases: [string, number[]][] = [
    ['portsmouth_triple',  [594, 583, 571, 560, 549, 532, 508, 472]],
    ['worcester_5_centre', [-9999, -9999, 300, 294, 283, 267, 246, 217]],
    ['vegas_300_triple',   [300, 297, 290, 281, 269, 252, 230, 201]],
  ];
  for (const [roundName, want] of cases) {
    it(roundName, () => {
      const scores = indoorClassificationScores(
        indoorRound(roundName), Bowstyle.Compound, Gender.Male, Age.Adult, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- non-strict ----

describe('indoorClassificationScores non-strict', () => {
  it('frostbite (outdoor round) with non-strict = ok', () => {
    const frostbite: Round = {
      name: 'Frostbite',
      codename: 'frostbite',
      passes: [atTarget(36, ScoringSystem.TenZone, cm(80), metres(30), false)],
      nArrows: 36,
    };
    const want = [360, 356, 349, 339, 326, 309, 286, 256];
    const scores = indoorClassificationScores(
      frostbite, Bowstyle.Compound, Gender.Male, Age.Adult, false,
    );
    expect(scores).toEqual(want);
  });
});

// ---- errors ----

describe('indoorClassificationScores errors', () => {
  it('throws for invalid bowstyle (Traditional)', () => {
    expect(() => indoorClassificationScores(
      indoorRound('portsmouth'), Bowstyle.Traditional, Gender.Male, Age.Adult, true,
    )).toThrow();
  });
  it('throws for unrecognised round', () => {
    const customRound: Round = {
      name: 'Custom', codename: 'custom_indoor_xyz',
      passes: [atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), true)],
      nArrows: 36,
    };
    expect(() => indoorClassificationScores(
      customRound, Bowstyle.Recurve, Gender.Male, Age.Adult, true,
    )).toThrow();
  });
});

// ---- calculateIndoorClassification ----

describe('calculateIndoorClassification', () => {
  const cases: [number, Age, Bowstyle, string][] = [
    [594, Age.Adult,   Bowstyle.Compound, 'I-GMB'],
    [582, Age.Over50,  Bowstyle.Recurve,  'I-MB'],
    [520, Age.Under21, Bowstyle.Barebow,  'I-B1'],
    [551, Age.Under18, Bowstyle.Recurve,  'I-B1'],
    [526, Age.Under18, Bowstyle.Recurve,  'I-B1'],
    [449, Age.Under12, Bowstyle.Compound, 'I-B2'],
    [ 40, Age.Under12, Bowstyle.Longbow,  'I-A1'],
    [ 12, Age.Under12, Bowstyle.Longbow,  'UC'],
    [  1, Age.Under12, Bowstyle.Longbow,  'UC'],
  ];
  for (const [score, age, bowstyle, want] of cases) {
    it(`score=${score} ${bowstyle} ${age} → ${want}`, () => {
      const cls = calculateIndoorClassification(
        score, indoorRound('portsmouth'), bowstyle, Gender.Male, age, true,
      );
      expect(cls).toBe(want);
    });
  }
});

describe('calculateIndoorClassification invalid score', () => {
  it('throws for negative score', () => {
    expect(() => calculateIndoorClassification(
      -1, indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Male, Age.Adult, true,
    )).toThrow();
  });
});

// ---- coaxIndoorGroup ----

describe('coaxIndoorGroup', () => {
  const cases: [Bowstyle, Bowstyle][] = [
    [Bowstyle.Flatbow,         Bowstyle.Barebow],
    [Bowstyle.Traditional,     Bowstyle.Barebow],
    [Bowstyle.CompoundLimited, Bowstyle.Compound],
    [Bowstyle.CompoundBarebow, Bowstyle.Compound],
    [Bowstyle.Recurve,         Bowstyle.Recurve],
  ];
  for (const [input, wantBowstyle] of cases) {
    it(`${input} → ${wantBowstyle}`, () => {
      const cat = coaxIndoorGroup(input, Gender.Male, Age.Adult);
      expect(cat.bowstyle).toBe(wantBowstyle);
    });
  }
});
