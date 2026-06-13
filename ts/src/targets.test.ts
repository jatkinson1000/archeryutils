import { describe, it, expect } from 'vitest';
import { Target, ScoringSystem, genFaceSpec, cm, metres, yards, inches, type FaceSpec } from './targets.js';

// ---- helpers ----

function makeTarget(
  system: ScoringSystem,
  diamVal: number, diamUnit: string,
  distVal: number, distUnit: string,
  indoor = false,
): Target {
  return Target.create(system, { value: diamVal, units: diamUnit }, { value: distVal, units: distUnit }, indoor);
}

// ---- Target.toString ----

describe('Target.toString', () => {
  it('native units preserved in string', () => {
    const t = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    expect(t.toString()).toContain('122');
    expect(t.toString()).toContain('cm');
    expect(t.toString()).toContain('70');
    expect(t.toString()).toContain('metre');
  });
  it('includes scoring system', () => {
    const t = makeTarget(ScoringSystem.FiveZone, 122, 'cm', 100, 'yard');
    expect(t.toString()).toContain('5_zone');
    expect(t.toString()).toContain('yard');
  });
});

// ---- Target equality ----

describe('Target equality', () => {
  it('identical targets are equal', () => {
    const a = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    const b = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    expect(a.equals(b)).toBe(true);
  });
  it('different scoring system', () => {
    const a = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    const b = makeTarget(ScoringSystem.FiveZone, 122, 'cm', 70, 'metre');
    expect(a.equals(b)).toBe(false);
  });
  it('different distance', () => {
    const a = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    const b = makeTarget(ScoringSystem.TenZone, 122, 'cm', 50, 'metre');
    expect(a.equals(b)).toBe(false);
  });
  it('different diameter', () => {
    const a = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    const b = makeTarget(ScoringSystem.TenZone, 80, 'cm', 70, 'metre');
    expect(a.equals(b)).toBe(false);
  });
  it('different indoor flag', () => {
    const a = makeTarget(ScoringSystem.TenZone, 40, 'cm', 18, 'metre', false);
    const b = makeTarget(ScoringSystem.TenZone, 40, 'cm', 18, 'metre', true);
    expect(a.equals(b)).toBe(false);
  });
  it('yard and metre equal after conversion', () => {
    const a = makeTarget(ScoringSystem.FiveZone, 122, 'cm', 100, 'yard');
    const b = makeTarget(ScoringSystem.FiveZone, 122, 'cm', 91.44, 'metre');
    // different native units → not equal
    expect(a.equals(b)).toBe(false);
  });
});

// ---- Invalid construction ----

describe('Target.create validation', () => {
  it('throws for invalid scoring system', () => {
    expect(() => Target.create('unknown_system' as ScoringSystem, cm(122), metres(70), false))
      .toThrow('Invalid Target Face Type');
  });
  it('throws for invalid distance unit', () => {
    expect(() => Target.create(ScoringSystem.TenZone, cm(122), { value: 70, units: 'furlong' }, false))
      .toThrow();
  });
  it('throws for invalid diameter unit', () => {
    expect(() => Target.create(ScoringSystem.TenZone, { value: 122, units: 'furlong' }, metres(70), false))
      .toThrow();
  });
  it('defaults distance unit aliases', () => {
    const t = Target.create(ScoringSystem.TenZone, cm(122), { value: 70, units: 'metres' }, false);
    expect(t.nativeDistance.units).toBe('metre');
  });
});

// ---- Unit coercion to definitive ----

describe('unit coercion', () => {
  it('Yards → yard in native distance', () => {
    const t = makeTarget(ScoringSystem.FiveZone, 122, 'cm', 100, 'Yards');
    expect(t.nativeDistance.units).toBe('yard');
  });
  it('Metres → metre in native distance', () => {
    const t = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'Metres');
    expect(t.nativeDistance.units).toBe('metre');
  });
  it('CM → cm in native diameter', () => {
    const t = makeTarget(ScoringSystem.TenZone, 122, 'CM', 70, 'metre');
    expect(t.nativeDiameter.units).toBe('cm');
  });
});

// ---- Yard to metre conversion ----

describe('Target.distance in metres', () => {
  it('100 yards converts correctly', () => {
    const t = makeTarget(ScoringSystem.FiveZone, 122, 'cm', 100, 'yard');
    expect(t.distance).toBeCloseTo(91.44, 4);
  });
  it('metre distance unmodified', () => {
    const t = makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre');
    expect(t.distance).toBe(70);
  });
});

// ---- Default location ----

describe('Target indoor flag', () => {
  it('defaults to outdoor (false)', () => {
    const t = Target.create(ScoringSystem.TenZone, cm(122), metres(70), false);
    expect(t.indoor).toBe(false);
  });
  it('indoor flag set', () => {
    const t = Target.create(ScoringSystem.Worcester, cm(40), metres(18), true);
    expect(t.indoor).toBe(true);
  });
});

// ---- maxScore for all systems ----

