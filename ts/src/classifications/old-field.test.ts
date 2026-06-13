import { describe, it, expect } from 'vitest';
import {
  oldFieldClassificationScores,
  calculateOldFieldClassification,
  coaxOldFieldGroup,
} from './old-field.js';
import { Gender, Age, Bowstyle } from './data.js';
import { waFieldRounds, agbOutdoorImperialRounds, waOutdoorRounds, type Round } from '../rounds.js';

// ---- helpers ----

function fieldRound(name: string): Round {
  return waFieldRounds().get(name)!;
}

// ---- ages ----

describe('oldFieldClassificationScores ages (blue_marked barebow male)', () => {
  const cases: [Age, number[]][] = [
    [Age.Adult,   [328, 307, 279, 252, 224, 197]],
    [Age.Under18, [298, 279, 254, 229, 204, 179]],
  ];
  for (const [age, want] of cases) {
    it(age, () => {
      const scores = oldFieldClassificationScores(
        fieldRound('wa_field_24_blue_marked'), Bowstyle.Barebow, Gender.Male, age,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- genders ----

describe('oldFieldClassificationScores genders', () => {
  const cases: [string, Gender, Age, number[]][] = [
    ['wa_field_24_blue_marked', Gender.Male,   Age.Adult,   [328, 307, 279, 252, 224, 197]],
    ['wa_field_24_blue_marked', Gender.Female, Age.Adult,   [303, 284, 258, 233, 207, 182]],
    ['wa_field_24_blue_marked', Gender.Male,   Age.Under18, [298, 279, 254, 229, 204, 179]],
    ['wa_field_24_blue_marked', Gender.Female, Age.Under18, [251, 236, 214, 193, 172, 151]],
  ];
  for (const [roundName, gender, age, want] of cases) {
    it(`${gender} ${age}`, () => {
      const scores = oldFieldClassificationScores(
        fieldRound(roundName), Bowstyle.Barebow, gender, age,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- bowstyles ----

describe('oldFieldClassificationScores bowstyles (male adult)', () => {
  const cases: [string, Bowstyle, number[]][] = [
    ['wa_field_24_red_marked',  Bowstyle.Compound,    [393, 377, 344, 312, 279, 247]],
    ['wa_field_24_red_marked',  Bowstyle.Recurve,     [338, 317, 288, 260, 231, 203]],
    ['wa_field_24_blue_marked', Bowstyle.Barebow,     [328, 307, 279, 252, 224, 197]],
    ['wa_field_24_blue_marked', Bowstyle.Traditional, [262, 245, 223, 202, 178, 157]],
    ['wa_field_24_blue_marked', Bowstyle.Flatbow,     [262, 245, 223, 202, 178, 157]],
    ['wa_field_24_blue_marked', Bowstyle.Longbow,     [201, 188, 171, 155, 137, 121]],
  ];
  for (const [roundName, bowstyle, want] of cases) {
    it(`${roundName} ${bowstyle}`, () => {
      const scores = oldFieldClassificationScores(
        fieldRound(roundName), bowstyle, Gender.Male, Age.Adult,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- errors ----

describe('oldFieldClassificationScores errors', () => {
  it('throws for invalid age (Under12)', () => {
    expect(() => oldFieldClassificationScores(
      fieldRound('wa_field_24_blue_marked'), Bowstyle.Barebow, Gender.Male, Age.Under12,
    )).toThrow();
  });
  it('throws for non-field round', () => {
    const outdoor = (agbOutdoorImperialRounds().get('york') ?? waOutdoorRounds().get('wa1440_90'))!;
    expect(() => oldFieldClassificationScores(
      outdoor, Bowstyle.Recurve, Gender.Male, Age.Adult,
    )).toThrow();
  });
});

// ---- calculateOldFieldClassification ----

describe('calculateOldFieldClassification', () => {
  const cases: [string, number, Age, Bowstyle, string][] = [
    ['wa_field_24_red_marked',  400, Age.Adult,   Bowstyle.Compound,    'GMB'],
    ['wa_field_24_blue_marked', 177, Age.Under18, Bowstyle.Traditional, '1C'],
    // wrong peg for sighted → UC
    ['wa_field_24_blue_marked', 400, Age.Adult,   Bowstyle.Compound,    'UC'],
    // wrong peg for unsighted → UC
    ['wa_field_24_red_marked',  337, Age.Adult,   Bowstyle.Barebow,     'UC'],
    // low score
    ['wa_field_24_blue_marked',   1, Age.Adult,   Bowstyle.Longbow,     'UC'],
  ];
  for (const [roundName, score, age, bowstyle, want] of cases) {
    it(`${roundName} score=${score} ${bowstyle} ${age} → ${want}`, () => {
      const cls = calculateOldFieldClassification(
        score, fieldRound(roundName), bowstyle, Gender.Male, age,
      );
      expect(cls).toBe(want);
    });
  }
});

describe('calculateOldFieldClassification invalid scores', () => {
  for (const score of [1000, 433, -1, -100]) {
    it(`score=${score} throws`, () => {
      expect(() => calculateOldFieldClassification(
        score, fieldRound('wa_field_24_blue_marked'), Bowstyle.Barebow, Gender.Male, Age.Adult,
      )).toThrow();
    });
  }
});

// ---- coaxOldFieldGroup ----

describe('coaxOldFieldGroup age coercion', () => {
  const cases: [Age, Age][] = [
    [Age.Adult,   Age.Adult],
    [Age.Over50,  Age.Adult],
    [Age.Under21, Age.Adult],
    [Age.Under18, Age.Under18],
    [Age.Under16, Age.Under18],
    [Age.Under12, Age.Under18],
  ];
  for (const [inputAge, wantAge] of cases) {
    it(`${inputAge} → ${wantAge}`, () => {
      const cat = coaxOldFieldGroup(Bowstyle.Recurve, Gender.Male, inputAge);
      expect(cat.ageGroup).toBe(wantAge);
    });
  }
});
