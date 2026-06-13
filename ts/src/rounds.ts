import { Target, ScoringSystem, Quantity } from './targets.js';
import { definitiveUnit, toMetres } from './length.js';

import agbOutdoorImperial from '../../rounds/data/AGB_outdoor_imperial.json' with { type: 'json' };
import agbOutdoorMetric from '../../rounds/data/AGB_outdoor_metric.json' with { type: 'json' };
import agbIndoor from '../../rounds/data/AGB_indoor.json' with { type: 'json' };
import waOutdoor from '../../rounds/data/WA_outdoor.json' with { type: 'json' };
import waIndoor from '../../rounds/data/WA_indoor.json' with { type: 'json' };
import waField from '../../rounds/data/WA_field.json' with { type: 'json' };
import waExperimental from '../../rounds/data/WA_experimental.json' with { type: 'json' };
import ifaaField from '../../rounds/data/IFAA_field.json' with { type: 'json' };
import waVI from '../../rounds/data/WA_VI.json' with { type: 'json' };
import agbVI from '../../rounds/data/AGB_VI.json' with { type: 'json' };
import aaOutdoorMetric from '../../rounds/data/AA_outdoor_metric.json' with { type: 'json' };
import aaIndoor from '../../rounds/data/AA_indoor.json' with { type: 'json' };
import aaField from '../../rounds/data/AA_field.json' with { type: 'json' };
import miscellaneous from '../../rounds/data/Miscellaneous.json' with { type: 'json' };

export interface Pass {
  nArrows: number;
  target: Target;
}

export function newPass(nArrows: number, target: Target): Pass {
  if (nArrows < 0) nArrows = -nArrows;
  return { nArrows, target };
}

export function atTarget(
  nArrows: number,
  system: ScoringSystem,
  diameter: Quantity,
  distance: Quantity,
  indoor: boolean,
): Pass {
  return newPass(nArrows, Target.create(system, diameter, distance, indoor));
}

export function passMaxScore(p: Pass): number {
  return p.nArrows * p.target.maxScore;
}

export interface Round {
  name: string;
  codename: string;
  passes: Pass[];
  location?: string;
  body?: string;
  family?: string;
  nArrows: number;
}

export function roundMaxScore(r: Round): number {
  return r.passes.reduce((s, p) => s + passMaxScore(p), 0);
}

export function roundMaxDistance(r: Round): Quantity {
  let maxM = 0;
  let result: Quantity = { value: 0, units: 'metre' };
  for (const p of r.passes) {
    if (p.target.distance > maxM) {
      maxM = p.target.distance;
      result = p.target.nativeDistance;
    }
  }
  return result;
}

export function roundInfo(r: Round): string {
  const lines = [`A ${r.name} consists of ${r.passes.length} pass${r.passes.length === 1 ? '' : 'es'}:`];
  for (const p of r.passes) {
    const { value: d, units: du } = p.target.nativeDiameter;
    const { value: di, units: diu } = p.target.nativeDistance;
    lines.push(`\t- ${p.nArrows} arrows at a ${d.toFixed(1)} ${du} target at ${di.toFixed(1)} ${diu}s.`);
  }
  return lines.join('\n');
}

// ---- JSON parsing ----

const INDOOR_ALIASES = new Set(['i', 'I', 'indoors', 'indoor', 'in', 'inside', 'Indoors', 'Indoor', 'In', 'Inside']);
const OUTDOOR_ALIASES = new Set(['o', 'O', 'outdoors', 'outdoor', 'out', 'outside', 'Outdoors', 'Outdoor', 'Out', 'Outside']);
const FIELD_ALIASES = new Set(['f', 'F', 'field', 'Field', 'woods', 'Woods']);

interface PassJSON {
  n_arrows: number;
  diameter: number;
  diameter_unit?: string;
  scoring: string;
  distance: number;
  dist_unit: string;
}

interface RoundJSON {
  name: string;
  codename: string;
  location?: string;
  body?: string;
  family?: string;
  passes: PassJSON[];
}

export function parseRoundsJSON(data: unknown): Map<string, Round> {
  const raw = data as RoundJSON[];
  const out = new Map<string, Round>();
  for (const rj of raw) {
    let location: string | undefined;
    let indoor = false;
    if (rj.location) {
      if (INDOOR_ALIASES.has(rj.location)) { indoor = true; location = 'indoor'; }
      else if (OUTDOOR_ALIASES.has(rj.location)) { location = 'outdoor'; }
      else if (FIELD_ALIASES.has(rj.location)) { location = 'field'; }
    }

    const passes: Pass[] = rj.passes.map(pj => {
      const diamUnit = pj.diameter_unit || 'cm';
      return atTarget(
        pj.n_arrows,
        pj.scoring as ScoringSystem,
        { value: pj.diameter, units: diamUnit },
        { value: pj.distance, units: pj.dist_unit },
        indoor,
      );
    });

    const nArrows = passes.reduce((s, p) => s + p.nArrows, 0);
    out.set(rj.codename, {
      name: rj.name,
      codename: rj.codename,
      passes,
      nArrows,
      ...(location !== undefined ? { location } : {}),
      ...(rj.body ? { body: rj.body } : {}),
      ...(rj.family ? { family: rj.family } : {}),
    });
  }
  return out;
}

// ---- Lazy-loaded caches ----

const cache = new Map<string, Map<string, Round>>();

function loadOnce(key: string, data: unknown): Map<string, Round> {
  if (!cache.has(key)) cache.set(key, parseRoundsJSON(data));
  return cache.get(key)!;
}

export const agbOutdoorImperialRounds  = () => loadOnce('agb_outdoor_imperial', agbOutdoorImperial);
export const agbOutdoorMetricRounds    = () => loadOnce('agb_outdoor_metric', agbOutdoorMetric);
export const agbIndoorRounds           = () => loadOnce('agb_indoor', agbIndoor);
export const waOutdoorRounds           = () => loadOnce('wa_outdoor', waOutdoor);
export const waIndoorRounds            = () => loadOnce('wa_indoor', waIndoor);
export const waFieldRounds             = () => loadOnce('wa_field', waField);
export const waExperimentalRounds      = () => loadOnce('wa_experimental', waExperimental);
export const ifaaFieldRounds           = () => loadOnce('ifaa_field', ifaaField);
export const waVIRounds                = () => loadOnce('wa_vi', waVI);
export const agbVIRounds               = () => loadOnce('agb_vi', agbVI);
export const aaOutdoorMetricRounds     = () => loadOnce('aa_outdoor_metric', aaOutdoorMetric);
export const aaIndoorRounds            = () => loadOnce('aa_indoor', aaIndoor);
export const aaFieldRounds             = () => loadOnce('aa_field', aaField);
export const miscellaneousRounds       = () => loadOnce('miscellaneous', miscellaneous);

export function allRounds(): Map<string, Round> {
  const loaders = [
    agbOutdoorImperialRounds, agbOutdoorMetricRounds, agbIndoorRounds,
    waOutdoorRounds, waIndoorRounds, waFieldRounds, waExperimentalRounds,
    ifaaFieldRounds, waVIRounds, agbVIRounds,
    aaOutdoorMetricRounds, aaIndoorRounds, aaFieldRounds,
    miscellaneousRounds,
  ];
  const out = new Map<string, Round>();
  for (const loader of loaders) {
    for (const [k, v] of loader()) out.set(k, v);
  }
  return out;
}