describe('Target.maxScore', () => {
  const cases: [ScoringSystem, number][] = [
    [ScoringSystem.FiveZone, 9],
    [ScoringSystem.TenZone, 10],
    [ScoringSystem.TenZoneCompound, 10],
    [ScoringSystem.TenZoneSixRing, 10],
    [ScoringSystem.TenZoneFiveRing, 10],
    [ScoringSystem.TenZoneFiveRingCmpd, 10],
    [ScoringSystem.ElevenZone, 11],
    [ScoringSystem.ElevenZoneSixRing, 11],
    [ScoringSystem.ElevenZoneFiveRing, 11],
    [ScoringSystem.WAField, 6],
    [ScoringSystem.IFAAField, 5],
    [ScoringSystem.IFAAFieldExpert, 5],
    [ScoringSystem.AANationalField, 5],
    [ScoringSystem.BeiterHitMiss, 1],
    [ScoringSystem.Worcester, 5],
    [ScoringSystem.Worcester2Ring, 5],
  ];
  for (const [sys, want] of cases) {
    it(`${sys} maxScore = ${want}`, () => {
      const t = Target.create(sys, cm(40), metres(18), false);
      expect(t.maxScore).toBe(want);
    });
  }
});

// ---- minScore ----

describe('Target.minScore', () => {
  it('5_zone minScore = 1', () => {
    expect(makeTarget(ScoringSystem.FiveZone, 122, 'cm', 70, 'metre').minScore).toBe(1);
  });
  it('10_zone minScore = 1', () => {
    expect(makeTarget(ScoringSystem.TenZone, 122, 'cm', 70, 'metre').minScore).toBe(1);
  });
  it('Worcester minScore = 1', () => {
    expect(makeTarget(ScoringSystem.Worcester, 40, 'cm', 18, 'metre', true).minScore).toBe(1);
  });
  it('Beiter_hit_miss minScore = 1', () => {
    expect(makeTarget(ScoringSystem.BeiterHitMiss, 40, 'cm', 18, 'metre').minScore).toBe(1);
  });
});

// ---- genFaceSpec / faceSpec ----

describe('genFaceSpec', () => {
  it('5_zone produces 5 rings with correct scores', () => {
    const spec = genFaceSpec(ScoringSystem.FiveZone, 1.22);
    expect(spec.size).toBe(5);
    const scores = [...spec.values()].sort((a, b) => a - b);
    expect(scores).toEqual([1, 3, 5, 7, 9]);
  });
  it('10_zone produces 10 rings', () => {
    const spec = genFaceSpec(ScoringSystem.TenZone, 1.22);
    expect(spec.size).toBe(10);
  });
  it('10_zone_6_ring produces 6 rings', () => {
    const spec = genFaceSpec(ScoringSystem.TenZoneSixRing, 1.22);
    expect(spec.size).toBe(6);
  });
  it('11_zone produces 11 rings', () => {
    const spec = genFaceSpec(ScoringSystem.ElevenZone, 0.40);
    expect(spec.size).toBe(11);
  });
  it('WA_field produces 6 rings', () => {
    const spec = genFaceSpec(ScoringSystem.WAField, 0.40);
    expect(spec.size).toBe(6);
  });
  it('Worcester produces 5 rings', () => {
    const spec = genFaceSpec(ScoringSystem.Worcester, 0.40);
    expect(spec.size).toBe(5);
  });
  it('Worcester_2_ring produces 2 rings', () => {
    const spec = genFaceSpec(ScoringSystem.Worcester2Ring, 0.40);
    expect(spec.size).toBe(2);
  });
  it('throws for unsupported system', () => {
    expect(() => genFaceSpec('unknown' as ScoringSystem, 1.0)).toThrow();
  });
});

// ---- Target.fromFaceSpec ----

describe('Target.fromFaceSpec', () => {
  it('custom face spec with cm units', () => {
    const spec: FaceSpec = new Map([[8, 10], [12, 8], [16, 7], [20, 6]]);
    const t = Target.fromFaceSpec([spec, 'cm'], cm(40), metres(18), true);
    expect(t.maxScore).toBe(10);
    expect(t.minScore).toBe(6);
    expect(t.indoor).toBe(true);
  });
  it('custom face spec in metres (default)', () => {
    const spec: FaceSpec = new Map([[0.08, 10], [0.12, 8], [0.16, 7], [0.20, 6]]);
    const t = Target.fromFaceSpec(spec, cm(40), metres(18), true);
    expect(t.maxScore).toBe(10);
    expect(t.faceSpec.size).toBe(4);
  });
  it('faceSpec copy is returned (not reference)', () => {
    const spec: FaceSpec = new Map([[0.08, 10], [0.12, 8]]);
    const t = Target.fromFaceSpec(spec, cm(40), metres(18), false);
    const returned = t.faceSpec;
    returned.set(99, 99);
    expect(t.faceSpec.has(99)).toBe(false);
  });
});

// ---- helper constructors ----

describe('Quantity helpers', () => {
  it('cm() creates cm quantity', () => {
    expect(cm(122)).toEqual({ value: 122, units: 'cm' });
  });
  it('metres() creates metre quantity', () => {
    expect(metres(70)).toEqual({ value: 70, units: 'metre' });
  });
  it('yards() creates yard quantity', () => {
    expect(yards(100)).toEqual({ value: 100, units: 'yard' });
  });
  it('inches() creates inch quantity', () => {
    expect(inches(16)).toEqual({ value: 16, units: 'inch' });
  });
});
