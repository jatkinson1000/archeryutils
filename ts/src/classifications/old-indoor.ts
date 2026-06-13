import { newScheme, scoreForRound } from '../handicaps.js';
import { agbIndoorRounds, waIndoorRounds, type Round } from '../rounds.js';
import {
  type Gender, type Age, type Bowstyle, type Category,
  Age as A, Bowstyle as B, Gender as G,
} from './data.js';
import { groupName, compoundCodename, stripSpots } from './utils.js';

interface OldIndoorGroupData {
  classes: string[];
  classHC: number[];
}

export const OldIndoorBowstyles: Bowstyle[] = [B.Compound, B.Recurve];

const OLD_INDOOR_HC: Record<string, number[]> = {
  [groupName(B.Compound, G.Male,   A.Adult)]: [5,  12, 24, 37, 49, 62, 73, 79],
  [groupName(B.Compound, G.Female, A.Adult)]: [12, 18, 30, 43, 55, 67, 79, 83],
  [groupName(B.Recurve,  G.Male,   A.Adult)]: [14, 21, 33, 46, 58, 70, 80, 85],
  [groupName(B.Recurve,  G.Female, A.Adult)]: [21, 27, 39, 51, 64, 75, 85, 90],
};

const OLD_INDOOR_CLASSES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

function allIndoorRounds(): Map<string, Round> {
  const m = new Map<string, Round>();
  for (const [k, v] of agbIndoorRounds()) m.set(k, v);
  for (const [k, v] of waIndoorRounds()) m.set(k, v);
  return m;
}

function isOldIndoorBowstyle(b: Bowstyle): boolean { return OldIndoorBowstyles.includes(b); }

function getOldIndoorGroupData(bowstyle: Bowstyle, gender: Gender, age: Age): OldIndoorGroupData {
  if (!isOldIndoorBowstyle(bowstyle))
    throw new Error(`${bowstyle} is not a recognised bowstyle for old indoor classifications`);
  if (gender !== G.Male && gender !== G.Female)
    throw new Error(`${gender} is not a recognised gender for old indoor classifications`);
  if (age !== A.Adult)
    throw new Error(`${age} is not a recognised age group for old indoor classifications (only Adult)`);
  const hcs = OLD_INDOOR_HC[groupName(bowstyle, gender, age)];
  if (!hcs) throw new Error(`No old indoor data for group "${groupName(bowstyle, gender, age)}"`);
  return { classes: OLD_INDOOR_CLASSES, classHC: hcs };
}

export function coaxOldIndoorGroup(bowstyle: Bowstyle, gender: Gender, _age: Age): Category {
  let coaxed = B.Recurve as Bowstyle;
  if (bowstyle === B.Compound || bowstyle === B.CompoundLimited || bowstyle === B.CompoundBarebow) {
    coaxed = B.Compound;
  }
  return { bowstyle: coaxed, gender, ageGroup: A.Adult };
}

export function oldIndoorClassificationScores(
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
): number[] {
  const gd = getOldIndoorGroupData(bowstyle, gender, age);
  const allRounds = allIndoorRounds();
  let round = archeryRound;
  let roundname = archeryRound.codename;

  if (strictRounds) {
    if (!allRounds.has(roundname)) {
      throw new Error(
        `This round is not recognised for old indoor classification. Please select an appropriate option. (codename="${roundname}")`
      );
    }
    if (bowstyle === B.Compound) {
      roundname = compoundCodename(roundname);
      const r = allRounds.get(roundname);
      if (r) round = r;
    }
    for (const name of ['portsmouth', 'worcester', 'bray_i', 'bray_ii']) {
      if (roundname.includes(name)) {
        const stripped = allRounds.get(stripSpots(roundname));
        if (stripped) round = stripped;
        break;
      }
    }
  }

  const hcScheme = newScheme('AGBold');
  return gd.classHC.map(hc => Math.trunc(scoreForRound(hcScheme, hc, round, 0, true)));
}

export function calculateOldIndoorClassification(
  score: number,
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
  strictRounds: boolean,
): string {
  const maxScore = archeryRound.passes.reduce((s, p) => s + p.nArrows * p.target.maxScore, 0);
  if (score < 0 || score > maxScore) {
    throw new Error(
      `Invalid score of ${Math.trunc(score)} for a ${archeryRound.name}. Should be in range 0-${Math.trunc(maxScore)}.`
    );
  }
  const scores = oldIndoorClassificationScores(archeryRound, bowstyle, gender, age, strictRounds);
  const gd = getOldIndoorGroupData(bowstyle, gender, age);
  for (let i = 0; i < gd.classes.length; i++) {
    if (scores[i] > score) continue;
    return gd.classes[i];
  }
  return 'UC';
}
