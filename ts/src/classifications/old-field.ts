import { waFieldRounds, type Round } from '../rounds.js';
import {
  type Gender, type Age, type Bowstyle, type Category,
  FieldBowstyles, Age as A, Bowstyle as B, Gender as G,
} from './data.js';

export const OldFieldClasses = ['GMB', 'MB', 'B', '1C', '2C', '3C'];
export const OldFieldAges: Age[] = [A.Adult, A.Under18];

const SightedBowstyles: Bowstyle[] = [B.Compound, B.Recurve, B.CompoundLimited];

function isSighted(b: Bowstyle): boolean { return SightedBowstyles.includes(b); }

type OldFieldKey = `${Bowstyle}|${Gender}|${Age}`;
function makeKey(b: Bowstyle, g: Gender, a: Age): OldFieldKey {
  return `${b}|${g}|${a}` as OldFieldKey;
}

const OLD_FIELD_SCORES: Record<string, number[]> = {
  [makeKey(B.Compound,        G.Male,   A.Adult)]:   [393, 377, 344, 312, 279, 247],
  [makeKey(B.Compound,        G.Female, A.Adult)]:   [376, 361, 330, 299, 268, 237],
  [makeKey(B.Recurve,         G.Male,   A.Adult)]:   [338, 317, 288, 260, 231, 203],
  [makeKey(B.Recurve,         G.Female, A.Adult)]:   [322, 302, 275, 247, 220, 193],
  [makeKey(B.Barebow,         G.Male,   A.Adult)]:   [328, 307, 279, 252, 224, 197],
  [makeKey(B.Barebow,         G.Female, A.Adult)]:   [303, 284, 258, 233, 207, 182],
  [makeKey(B.Longbow,         G.Male,   A.Adult)]:   [201, 188, 171, 155, 137, 121],
  [makeKey(B.Longbow,         G.Female, A.Adult)]:   [152, 142, 129, 117, 103, 91],
  [makeKey(B.Traditional,     G.Male,   A.Adult)]:   [262, 245, 223, 202, 178, 157],
  [makeKey(B.Traditional,     G.Female, A.Adult)]:   [197, 184, 167, 152, 134, 118],
  [makeKey(B.Flatbow,         G.Male,   A.Adult)]:   [262, 245, 223, 202, 178, 157],
  [makeKey(B.Flatbow,         G.Female, A.Adult)]:   [197, 184, 167, 152, 134, 118],
  [makeKey(B.CompoundLimited, G.Male,   A.Adult)]:   [338, 317, 288, 260, 231, 203],
  [makeKey(B.CompoundLimited, G.Female, A.Adult)]:   [322, 302, 275, 247, 220, 193],
  [makeKey(B.CompoundBarebow, G.Male,   A.Adult)]:   [328, 307, 279, 252, 224, 197],
  [makeKey(B.CompoundBarebow, G.Female, A.Adult)]:   [303, 284, 258, 233, 207, 182],

  [makeKey(B.Compound,        G.Male,   A.Under18)]: [385, 369, 337, 306, 273, 242],
  [makeKey(B.Compound,        G.Female, A.Under18)]: [357, 343, 314, 284, 255, 225],
  [makeKey(B.Recurve,         G.Male,   A.Under18)]: [311, 292, 265, 239, 213, 187],
  [makeKey(B.Recurve,         G.Female, A.Under18)]: [280, 263, 239, 215, 191, 168],
  [makeKey(B.Barebow,         G.Male,   A.Under18)]: [298, 279, 254, 229, 204, 179],
  [makeKey(B.Barebow,         G.Female, A.Under18)]: [251, 236, 214, 193, 172, 151],
  [makeKey(B.Longbow,         G.Male,   A.Under18)]: [161, 150, 137, 124, 109, 96],
  [makeKey(B.Longbow,         G.Female, A.Under18)]: [122, 114, 103, 94,  83,  73],
  [makeKey(B.Traditional,     G.Male,   A.Under18)]: [210, 196, 178, 161, 143, 126],
  [makeKey(B.Traditional,     G.Female, A.Under18)]: [158, 147, 134, 121, 107, 95],
  [makeKey(B.Flatbow,         G.Male,   A.Under18)]: [210, 196, 178, 161, 143, 126],
  [makeKey(B.Flatbow,         G.Female, A.Under18)]: [158, 147, 134, 121, 107, 95],
  [makeKey(B.CompoundLimited, G.Male,   A.Under18)]: [311, 292, 265, 239, 213, 187],
  [makeKey(B.CompoundLimited, G.Female, A.Under18)]: [280, 263, 239, 215, 191, 168],
  [makeKey(B.CompoundBarebow, G.Male,   A.Under18)]: [298, 279, 254, 229, 204, 179],
  [makeKey(B.CompoundBarebow, G.Female, A.Under18)]: [251, 236, 214, 193, 172, 151],
};

