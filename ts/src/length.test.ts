import { describe, it, expect } from 'vitest';
import { toMetres, fromMetres, definitiveUnit, SUPPORTED_DIAM_UNITS, SUPPORTED_DIST_UNITS } from './length.js';

describe('toMetres', () => {
  it('metres pass through unchanged', () => {
    expect(toMetres(10, 'metre')).toBe(10);
  });
  it('centimetres to metres', () => {
    expect(toMetres(10, 'cm')).toBeCloseTo(0.1, 9);
  });
  it('inches to metres', () => {
    expect(toMetres(10, 'inch')).toBeCloseTo(0.254, 9);
  });
  it('yards to metres', () => {
    expect(toMetres(10, 'yard')).toBeCloseTo(9.144, 9);
  });
  it('alias: Metres', () => {
    expect(toMetres(5, 'Metres')).toBe(5);
  });
  it('alias: Yard', () => {
    expect(toMetres(100, 'Yard')).toBeCloseTo(91.44, 6);
  });
  it('throws for unsupported unit', () => {
    expect(() => toMetres(1, 'furlong')).toThrow();
  });
});

describe('fromMetres', () => {
  it('metres pass through unchanged', () => {
    expect(fromMetres(10, 'metre')).toBe(10);
  });
  it('metres to centimetres', () => {
    expect(fromMetres(0.1, 'cm')).toBeCloseTo(10, 9);
  });
  it('metres to yards', () => {
    expect(fromMetres(9.144, 'yard')).toBeCloseTo(10, 9);
  });
  it('throws for unsupported unit', () => {
    expect(() => fromMetres(1, 'furlong')).toThrow();
  });
});

describe('definitiveUnit', () => {
  it('yard aliases resolve to yard', () => {
    for (const a of ['yard', 'Yard', 'yards', 'Yards', 'yd', 'Yd', 'Y', 'y']) {
      expect(definitiveUnit(a)).toBe('yard');
    }
  });
  it('metre aliases resolve to metre', () => {
    for (const a of ['metre', 'Metre', 'metres', 'Metres', 'm', 'M']) {
      expect(definitiveUnit(a)).toBe('metre');
    }
  });
  it('cm aliases resolve to cm', () => {
    for (const a of ['cm', 'CM', 'cms', 'centimetre', 'Centimetre']) {
      expect(definitiveUnit(a)).toBe('cm');
    }
  });
  it('inch aliases resolve to inch', () => {
    for (const a of ['inch', 'Inch', 'inches', 'Inches']) {
      expect(definitiveUnit(a)).toBe('inch');
    }
  });
  it('throws for unrecognised alias', () => {
    expect(() => definitiveUnit('furlong')).toThrow();
  });
});

describe('SUPPORTED_DIAM_UNITS', () => {
  it('includes cm, inch, metre', () => {
    expect(SUPPORTED_DIAM_UNITS.has('cm')).toBe(true);
    expect(SUPPORTED_DIAM_UNITS.has('inch')).toBe(true);
    expect(SUPPORTED_DIAM_UNITS.has('metre')).toBe(true);
  });
  it('does not include yard', () => {
    expect(SUPPORTED_DIAM_UNITS.has('yard')).toBe(false);
  });
});

describe('SUPPORTED_DIST_UNITS', () => {
  it('includes yard and metre', () => {
    expect(SUPPORTED_DIST_UNITS.has('yard')).toBe(true);
    expect(SUPPORTED_DIST_UNITS.has('metre')).toBe(true);
  });
  it('does not include cm or inch', () => {
    expect(SUPPORTED_DIST_UNITS.has('cm')).toBe(false);
    expect(SUPPORTED_DIST_UNITS.has('inch')).toBe(false);
  });
});
