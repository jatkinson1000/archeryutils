import { newScheme, scoreForRound } from '../handicaps.js';
import { agbIndoorRounds, waIndoorRounds, type Round, roundMaxScore } from '../rounds.js';
import {
  type Gender, type Age, type Bowstyle, type Category,
  AllGenders, AllAges, IndoorBowstyles,
  Gender as G, Bowstyle as B,
} from './data.js';
import { loadAgeData, loadBowstyleData, loadClassesIn } from './jsonio.js';
import { groupName, getAgeGenderStep, stripSpots, compoundCodename, fixRepeatedScores } from './utils.js';

interface IndoorGroupData {
  classes: string[];
  classesLong: string[];
  classHC: number[];
}

let indoorDict: Map<string, IndoorGroupData> | null = null;

function allIndoorRounds(): Map<string, Round> {
  const m = new Map<string, Round>();
  for (const [k, v] of agbIndoorRounds()) m.set(k, v);
  for (const [k, v] of waIndoorRounds()) m.set(k, v);
  return m;
}

function buildIndoorDict(): Map<string, IndoorGroupData> {
  if (indoorDict !== null) return indoorDict;
  const agbAgeData = loadAgeData();
  const agbBowstyleData = loadBowstyleData();
  const classInfo = loadClassesIn();
  const { classes, classes_long: classesLong } = classInfo;
  const n = classes.length;

  indoorDict = new Map();
  for (const bowstyle of IndoorBowstyles) {
    for (const gender of AllGenders) {
      for (const age of AllAges) {
        const gname = groupName(bowstyle, gender, age);
        const ad = agbAgeData[age];
        const bd = agbBowstyleData[bowstyle];
        const ageCat = ad.step;
        const delta = getAgeGenderStep(gender, ageCat, bd.ageStep_in, bd.genderStep_in);
        const hcs = Array.from({ length: n }, (_, i) => bd.datum_in + delta + (i - 1) * bd.classStep_in);
        indoorDict.set(gname, { classes, classesLong, classHC: hcs });
      }
    }
  }
  return indoorDict;
}

function isIndoorBowstyle(b: Bowstyle): boolean { return IndoorBowstyles.includes(b); }
function isValidGender(g: Gender): boolean { return g === G.Male || g === G.Female || g === G.Open; }
function isValidAge(a: Age): boolean { return AllAges.includes(a); }

function getIndoorGroupData(bowstyle: Bowstyle, gender: Gender, age: Age): IndoorGroupData {
  if (!isIndoorBowstyle(bowstyle))
    throw new Error(`${bowstyle} is not a recognised bowstyle for indoor classifications`);
  if (!isValidGender(gender))
    throw new Error(`${gender} is not a recognised gender for indoor classifications`);
  if (!isValidAge(age))
    throw new Error(`${age} is not a recognised age group for indoor classifications`);
  const gd = buildIndoorDict().get(groupName(bowstyle, gender, age));
  if (!gd) throw new Error(`No indoor data for group "${groupName(bowstyle, gender, age)}"`);
  return gd;
}

export function coaxIndoorGroup(bowstyle: Bowstyle, gender: Gender, age: Age): Category {
  let coaxed = bowstyle;
  if (bowstyle === B.Flatbow || bowstyle === B.Traditional) coaxed = B.Barebow;
  else if (bowstyle === B.CompoundLimited || bowstyle === B.CompoundBarebow) coaxed = B.Compound;
  return { bowstyle: coaxed, gender, ageGroup: age };
}

export function indoorClassificationScores(
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
): number[] {
  const gd = getIndoorGroupData(bowstyle, gender, age);
  const allRounds = allIndoorRounds();
  let round = archeryRound;
  let roundname = archeryRound.codename;

  if (strictRounds) {
    if (!allRounds.has(roundname)) {
      throw new Error(
        `This round is not recognised for indoor classification. Please select an appropriate option. (codename="${roundname}")`
      );
    }
    if (bowstyle === B.Compound) roundname = compoundCodename(roundname);
    const stripped = allRounds.get(stripSpots(roundname));
    if (stripped) round = stripped;
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

  return classScores;
}

export function calculateIndoorClassification(
  score: number,
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
): string {
  const maxScore = roundMaxScore(archeryRound);
  if (score < 0 || score > maxScore) {
    throw new Error(
      `Invalid score of ${Math.trunc(score)} for a ${archeryRound.name}. Should be in range 0-${Math.trunc(maxScore)}.`
    );
  }
  const scores = indoorClassificationScores(archeryRound, bowstyle, gender, age, strictRounds);
  const gd = getIndoorGroupData(bowstyle, gender, age);
  for (let i = 0; i < gd.classes.length; i++) {
    if (scores[i] < 0 || scores[i] > score) continue;
    return gd.classes[i];
  }
  return 'UC';
}
