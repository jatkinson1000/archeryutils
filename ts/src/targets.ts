import { toMetres, definitiveUnit, SUPPORTED_DIAM_UNITS, SUPPORTED_DIST_UNITS } from './length.js';

export type ScoringSystem =
  | '5_zone' | '10_zone' | '10_zone_compound' | '10_zone_6_ring'
  | '10_zone_5_ring' | '10_zone_5_ring_compound' | '11_zone'
  | '11_zone_6_ring' | '11_zone_5_ring' | 'WA_field' | 'IFAA_field'
  | 'IFAA_field_expert' | 'AA_national_field' | 'Beiter_hit_miss'
  | 'Worcester' | 'Worcester_2_ring' | 'Custom';

export const ScoringSystem = {
  FiveZone: '5_zone' as ScoringSystem,
  TenZone: '10_zone' as ScoringSystem,
  TenZoneCompound: '10_zone_compound' as ScoringSystem,
  TenZoneSixRing: '10_zone_6_ring' as ScoringSystem,
  TenZoneFiveRing: '10_zone_5_ring' as ScoringSystem,
  TenZoneFiveRingCmpd: '10_zone_5_ring_compound' as ScoringSystem,
  ElevenZone: '11_zone' as ScoringSystem,
  ElevenZoneSixRing: '11_zone_6_ring' as ScoringSystem,
  ElevenZoneFiveRing: '11_zone_5_ring' as ScoringSystem,
  WAField: 'WA_field' as ScoringSystem,
  IFAAField: 'IFAA_field' as ScoringSystem,
  IFAAFieldExpert: 'IFAA_field_expert' as ScoringSystem,
  AANationalField: 'AA_national_field' as ScoringSystem,
  BeiterHitMiss: 'Beiter_hit_miss' as ScoringSystem,
  Worcester: 'Worcester' as ScoringSystem,
  Worcester2Ring: 'Worcester_2_ring' as ScoringSystem,
  Custom: 'Custom' as ScoringSystem,
} as const;

const SUPPORTED_SYSTEMS = new Set<string>([
  '5_zone', '10_zone', '10_zone_compound', '10_zone_6_ring',
  '10_zone_5_ring', '10_zone_5_ring_compound', '11_zone',
  '11_zone_6_ring', '11_zone_5_ring', 'WA_field', 'IFAA_field',
  'IFAA_field_expert', 'AA_national_field', 'Beiter_hit_miss',
  'Worcester', 'Worcester_2_ring', 'Custom',
]);

/** Maps each ring diameter (metres) to its score value. */
export type FaceSpec = Map<number, number>;

export interface Quantity {
  value: number;
  units: string;
}

export function cm(v: number): Quantity { return { value: v, units: 'cm' }; }
export function metres(v: number): Quantity { return { value: v, units: 'metre' }; }
export function yards(v: number): Quantity { return { value: v, units: 'yard' }; }
export function inches(v: number): Quantity { return { value: v, units: 'inch' }; }

function rnd6(x: number): number {
  return Math.round(x * 1e6) / 1e6;
}

function resolveQuantity(q: Quantity, supportedAliases: Set<string>): [number, string] {
  const unitAlias = q.units || 'cm';
  if (!supportedAliases.has(unitAlias)) {
    throw new Error(`Unit "${unitAlias}" not recognised.`);
  }
  const def = definitiveUnit(unitAlias);
  return [q.value, def];
}

export class Target {
  private constructor(
    private readonly _diameter: number,       // metres
    private readonly _distance: number,       // metres
    private readonly _nativeDiameter: Quantity,
    private readonly _nativeDistance: Quantity,
    private readonly _scoringSystem: ScoringSystem,
    private readonly _indoor: boolean,
    private readonly _faceSpec: FaceSpec,
  ) {}

  get scoringSystem(): ScoringSystem { return this._scoringSystem; }
  get diameter(): number { return this._diameter; }
  get distance(): number { return this._distance; }
  get nativeDiameter(): Quantity { return this._nativeDiameter; }
  get nativeDistance(): Quantity { return this._nativeDistance; }
  get indoor(): boolean { return this._indoor; }

  get faceSpec(): FaceSpec {
    if (!this._faceSpec) {
      throw new Error(
        'No face spec available for custom target — use Target.fromFaceSpec() instead'
      );
    }
    return new Map(this._faceSpec);
  }

  get maxScore(): number {
    let max = 0;
    for (const v of this._faceSpec.values()) {
      if (v > max) max = v;
    }
    return max;
  }

  get minScore(): number {
    let min = Infinity;
    for (const v of this._faceSpec.values()) {
      if (v < min) min = v;
    }
    return min === Infinity ? 0 : min;
  }

