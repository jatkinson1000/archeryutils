import { type Bowstyle, type Gender, type Age } from './data.js';

export function groupName(bowstyle: Bowstyle, gender: Gender, age: Age): string {
  return `${age}_${gender}_${bowstyle}`;
}

export function getAgeGenderStep(gender: Gender, ageCat: number, ageStep: number, genderStep: number): number {
  const UNDER16_INT = 3;
  if (gender === 'FEMALE' && ageCat === UNDER16_INT && ageStep < genderStep) {
    return ageCat * ageStep + ageStep;
  }
  if (gender === 'FEMALE' && ageCat <= UNDER16_INT) {
    return genderStep + ageCat * ageStep;
  }
  return ageCat * ageStep;
}

export function stripSpots(roundname: string): string {
  return roundname.replace('_triple', '').replace('_5_centre', '').replace('_small', '');
}

export function compoundCodename(codename: string): string {
  const conv: Record<string, string> = {
    bray_i:              'bray_i_compound',
    bray_i_triple:       'bray_i_compound_triple',
    bray_ii:             'bray_ii_compound',
    bray_ii_triple:      'bray_ii_compound_triple',
    stafford:            'stafford_compound',
    portsmouth:          'portsmouth_compound',
    portsmouth_triple:   'portsmouth_compound_triple',
    vegas:               'vegas_compound',
    wa18:                'wa18_compound',
    wa18_triple:         'wa18_compound_triple',
    wa25:                'wa25_compound',
    wa25_triple:         'wa25_compound_triple',
  };
  return conv[codename] ?? codename;
}

export function classHCs(datum: number, deltaHCAgeGender: number, classStep: number, n: number): number[] {
  return Array.from({ length: n }, (_, i) => datum + deltaHCAgeGender + (i - 2) * classStep);
}

export function minFloats(xs: number[]): number {
  if (xs.length === 0) return Infinity;
  return Math.min(...xs);
}

export function distIndex(dists: number[], d: number): number {
  return dists.indexOf(d);
}

export function takeClip(arr: number[], idxs: number[], offset: number): number[] {
  return idxs.map(idx => {
    let j = idx + offset;
    if (j < 0) j = 0;
    if (j >= arr.length) j = arr.length - 1;
    return arr[j];
  });
}

export function fixRepeatedScores(scores: number[], maxScore: number): number[] {
  for (let i = scores.length - 1; i > 0; i--) {
    if (scores[i] < 0) {
      scores[i - 1] = -9999;
    } else if (scores[i - 1] >= 0 && scores[i - 1] <= scores[i]) {
      if (scores[i] === Math.trunc(maxScore)) {
        scores[i - 1] = -9999;
      } else {
        scores[i - 1] = scores[i] + 1;
      }
    }
  }
  return scores;
}
