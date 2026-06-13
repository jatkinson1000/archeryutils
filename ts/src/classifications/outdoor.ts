import { newScheme, scoreForRound } from '../handicaps.js';
import { waOutdoorRounds, agbOutdoorImperialRounds, agbOutdoorMetricRounds, type Round, roundMaxScore } from '../rounds.js';
import {
  type Gender, type Age, type Bowstyle, type Category,
  AllGenders, AllAges, OutdoorBowstyles,
  Gender as G, Age as A, Bowstyle as B,
} from './data.js';
import {
  loadAgeData, loadBowstyleData, loadClassesOut, maxDistsForGender,
} from './jsonio.js';
import {
  groupName, getAgeGenderStep, classHCs, stripSpots,
  minFloats, distIndex, takeClip, fixRepeatedScores,
} from './utils.js';

interface OutdoorGroupData {
  classes: string[];
  classesLong: string[];
  classHC: number[];
  minDists: number[];
  maxDists: number[];
  prestigeRounds: string[];
}

let outdoorDict: Map<string, OutdoorGroupData> | null = null;

// Standard outdoor distance ladder (metres)
const STD_DISTS = [90, 70, 60, 50, 40, 30, 20, 15];

function allOutdoorRounds(): Map<string, Round> {
  const m = new Map<string, Round>();
  for (const [k, v] of agbOutdoorImperialRounds()) m.set(k, v);
  for (const [k, v] of agbOutdoorMetricRounds()) m.set(k, v);
  for (const [k, v] of waOutdoorRounds()) m.set(k, v);
  return m;
}

function assignMinDistOutdoor(gender: Gender, age: Age, maxDists: number[]): number[] {
  const minMaxDist = minFloats(maxDists);
  let maxDistIdx = distIndex(STD_DISTS, minMaxDist);
  if (maxDistIdx < 0) maxDistIdx = 0;

  const youngMale = age === A.Under15 || age === A.Under14 || age === A.Under12;
  const idxs = (gender !== G.Female && !youngMale)
    ? [0, 0, 0, 0, 1, 2, 3, 4, 5]
    : [0, 0, 0, 0, 0, 1, 2, 3, 4];
  return takeClip(STD_DISTS, idxs, maxDistIdx);
}

function assignOutdoorPrestige(bowstyle: Bowstyle, gender: Gender, age: Age, maxDists: number[]): string[] {
  const prestigeImperial = [
    'york', 'hereford', 'bristol_i', 'bristol_ii', 'bristol_iii', 'bristol_iv', 'bristol_v',
  ];
  const prestigeMetric = [
    'wa1440_90', 'wa1440_90_small', 'wa1440_70', 'wa1440_70_small',
    'wa1440_60', 'wa1440_60_small',
    'metric_i', 'metric_ii', 'metric_iii', 'metric_iv', 'metric_v',
  ];
  const prestige720 = [
    'wa720_70', 'wa720_60', 'metric_122_50', 'wa720_40', 'metric_122_40', 'metric_122_30',
  ];
  const prestige720Compound = [
    'wa720_50_c', 'metric_80_50', 'wa720_40_c', 'metric_80_40', 'metric_80_30',
  ];
  const prestige720Barebow = [
    'wa720_50_b', 'metric_122_50', 'wa720_40', 'metric_122_40', 'wa720_30_b', 'metric_122_30',
  ];

  const youngJunior = age === A.Under15 || age === A.Under14 || age === A.Under12;
  let prestige: string[] = [];
  let distCheck: string[] = [];

  if (bowstyle === B.Compound) {
    prestige.push(...prestige720Compound.slice(0, 2));
    distCheck.push(...prestige720Compound.slice(2));
    if (youngJunior) prestige.push(...prestige720Compound.slice(2, 4));
  } else if (bowstyle === B.Barebow) {
    prestige.push(prestige720Barebow[0]);
    distCheck.push(...prestige720Barebow.slice(1));
    if (youngJunior) prestige.push(...prestige720Barebow.slice(2));
  } else {
    prestige.push(prestige720[0]);
    distCheck.push(...prestige720.slice(1));
    if (youngJunior) prestige.push(...prestige720.slice(3, 5));
    if (gender === G.Open || gender === G.Male) {
      if (age === A.Over50 || age === A.Under18) {
        prestige.push(prestige720[1]);
      } else if (age === A.Under16) {
        prestige.push(prestige720[2]);
      }
    }
  }

  distCheck.push(...prestigeImperial, ...prestigeMetric);
  const minMaxDist = minFloats(maxDists);
  const allRounds = allOutdoorRounds();
  for (const rname of distCheck) {
    const r = allRounds.get(rname);
    if (r) {
      const md = r.passes.reduce((m, p) => Math.max(m, p.target.distance), 0);
      if (md >= minMaxDist) prestige.push(rname);
    }
  }
  return prestige;
}

