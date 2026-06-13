import { describe, it, expect } from 'vitest';
import {
  oldIndoorClassificationScores,
  calculateOldIndoorClassification,
  coaxOldIndoorGroup,
} from './old-indoor.js';
import { Gender, Age, Bowstyle } from './data.js';
import { agbIndoorRounds, waIndoorRounds, type Round, atTarget } from '../rounds.js';
import { ScoringSystem, cm, metres } from '../targets.js';

// ---- helpers ----

function indoorRound(name: string): Round {
  return (agbIndoorRounds().get(name) ?? waIndoorRounds().get(name))!;
}

// ---- ages (all map to Adult for old indoor) ----

describe('oldIndoorClassificationScores ages all → Adult', () => {
  it('Adult recurve male portsmouth', () => {
    const want = [592, 582, 554, 505, 432, 315, 195, 139];
    const scores = oldIndoorClassificationScores(
      indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Male, Age.Adult, true,
    );
    expect(scores).toEqual(want);
  });
});

// ---- gender ----

describe('oldIndoorClassificationScores gender', () => {
  it('female recurve portsmouth', () => {
    const want = [582, 569, 534, 479, 380, 255, 139, 93];
    const scores = oldIndoorClassificationScores(
      indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Female, Age.Adult, true,
    );
    expect(scores).toEqual(want);
  });
});

// ---- bowstyles ----

describe('oldIndoorClassificationScores bowstyles', () => {
  const cases: [Bowstyle, Gender, number[]][] = [
    [Bowstyle.Compound, Gender.Male,   [581, 570, 554, 529, 484, 396, 279, 206]],
    [Bowstyle.Compound, Gender.Female, [570, 562, 544, 509, 449, 347, 206, 160]],
  ];
  for (const [bowstyle, gender, want] of cases) {
    it(`${bowstyle} ${gender}`, () => {
      const scores = oldIndoorClassificationScores(
        indoorRound('portsmouth'), bowstyle, gender, Age.Adult, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- triple faces / spot variants ----

describe('oldIndoorClassificationScores triple faces', () => {
  const cases: [string, number[]][] = [
    ['portsmouth_triple', [581, 570, 554, 529, 484, 396, 279, 206]],
    ['worcester_5_centre', [300, 299, 289, 264, 226, 162, 96, 65]],
    ['wa18_triple', [568, 558, 537, 486, 370, 203, 100, 63]],
    ['wa18',        [568, 558, 537, 493, 420, 295, 173, 117]],
  ];
  for (const [roundName, want] of cases) {
    it(roundName, () => {
      const scores = oldIndoorClassificationScores(
        indoorRound(roundName), Bowstyle.Compound, Gender.Male, Age.Adult, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- non-strict ----

describe('oldIndoorClassificationScores non-strict', () => {
  it('frostbite (outdoor) with non-strict', () => {
    const frostbite: Round = {
      name: 'Frostbite',
      codename: 'frostbite',
      passes: [atTarget(36, ScoringSystem.TenZone, cm(80), metres(30), false)],
      nArrows: 36,
    };
    const want = [357, 351, 336, 310, 269, 195, 110, 68];
    const scores = oldIndoorClassificationScores(
      frostbite, Bowstyle.Compound, Gender.Male, Age.Adult, false,
    );
    expect(scores).toEqual(want);
  });
});

// ---- errors ----

describe('oldIndoorClassificationScores errors', () => {
  it('throws for invalid bowstyle (Barebow)', () => {
    expect(() => oldIndoorClassificationScores(
      indoorRound('portsmouth'), Bowstyle.Barebow, Gender.Male, Age.Adult, true,
    )).toThrow();
  });
  it('throws for invalid age (Under12)', () => {
    expect(() => oldIndoorClassificationScores(
      indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Male, Age.Under12, true,
    )).toThrow();
  });
  it('throws for outdoor round', () => {
    // use an outdoor round codename not in indoor
    const outdoorRound: Round = {
      name: 'WA1440', codename: 'wa1440_90',
      passes: [atTarget(36, ScoringSystem.TenZone, cm(122), metres(90), false)],
      nArrows: 36,
    };
    expect(() => oldIndoorClassificationScores(
      outdoorRound, Bowstyle.Recurve, Gender.Male, Age.Adult, true,
    )).toThrow();
  });
});

// ---- calculateOldIndoorClassification ----

describe('calculateOldIndoorClassification', () => {
  const cases: [number, Gender, string][] = [
    [400, Gender.Male,   'F'],
    [337, Gender.Female, 'F'],
    [592, Gender.Male,   'A'],
    [582, Gender.Female, 'A'],
    [581, Gender.Male,   'C'],
    [120, Gender.Male,   'UC'],
    [  1, Gender.Male,   'UC'],
  ];
  for (const [score, gender, want] of cases) {
    it(`score=${score} ${gender} → ${want}`, () => {
      const cls = calculateOldIndoorClassification(
        score, indoorRound('portsmouth'), Bowstyle.Recurve, gender, Age.Adult, true,
      );
      expect(cls).toBe(want);
    });
  }
});

describe('calculateOldIndoorClassification invalid scores', () => {
  for (const score of [1000, 601, -1, -100]) {
    it(`score=${score} throws`, () => {
      expect(() => calculateOldIndoorClassification(
        score, indoorRound('portsmouth'), Bowstyle.Recurve, Gender.Male, Age.Adult, true,
      )).toThrow();
    });
  }
});

// ---- coaxOldIndoorGroup ----

describe('coaxOldIndoorGroup', () => {
  const cases: [Bowstyle, Bowstyle, Age][] = [
    [Bowstyle.Compound,        Bowstyle.Compound, Age.Adult],
    [Bowstyle.CompoundLimited, Bowstyle.Compound, Age.Adult],
    [Bowstyle.CompoundBarebow, Bowstyle.Compound, Age.Adult],
    [Bowstyle.Recurve,         Bowstyle.Recurve,  Age.Adult],
    [Bowstyle.Barebow,         Bowstyle.Recurve,  Age.Adult],
    [Bowstyle.Longbow,         Bowstyle.Recurve,  Age.Adult],
  ];
  for (const [input, wantBowstyle, wantAge] of cases) {
    it(`${input} → ${wantBowstyle}`, () => {
      const cat = coaxOldIndoorGroup(input, Gender.Male, Age.Under18);
      expect(cat.bowstyle).toBe(wantBowstyle);
      expect(cat.ageGroup).toBe(wantAge);
    });
  }
});
