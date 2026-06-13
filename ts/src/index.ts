export * from './length.js';
export * from './targets.js';
export * from './rounds.js';
export * from './handicaps.js';
export { HandicapTable } from './handicap-table.js';
export type { HandicapTableOptions } from './handicap-table.js';

export {
  Gender, Age, Bowstyle,
  AllGenders, AllAges,
  OutdoorBowstyles, IndoorBowstyles, FieldBowstyles,
  type Category,
} from './classifications/data.js';

export {
  calculateOutdoorClassification,
  outdoorClassificationScores,
  coaxOutdoorGroup,
} from './classifications/outdoor.js';

export {
  calculateIndoorClassification,
  indoorClassificationScores,
  coaxIndoorGroup,
} from './classifications/indoor.js';

export {
  calculateFieldClassification,
  fieldClassificationScores,
  coaxFieldGroup,
  FieldAges,
} from './classifications/field.js';

export {
  calculateOldIndoorClassification,
  oldIndoorClassificationScores,
  coaxOldIndoorGroup,
  OldIndoorBowstyles,
} from './classifications/old-indoor.js';

export {
  calculateOldFieldClassification,
  oldFieldClassificationScores,
  coaxOldFieldGroup,
  OldFieldClasses,
  OldFieldAges,
} from './classifications/old-field.js';
