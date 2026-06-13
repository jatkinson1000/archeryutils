import { describe, it, expect } from 'vitest';
import {
  newPass, atTarget, passMaxScore,
  roundMaxScore, roundMaxDistance, roundInfo,
  agbOutdoorImperialRounds, agbOutdoorMetricRounds,
  waOutdoorRounds, waIndoorRounds, agbIndoorRounds,
  waFieldRounds, allRounds,
  type Pass, type Round,
} from './rounds.js';
import { ScoringSystem, cm, metres, yards } from './targets.js';

// ---- helpers ----

function makePass(nArrows: number, system: ScoringSystem, diamVal: number, distVal: number, distUnit = 'metre', indoor = false): Pass {
  return atTarget(nArrows, system, cm(diamVal), { value: distVal, units: distUnit }, indoor);
}

function makeYork(): Round {
  return {
    name: 'York',
    codename: 'york',
    passes: [
      makePass(72, ScoringSystem.FiveZone, 122, 100, 'yard'),
      makePass(48, ScoringSystem.FiveZone, 122, 80, 'yard'),
      makePass(24, ScoringSystem.FiveZone, 122, 60, 'yard'),
    ],
    nArrows: 144,
  };
}

function makeWA1440(): Round {
  return {
    name: 'WA1440 90m',
    codename: 'wa1440_90',
    passes: [
      makePass(36, ScoringSystem.TenZone, 122, 90),
      makePass(36, ScoringSystem.TenZone, 122, 70),
      makePass(36, ScoringSystem.TenZone, 80, 50),
      makePass(36, ScoringSystem.TenZone, 80, 30),
    ],
    nArrows: 144,
  };
}

// ---- newPass / atTarget ----

describe('newPass', () => {
  it('creates pass with correct arrow count', () => {
    const p = makePass(36, ScoringSystem.TenZone, 122, 70);
    expect(p.nArrows).toBe(36);
  });
  it('negative arrow count becomes positive', () => {
    const tgt = atTarget(36, ScoringSystem.TenZone, cm(122), metres(70), false).target;
    const p = newPass(-36, tgt);
    expect(p.nArrows).toBe(36);
  });
  it('pass target is accessible', () => {
    const p = makePass(36, ScoringSystem.TenZone, 122, 70);
    expect(p.target.maxScore).toBe(10);
  });
});

describe('atTarget', () => {
  it('throws for invalid scoring system', () => {
    expect(() => atTarget(36, 'bad_system' as ScoringSystem, cm(122), metres(70), false))
      .toThrow();
  });
  it('default distance unit is coerced', () => {
    const p = atTarget(36, ScoringSystem.TenZone, cm(122), { value: 70, units: 'metres' }, false);
    expect(p.target.nativeDistance.units).toBe('metre');
  });
  it('default diameter unit is cm', () => {
    const p = atTarget(36, ScoringSystem.TenZone, { value: 122, units: 'cms' }, metres(70), false);
    expect(p.target.nativeDiameter.units).toBe('cm');
  });
});

// ---- passMaxScore ----

describe('passMaxScore', () => {
  it('10_zone: 36 arrows × 10 = 360', () => {
    const p = makePass(36, ScoringSystem.TenZone, 122, 70);
    expect(passMaxScore(p)).toBe(360);
  });
  it('5_zone: 72 arrows × 9 = 648', () => {
    const p = makePass(72, ScoringSystem.FiveZone, 122, 100, 'yard');
    expect(passMaxScore(p)).toBe(648);
  });
  it('Worcester: 60 arrows × 5 = 300', () => {
    const p = atTarget(60, ScoringSystem.Worcester, cm(40), metres(18), true);
    expect(passMaxScore(p)).toBe(300);
  });
});

// ---- roundMaxScore ----

describe('roundMaxScore', () => {
  it('York: 144 arrows at 9 = 1296', () => {
    expect(roundMaxScore(makeYork())).toBe(1296);
  });
  it('WA1440: 144 arrows at 10 = 1440', () => {
    expect(roundMaxScore(makeWA1440())).toBe(1440);
  });
  it('Portsmouth: 60 arrows × 10 = 600', () => {
    const r: Round = {
      name: 'Portsmouth',
      codename: 'portsmouth',
      passes: [atTarget(60, ScoringSystem.TenZone, cm(60), metres(18), true)],
      nArrows: 60,
    };
    expect(roundMaxScore(r)).toBe(600);
  });
});