  static create(
    system: ScoringSystem,
    diameter: Quantity,
    distance: Quantity,
    indoor: boolean,
  ): Target {
    if (!SUPPORTED_SYSTEMS.has(system)) {
      throw new Error(
        `Invalid Target Face Type specified. Please select from ${[...SUPPORTED_SYSTEMS].map(s => `'${s}'`).join(', ')}.`
      );
    }
    const [diamVal, diamUnit] = resolveQuantity(diameter, SUPPORTED_DIAM_UNITS);
    const [distVal, distUnit] = resolveQuantity(distance, SUPPORTED_DIST_UNITS);
    const diamM = toMetres(diamVal, diamUnit);
    const distM = toMetres(distVal, distUnit);
    const spec = system !== 'Custom' ? genFaceSpec(system, diamM) : new Map<number, number>();
    return new Target(
      diamM, distM,
      { value: diamVal, units: diamUnit },
      { value: distVal, units: distUnit },
      system, indoor, spec,
    );
  }

  static fromFaceSpec(
    spec: FaceSpec | [FaceSpec, string],
    diameter: Quantity,
    distance: Quantity,
    indoor: boolean,
  ): Target {
    let rawSpec: FaceSpec;
    let specUnit: string;
    if (spec instanceof Map) {
      rawSpec = spec;
      specUnit = 'metre';
    } else {
      [rawSpec, specUnit] = spec;
    }
    const def = definitiveUnit(specUnit);
    const converted = new Map<number, number>();
    for (const [ringDiam, score] of rawSpec) {
      converted.set(rnd6(toMetres(ringDiam, def)), score);
    }
    const base = Target.create('Custom', diameter, distance, indoor);
    return new Target(
      base._diameter, base._distance,
      base._nativeDiameter, base._nativeDistance,
      'Custom', indoor, converted,
    );
  }

  equals(other: Target): boolean {
    if (this === other) return true;
    if (
      this._scoringSystem !== other._scoringSystem ||
      this._diameter !== other._diameter ||
      this._distance !== other._distance ||
      this._nativeDiameter.value !== other._nativeDiameter.value ||
      this._nativeDiameter.units !== other._nativeDiameter.units ||
      this._nativeDistance.value !== other._nativeDistance.value ||
      this._nativeDistance.units !== other._nativeDistance.units ||
      this._indoor !== other._indoor ||
      this._faceSpec.size !== other._faceSpec.size
    ) return false;
    for (const [k, v] of this._faceSpec) {
      if (other._faceSpec.get(k) !== v) return false;
    }
    return true;
  }

  toString(): string {
    const { value: d, units: du } = this._nativeDiameter;
    const { value: di, units: diu } = this._nativeDistance;
    return `Target('${this._scoringSystem}', (${d}, '${du}'), (${di}, '${diu}'), indoor=${this._indoor})`;
  }
}

export function genFaceSpec(system: ScoringSystem, diameter: number): FaceSpec {
  const spec = new Map<number, number>();
  const REMOVED: Partial<Record<ScoringSystem, number>> = {
    '10_zone_6_ring': 4,
    '10_zone_5_ring': 5,
    '10_zone_5_ring_compound': 5,
    '11_zone_6_ring': 4,
    '11_zone_5_ring': 5,
    'Worcester_2_ring': 3,
  };
  const missing = REMOVED[system] ?? 0;

  switch (system) {
    case '5_zone':
      for (let n = 1; n <= 10; n += 2) {
        spec.set(rnd6((n + 1) * diameter / 10), 10 - n);
      }
      break;
    case '10_zone':
    case '10_zone_6_ring':
    case '10_zone_5_ring':
      for (let n = 1; n <= 10 - missing; n++) {
        spec.set(rnd6(n * diameter / 10), 11 - n);
      }
      break;
    case '10_zone_compound':
    case '10_zone_5_ring_compound':
      spec.set(rnd6(diameter / 20), 10);
      for (let n = 2; n <= 10 - missing; n++) {
        spec.set(rnd6(n * diameter / 10), 11 - n);
      }
      break;
    case '11_zone':
    case '11_zone_6_ring':
    case '11_zone_5_ring':
      spec.set(rnd6(diameter / 20), 11);
      for (let n = 1; n <= 10 - missing; n++) {
        spec.set(rnd6(n * diameter / 10), 11 - n);
      }
      break;
    case 'WA_field':
      spec.set(rnd6(diameter / 10), 6);
      for (let n = 1; n <= 5; n++) {
        spec.set(rnd6(n * diameter / 5), 6 - n);
      }
      break;
    case 'IFAA_field':
      for (const n of [1, 3, 5]) {
        spec.set(rnd6(n * diameter / 5), 5 - Math.floor(n / 2));
      }
      break;
    case 'AA_national_field':
      for (let n = 1; n <= 5; n++) {
        spec.set(rnd6(n * diameter / 5), 6 - n);
      }
      break;
    case 'Beiter_hit_miss':
      spec.set(diameter, 1);
      break;
    case 'Worcester':
    case 'Worcester_2_ring':
    case 'IFAA_field_expert':
      for (let n = 1; n <= 5 - missing; n++) {
        spec.set(rnd6(n * diameter / 5), 6 - n);
      }
      break;
    default:
      throw new Error(`Scoring system "${system}" is not supported`);
  }
  return spec;
}

export function sortedKeys(fs: FaceSpec): number[] {
  return [...fs.keys()].sort((a, b) => a - b);
}
