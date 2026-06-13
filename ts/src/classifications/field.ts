import { newScheme, scoreForRound } from '../handicaps.js';
import { waFieldRounds, type Round, roundMaxScore } from '../rounds.js';
import {
  type Gender, type Age, type Bowstyle, type Category,
  AllGenders, FieldBowstyles,
  Gender as G, Age as A, Bowstyle as B,
} from './data.js';
import { loadAgeData, loadBowstyleData, loadClassesOut, type AgeData } from './jsonio.js';
import { groupName, getAgeGenderStep, fixRepeatedScores } from './utils.js';

interface FieldGroupData {
  classes: string[];
  classesLong: string[];
  classHC: number[];
  maxDistance: number;
  minDists: number[];
}

let fieldDict: Map<string, FieldGroupData> | null = null;

export const FieldAges: Age[] = [A.Over50, A.Adult, A.Under18, A.Under16, A.Under15, A.Under14, A.Under12];
const SightedBowstyles: Bowstyle[] = [B.Compound, B.Recurve, B.CompoundLimited];

function allFieldRounds(): Map<string, Round> {
  return waFieldRounds();
}

function isSighted(b: Bowstyle): boolean { return SightedBowstyles.includes(b); }

function assignDistsField(bowstyle: Bowstyle, ad: AgeData): [number[], number] {
  const [minD, maxD] = isSighted(bowstyle)
    ? [ad.sighted[0], ad.sighted[1]]
    : [ad.unsighted[0], ad.unsighted[1]];

  const minDists = new Array<number>(9).fill(0);
  for (let i = 0; i < 6; i++) minDists[i] = minD;
  for (let i = 0; i < 3; i++) {
    const v = minD - 10 * (i + 1);
    minDists[6 + i] = v < 30 ? 30 : v;
  }
  return [minDists, maxD];
}

function buildFieldDict(): Map<string, FieldGroupData> {
  if (fieldDict !== null) return fieldDict;
  const agbAgeData = loadAgeData();
  const agbBowstyleData = loadBowstyleData();
  const classInfo = loadClassesOut();
  const { classes, classes_long: classesLong } = classInfo;
  const n = classes.length;

  fieldDict = new Map();
  for (const bowstyle of FieldBowstyles) {
    for (const gender of AllGenders) {
      for (const age of FieldAges) {
        const gname = groupName(bowstyle, gender, age);
        const ad = agbAgeData[age];
        const bd = agbBowstyleData[bowstyle];
        const [minDists, maxDistance] = assignDistsField(bowstyle, ad);
        const ageCat = ad.step;
        const delta = getAgeGenderStep(gender, ageCat, bd.ageStep_field, bd.genderStep_field);
        const hcs = Array.from({ length: n }, (_, i) => bd.datum_field + delta + (i - 2) * bd.classStep_field);
        fieldDict.set(gname, { classes, classesLong, classHC: hcs, maxDistance, minDists });
      }
    }
  }
  return fieldDict;
}

function isFieldBowstyle(b: Bowstyle): boolean { return FieldBowstyles.includes(b); }
function isValidGender(g: Gender): boolean { return g === G.Male || g === G.Female || g === G.Open; }
function isFieldAge(a: Age): boolean { return FieldAges.includes(a); }

function getFieldGroupData(bowstyle: Bowstyle, gender: Gender, age: Age): FieldGroupData {
  if (!isFieldBowstyle(bowstyle))
    throw new Error(`${bowstyle} is not a recognised bowstyle for field classifications`);
  if (!isValidGender(gender))
    throw new Error(`${gender} is not a recognised gender for field classifications`);
  if (!isFieldAge(age))
    throw new Error(`${age} is not a recognised age group for field classifications`);
  const gd = buildFieldDict().get(groupName(bowstyle, gender, age));
  if (!gd) throw new Error(`No field data for group "${groupName(bowstyle, gender, age)}"`);
  return gd;
}

function normaliseFieldRound(roundname: string): string {
  return roundname.replace('unmarked', 'marked').replace('mixed', 'marked');
}

export function coaxFieldGroup(bowstyle: Bowstyle, gender: Gender, age: Age): Category {
  const coaxedAge = age === A.Under21 ? A.Adult : age;
  return { bowstyle, gender, ageGroup: coaxedAge };
}

export function fieldClassificationScores(
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
  strictDistance: boolean,
): number[] {
  const gd = getFieldGroupData(bowstyle, gender, age);
  const allRounds = allFieldRounds();
  let round = archeryRound;
  let roundname = archeryRound.codename;

  if (strictRounds) {
    const normName = normaliseFieldRound(roundname);
    const r = allRounds.get(normName);
    if (!r) {
      throw new Error(`This round is not recognised for field classification. (codename="${roundname}")`);
    }
    round = r;
    roundname = normName;
  }

  const hcScheme = newScheme('AGB');
  const maxScore = roundMaxScore(round);
  const classScores = gd.classHC.map(hc => Math.trunc(scoreForRound(hcScheme, hc, round, 0, true)));

  for (let i = 0; i < gd.classHC.length; i++) {
    const nextScore = Math.trunc(scoreForRound(hcScheme, Math.floor(gd.classHC[i]) + 1, round, 0, true));
    if (nextScore === classScores[i]) {
      classScores[i] = classScores[i] === Math.trunc(maxScore) ? -9999 : classScores[i] + 1;
    }
  }
  fixRepeatedScores(classScores, maxScore);

  if (strictRounds && !roundname.includes('wa_field_24_')) {
    classScores[0] = -9999; classScores[1] = -9999; classScores[2] = -9999;
  }

  if (strictDistance) {
    const roundMaxDist = round.passes.reduce((m, p) => Math.max(m, p.target.distance), 0);
    for (let i = 0; i < classScores.length; i++) {
      if (gd.minDists[i] > roundMaxDist) classScores[i] = -9999;
      if (gd.maxDistance < roundMaxDist) classScores[i] = -9999;
    }
  }

  return classScores;
}

export function calculateFieldClassification(
  score: number,
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
  strictDistance: boolean,
): string {
  if (strictRounds) {
    const allRounds = allFieldRounds();
    const normName = normaliseFieldRound(archeryRound.codename);
    const r = allRounds.get(normName);
    if (!r) {
      throw new Error(`This round is not recognised for field classification. (codename="${archeryRound.codename}")`);
    }
    archeryRound = r;
  }
  const maxScore = roundMaxScore(archeryRound);
  if (score < 0 || score > maxScore) {
    throw new Error(
      `Invalid score of ${Math.trunc(score)} for a ${archeryRound.name}. Should be in range 0-${Math.trunc(maxScore)}.`
    );
  }
  const scores = fieldClassificationScores(archeryRound, bowstyle, gender, age, strictRounds, strictDistance);
  const gd = getFieldGroupData(bowstyle, gender, age);
  for (let i = 0; i < gd.classes.length; i++) {
    if (scores[i] < 0 || scores[i] > score) continue;
    return gd.classes[i];
  }
  return 'UC';
}