function buildOutdoorDict(): Map<string, OutdoorGroupData> {
  if (outdoorDict !== null) return outdoorDict;
  const agbAgeData = loadAgeData();
  const agbBowstyleData = loadBowstyleData();
  const classInfo = loadClassesOut();
  const { classes, classes_long: classesLong } = classInfo;
  const n = classes.length;

  outdoorDict = new Map();
  for (const bowstyle of OutdoorBowstyles) {
    for (const gender of AllGenders) {
      for (const age of AllAges) {
        const gname = groupName(bowstyle, gender, age);
        const ad = agbAgeData[age];
        const bd = agbBowstyleData[bowstyle];
        const maxDists = maxDistsForGender(ad, gender);
        const ageCat = ad.step;
        const delta = getAgeGenderStep(gender, ageCat, bd.ageStep_out, bd.genderStep_out);
        const hcs = classHCs(bd.datum_out, delta, bd.classStep_out, n);
        const minDists = assignMinDistOutdoor(gender, age, maxDists);
        const prestige = assignOutdoorPrestige(bowstyle, gender, age, maxDists);
        outdoorDict.set(gname, { classes, classesLong, classHC: hcs, minDists, maxDists, prestigeRounds: prestige });
      }
    }
  }
  return outdoorDict;
}

function isOutdoorBowstyle(b: Bowstyle): boolean { return OutdoorBowstyles.includes(b); }
function isValidGender(g: Gender): boolean { return g === G.Male || g === G.Female || g === G.Open; }
function isValidAge(a: Age): boolean { return AllAges.includes(a); }

function getOutdoorGroupData(bowstyle: Bowstyle, gender: Gender, age: Age): OutdoorGroupData {
  if (!isOutdoorBowstyle(bowstyle))
    throw new Error(`${bowstyle} is not a recognised bowstyle for outdoor classifications`);
  if (!isValidGender(gender))
    throw new Error(`${gender} is not a recognised gender for outdoor classifications`);
  if (!isValidAge(age))
    throw new Error(`${age} is not a recognised age group for outdoor classifications`);
  const gd = buildOutdoorDict().get(groupName(bowstyle, gender, age));
  if (!gd) throw new Error(`No outdoor data for group "${groupName(bowstyle, gender, age)}"`);
  return gd;
}

export function coaxOutdoorGroup(bowstyle: Bowstyle, gender: Gender, age: Age): Category {
  let coaxed = bowstyle;
  if (bowstyle === B.Flatbow || bowstyle === B.Traditional) coaxed = B.Barebow;
  else if (bowstyle === B.CompoundLimited || bowstyle === B.CompoundBarebow) coaxed = B.Compound;
  return { bowstyle: coaxed, gender, ageGroup: age };
}

export function outdoorClassificationScores(
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
  strictDistance: boolean,
): number[] {
  const gd = getOutdoorGroupData(bowstyle, gender, age);
  const allRounds = allOutdoorRounds();
  let round = archeryRound;
  let roundname = archeryRound.codename;

  if (strictRounds) {
    if (!allRounds.has(roundname)) {
      throw new Error(
        `This round is not recognised for outdoor classification. Please select an appropriate option. (codename="${roundname}")`
      );
    }
    const base = stripSpots(roundname);
    const baseRound = allRounds.get(base);
    if (baseRound) round = baseRound;
  }

  const hcScheme = newScheme('AGB');
  const classScores = gd.classHC.map(hc => Math.trunc(scoreForRound(hcScheme, hc, round, 0, true)));

  // Gap/max-score handling
  const maxScore = roundMaxScore(round);
  for (let i = 0; i < gd.classHC.length; i++) {
    const nextScore = Math.trunc(scoreForRound(hcScheme, Math.floor(gd.classHC[i]) + 1, round, 0, true));
    if (nextScore === classScores[i]) {
      classScores[i] = classScores[i] === Math.trunc(maxScore) ? -9999 : classScores[i] + 1;
    }
  }
  fixRepeatedScores(classScores, maxScore);

  if (strictRounds) {
    const isPrestige = gd.prestigeRounds.includes(roundname);
    if (!isPrestige) { classScores[0] = -9999; classScores[1] = -9999; classScores[2] = -9999; }
  }

  if (strictDistance) {
    const isPrestige = strictRounds && gd.prestigeRounds.includes(roundname);
    if (!isPrestige) {
      const roundMaxDist = round.passes.reduce((m, p) => Math.max(m, p.target.distance), 0);
      for (let i = 0; i < classScores.length; i++) {
        if (gd.minDists[i] > roundMaxDist) classScores[i] = -9999;
      }
    }
  }

  return classScores;
}

export function calculateOutdoorClassification(
  score: number,
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
  strictDistance: boolean,
): string {
  const maxScore = roundMaxScore(archeryRound);
  if (score < 0 || score > maxScore) {
    throw new Error(
      `Invalid score of ${Math.trunc(score)} for a ${archeryRound.name}. Should be in range 0-${Math.trunc(maxScore)}.`
    );
  }
  const scores = outdoorClassificationScores(archeryRound, bowstyle, gender, age, strictRounds, strictDistance);
  const gd = getOutdoorGroupData(bowstyle, gender, age);
  for (let i = 0; i < gd.classes.length; i++) {
    if (scores[i] < 0 || scores[i] > score) continue;
    return gd.classes[i];
  }
  return 'UC';
}