// ---- roundMaxDistance ----

describe('roundMaxDistance', () => {
  it('WA1440 max distance is 90m', () => {
    const d = roundMaxDistance(makeWA1440());
    expect(d.value).toBe(90);
    expect(d.units).toBe('metre');
  });
  it('York max distance is 100 yards', () => {
    const d = roundMaxDistance(makeYork());
    expect(d.value).toBe(100);
    expect(d.units).toBe('yard');
  });
  it('handles out-of-order passes', () => {
    const r: Round = {
      name: 'Test',
      codename: 'test',
      passes: [
        makePass(36, ScoringSystem.TenZone, 80, 30),
        makePass(36, ScoringSystem.TenZone, 122, 90),
        makePass(36, ScoringSystem.TenZone, 122, 70),
      ],
      nArrows: 108,
    };
    const d = roundMaxDistance(r);
    expect(d.value).toBe(90);
  });
  it('mixed units: max by metres', () => {
    const r: Round = {
      name: 'Mixed',
      codename: 'mixed',
      passes: [
        makePass(36, ScoringSystem.TenZone, 122, 50),
        makePass(36, ScoringSystem.FiveZone, 122, 100, 'yard'),
      ],
      nArrows: 72,
    };
    // 100 yards = 91.44m > 50m
    const d = roundMaxDistance(r);
    expect(d.units).toBe('yard');
  });
});

// ---- roundInfo ----

describe('roundInfo', () => {
  it('contains round name', () => {
    const info = roundInfo(makeYork());
    expect(info).toContain('York');
  });
  it('contains arrow counts', () => {
    const info = roundInfo(makeYork());
    expect(info).toContain('72');
    expect(info).toContain('48');
    expect(info).toContain('24');
  });
});

// ---- round data loading ----

describe('waOutdoorRounds', () => {
  it('loads wa1440_90', () => {
    const r = waOutdoorRounds().get('wa1440_90');
    expect(r).toBeDefined();
    expect(r!.name).toBeDefined();
    expect(r!.passes.length).toBeGreaterThan(0);
  });
  it('wa1440_90 max score is 1440', () => {
    const r = waOutdoorRounds().get('wa1440_90')!;
    expect(roundMaxScore(r)).toBe(1440);
  });
  it('wa720_70 max score is 720', () => {
    const r = waOutdoorRounds().get('wa720_70')!;
    expect(roundMaxScore(r)).toBe(720);
  });
});

describe('agbOutdoorImperialRounds', () => {
  it('loads york', () => {
    const r = agbOutdoorImperialRounds().get('york');
    expect(r).toBeDefined();
    expect(r!.passes.length).toBe(3);
  });
  it('york max score is 1296', () => {
    const r = agbOutdoorImperialRounds().get('york')!;
    expect(roundMaxScore(r)).toBe(1296);
  });
});

describe('agbIndoorRounds', () => {
  it('loads portsmouth', () => {
    const r = agbIndoorRounds().get('portsmouth');
    expect(r).toBeDefined();
    expect(r!.location).toBe('indoor');
  });
  it('portsmouth max score is 600', () => {
    const r = agbIndoorRounds().get('portsmouth')!;
    expect(roundMaxScore(r)).toBe(600);
  });
});

describe('waFieldRounds', () => {
  it('loads wa_field_24_red_marked', () => {
    const r = waFieldRounds().get('wa_field_24_red_marked');
    expect(r).toBeDefined();
  });
});

describe('allRounds', () => {
  it('loads at least 50 rounds', () => {
    const all = allRounds();
    expect(all.size).toBeGreaterThanOrEqual(50);
  });
  it('includes rounds from multiple collections', () => {
    const all = allRounds();
    expect(all.has('york')).toBe(true);
    expect(all.has('wa1440_90')).toBe(true);
    expect(all.has('portsmouth')).toBe(true);
    expect(all.has('wa_field_24_red_marked')).toBe(true);
  });
});
