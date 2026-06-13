import { describe, it, expect } from 'vitest';
import {
  fieldClassificationScores,
  calculateFieldClassification,
  coaxFieldGroup,
} from './field.js';
import { Gender, Age, Bowstyle } from './data.js';
import { waFieldRounds, type Round, atTarget } from '../rounds.js';
import { ScoringSystem, cm, metres } from '../targets.js';

// ---- helpers ----

function fieldRound(name: string): Round {
  return waFieldRounds().get(name)!;
}

// ---- fieldClassificationScores: ages ----

describe('fieldClassificationScores ages (blue_marked barebow male)', () => {
  const cases: [Age, number[]][] = [
    [Age.Adult,   [336, 311, 283, 249, 212, 173, 135, 101, 74]],
    [Age.Over50,  [321, 294, 263, 227, 188, 149, 114,  84, 60]],
    [Age.Under18, [305, 275, 241, 203, 164, 127,  94,  68, 48]],
    [Age.Under12, [224, 185, 146, 111,  82,  58,  41,  28, 19]],
  ];
  for (const [age, want] of cases) {
    it(age, () => {
      const scores = fieldClassificationScores(
        fieldRound('wa_field_24_blue_marked'), Bowstyle.Barebow, Gender.Male, age, true, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- fieldClassificationScores: genders ----

describe('fieldClassificationScores genders (blue_marked barebow)', () => {
  const cases: [Gender, Age, number[]][] = [
    [Gender.Male,   Age.Adult,   [336, 311, 283, 249, 212, 173, 135, 101, 74]],
    [Gender.Female, Age.Adult,   [315, 287, 255, 218, 179, 140, 106,  78, 55]],
    [Gender.Male,   Age.Under18, [305, 275, 241, 203, 164, 127,  94,  68, 48]],
    [Gender.Female, Age.Under18, [280, 247, 209, 170, 132,  99,  72,  51, 35]],
  ];
  for (const [gender, age, want] of cases) {
    it(`${gender} ${age}`, () => {
      const scores = fieldClassificationScores(
        fieldRound('wa_field_24_blue_marked'), Bowstyle.Barebow, gender, age, true, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- fieldClassificationScores: bowstyles ----

describe('fieldClassificationScores bowstyles (male adult)', () => {
  const cases: [string, Bowstyle, number[]][] = [
    ['wa_field_24_red_marked',   Bowstyle.Compound,       [408, 391, 369, 345, 318, 286, 248, 204, 157]],
    ['wa_field_12_red_unmarked', Bowstyle.Compound,       [-9999, -9999, -9999, 173, 159, 143, 124, 102, 79]],
    ['wa_field_24_red_marked',   Bowstyle.CompoundLimited,[369, 347, 322, 293, 259, 219, 176, 133, 96]],
    ['wa_field_24_blue_marked',  Bowstyle.CompoundBarebow,[343, 321, 296, 268, 235, 200, 164, 129, 99]],
    ['wa_field_24_red_marked',   Bowstyle.Recurve,        [369, 343, 314, 279, 237, 189, 139,  96, 62]],
    ['wa_field_24_blue_marked',  Bowstyle.Barebow,        [336, 311, 283, 249, 212, 173, 135, 101, 74]],
    ['wa_field_24_blue_marked',  Bowstyle.Traditional,    [309, 283, 252, 218, 182, 146, 114,  86, 63]],
    ['wa_field_24_blue_marked',  Bowstyle.Flatbow,        [273, 244, 212, 179, 146, 116,  90,  68, 51]],
    ['wa_field_24_blue_marked',  Bowstyle.Longbow,        [241, 209, 176, 143, 114,  88,  67,  49, 36]],
  ];
  for (const [roundName, bowstyle, want] of cases) {
    it(`${roundName} ${bowstyle}`, () => {
      const scores = fieldClassificationScores(
        fieldRound(roundName), bowstyle, Gender.Male, Age.Adult, true, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- unmarked same as marked ----

describe('fieldClassificationScores unmarked', () => {
  it('blue_unmarked = blue_marked scores', () => {
    const want = [336, 311, 283, 249, 212, 173, 135, 101, 74];
    const scores = fieldClassificationScores(
      fieldRound('wa_field_24_blue_unmarked'), Bowstyle.Barebow, Gender.Male, Age.Adult, true, true,
    );
    expect(scores).toEqual(want);
  });
});

// ---- non-strict round ----

describe('fieldClassificationScores non-strict round', () => {
  const cases: [string, Bowstyle, Gender, Age, number[]][] = [
    ['wa_field_24_red_marked', Bowstyle.Barebow, Gender.Male, Age.Adult,
      [-9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999, -9999]],
    ['wa_field_24_yellow_marked', Bowstyle.Barebow, Gender.Male, Age.Adult,
      [-9999, -9999, -9999, -9999, -9999, -9999, 178, 140, 106]],
  ];
  for (const [roundName, bowstyle, gender, age, want] of cases) {
    it(roundName, () => {
      const scores = fieldClassificationScores(
        fieldRound(roundName), bowstyle, gender, age, false, true,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- non-strict distance ----

describe('fieldClassificationScores non-strict distance', () => {
  const cases: [string, Bowstyle, number[]][] = [
    ['wa_field_24_red_marked',   Bowstyle.Barebow, [306, 277, 243, 204, 164, 125,  91, 64, 44]],
    ['wa_field_12_red_marked',   Bowstyle.Barebow, [-9999, -9999, -9999, 102, 82, 63, 46, 32, 22]],
    ['wa_field_24_yellow_marked',Bowstyle.Barebow, [360, 338, 313, 285, 253, 217, 178, 140, 106]],
  ];
  for (const [roundName, bowstyle, want] of cases) {
    it(`${roundName} non-strict-dist`, () => {
      const scores = fieldClassificationScores(
        fieldRound(roundName), bowstyle, Gender.Male, Age.Adult, true, false,
      );
      expect(scores).toEqual(want);
    });
  }
});

// ---- errors ----

describe('fieldClassificationScores errors', () => {
  it('throws for Under21 (not a valid field age)', () => {
    expect(() => fieldClassificationScores(
      fieldRound('wa_field_24_blue_marked'), Bowstyle.Barebow, Gender.Male, Age.Under21, true, true,
    )).toThrow();
  });
  it('throws for unrecognised round', () => {
    const customRound: Round = {
      name: 'Custom', codename: 'custom_field_xyz',
      passes: [atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), false)],
      nArrows: 36,
    };
    expect(() => fieldClassificationScores(
      customRound, Bowstyle.Recurve, Gender.Male, Age.Adult, true, true,
    )).toThrow();
  });
});

// ---- calculateFieldClassification ----

describe('calculateFieldClassification', () => {
  const cases: [string, number, Age, Bowstyle, string][] = [
    ['wa_field_24_red_marked',   400, Age.Adult,   Bowstyle.Compound,   'GMB'],
    ['wa_field_12_red_marked',   200, Age.Adult,   Bowstyle.Compound,   'B1'],
    ['wa_field_24_blue_marked',  400, Age.Adult,   Bowstyle.Compound,   'A1'],
    ['wa_field_24_blue_marked',  177, Age.Under18, Bowstyle.Traditional,'B1'],
    ['wa_field_24_blue_marked',  100, Age.Adult,   Bowstyle.Barebow,    'A3'],
    ['wa_field_24_blue_marked',   50, Age.Adult,   Bowstyle.Barebow,    'UC'],
  ];
  for (const [roundName, score, age, bowstyle, want] of cases) {
    it(`${roundName} score=${score} ${bowstyle} ${age} → ${want}`, () => {
      const cls = calculateFieldClassification(
        score, fieldRound(roundName), bowstyle, Gender.Male, age, true, true,
      );
      expect(cls).toBe(want);
    });
  }
});

// ---- coaxFieldGroup ----

describe('coaxFieldGroup age coercion', () => {
  const cases: [Age, Age][] = [
    [Age.Adult,   Age.Adult],
    [Age.Under21, Age.Adult],
    [Age.Under18, Age.Under18],
    [Age.Under12, Age.Under12],
  ];
  for (const [inputAge, wantAge] of cases) {
    it(`${inputAge} → ${wantAge}`, () => {
      const cat = coaxFieldGroup(Bowstyle.Recurve, Gender.Male, inputAge);
      expect(cat.ageGroup).toBe(wantAge);
    });
  }
});