function isOldFieldBowstyle(b: Bowstyle): boolean { return FieldBowstyles.includes(b); }
function isOldFieldAge(a: Age): boolean { return OldFieldAges.includes(a); }

function getOldFieldGroupData(bowstyle: Bowstyle, gender: Gender, age: Age): number[] {
  if (!isOldFieldBowstyle(bowstyle))
    throw new Error(`${bowstyle} is not a recognised bowstyle for old field classifications`);
  if (gender !== G.Male && gender !== G.Female)
    throw new Error(`${gender} is not a recognised gender for old field classifications`);
  if (!isOldFieldAge(age))
    throw new Error(`${age} is not a recognised age group for old field classifications`);
  const scores = OLD_FIELD_SCORES[makeKey(bowstyle, gender, age)];
  if (!scores) throw new Error(`No old field data for bowstyle=${bowstyle} gender=${gender} age=${age}`);
  return scores;
}

export function coaxOldFieldGroup(bowstyle: Bowstyle, gender: Gender, age: Age): Category {
  let coaxedAge: Age = A.Adult;
  if (age === A.Under21 || age === A.Over50 || age === A.Adult) {
    coaxedAge = A.Adult;
  } else {
    coaxedAge = A.Under18;
  }
  return { bowstyle, gender, ageGroup: coaxedAge };
}

export function oldFieldClassificationScores(archeryRound: Round, bowstyle: Bowstyle, gender: Gender, age: Age): number[] {
  const allRounds = waFieldRounds();
  if (!allRounds.has(archeryRound.codename)) {
    throw new Error(`This round is not recognised for old field classification. (codename="${archeryRound.codename}")`);
  }
  return getOldFieldGroupData(bowstyle, gender, age);
}

export function calculateOldFieldClassification(
  score: number,
  archeryRound: Round,
  bowstyle: Bowstyle,
  gender: Gender,
  age: Age,
): string {
  const allRounds = waFieldRounds();
  const roundname = archeryRound.codename;
  if (!allRounds.has(roundname)) {
    throw new Error(`This round is not recognised for old field classification. (codename="${roundname}")`);
  }
  const maxScore = archeryRound.passes.reduce((s, p) => s + p.nArrows * p.target.maxScore, 0);
  if (score < 0 || score > maxScore) {
    throw new Error(
      `Invalid score of ${Math.trunc(score)} for a ${archeryRound.name}. Should be in range 0-${Math.trunc(maxScore)}.`
    );
  }
  const classScores = getOldFieldGroupData(bowstyle, gender, age);

  // Check round eligibility: sighted needs red 24, unsighted needs blue 24
  if (isSighted(bowstyle)) {
    if (!roundname.includes('wa_field_24_red_')) return 'UC';
  } else {
    if (!roundname.includes('wa_field_24_blue_')) return 'UC';
  }

  for (let i = 0; i < OldFieldClasses.length; i++) {
    if (classScores[i] > score) continue;
    return OldFieldClasses[i];
  }
  return 'UC';
}
