import { type Gender } from './data.js';

import agbAgesRaw    from '../../../classifications/data/AGB_ages.json' with { type: 'json' };
import agbBowstylesRaw from '../../../classifications/data/AGB_bowstyles.json' with { type: 'json' };
import agbClassesOutRaw from '../../../classifications/data/AGB_classes_out.json' with { type: 'json' };
import agbClassesInRaw  from '../../../classifications/data/AGB_classes_in.json' with { type: 'json' };

export interface AgeData {
  age_group: string;
  open: number[];
  female: number[];
  sighted: number[];
  unsighted: number[];
  step: number;
}

export interface BowstyleData {
  bowstyle: string;
  datum_out: number;
  classStep_out: number;
  genderStep_out: number;
  ageStep_out: number;
  datum_in: number;
  classStep_in: number;
  genderStep_in: number;
  ageStep_in: number;
  datum_field: number;
  classStep_field: number;
  genderStep_field: number;
  ageStep_field: number;
}

export interface ClassificationData {
  location: string;
  classes: string[];
  classes_long: string[];
}

let ageDataCache: Record<string, AgeData> | null = null;
let bowstyleDataCache: Record<string, BowstyleData> | null = null;
let classesOutCache: ClassificationData | null = null;
let classesInCache: ClassificationData | null = null;

export function loadAgeData(): Record<string, AgeData> {
  if (!ageDataCache) ageDataCache = agbAgesRaw as unknown as Record<string, AgeData>;
  return ageDataCache;
}

export function loadBowstyleData(): Record<string, BowstyleData> {
  if (!bowstyleDataCache) bowstyleDataCache = agbBowstylesRaw as unknown as Record<string, BowstyleData>;
  return bowstyleDataCache;
}

export function loadClassesOut(): ClassificationData {
  if (!classesOutCache) classesOutCache = agbClassesOutRaw as unknown as ClassificationData;
  return classesOutCache;
}

export function loadClassesIn(): ClassificationData {
  if (!classesInCache) classesInCache = agbClassesInRaw as unknown as ClassificationData;
  return classesInCache;
}

export function maxDistsForGender(ad: AgeData, g: Gender): number[] {
  return g === 'FEMALE' ? ad.female : ad.open;
}
