export const Gender = {
  Male: 'MALE',
  Female: 'FEMALE',
  Open: 'OPEN',
} as const;
export type Gender = typeof Gender[keyof typeof Gender];

export const AllGenders: Gender[] = [Gender.Male, Gender.Female, Gender.Open];

export const Age = {
  Over50:  'OVER_50',
  Adult:   'ADULT',
  Under21: 'UNDER_21',
  Under18: 'UNDER_18',
  Under16: 'UNDER_16',
  Under15: 'UNDER_15',
  Under14: 'UNDER_14',
  Under12: 'UNDER_12',
} as const;
export type Age = typeof Age[keyof typeof Age];

export const AllAges: Age[] = [
  Age.Over50, Age.Adult, Age.Under21, Age.Under18,
  Age.Under16, Age.Under15, Age.Under14, Age.Under12,
];

export const Bowstyle = {
  Compound:        'COMPOUND',
  Recurve:         'RECURVE',
  Barebow:         'BAREBOW',
  Longbow:         'LONGBOW',
  Traditional:     'TRADITIONAL',
  Flatbow:         'FLATBOW',
  CompoundLimited: 'COMPOUNDLIMITED',
  CompoundBarebow: 'COMPOUNDBAREBOW',
} as const;
export type Bowstyle = typeof Bowstyle[keyof typeof Bowstyle];

export const OutdoorBowstyles: Bowstyle[] = [
  Bowstyle.Compound, Bowstyle.Recurve, Bowstyle.Barebow, Bowstyle.Longbow,
];
export const IndoorBowstyles: Bowstyle[] = [
  Bowstyle.Compound, Bowstyle.Recurve, Bowstyle.Barebow, Bowstyle.Longbow,
];
export const FieldBowstyles: Bowstyle[] = [
  Bowstyle.Compound, Bowstyle.Recurve, Bowstyle.Barebow, Bowstyle.Longbow,
  Bowstyle.Traditional, Bowstyle.Flatbow, Bowstyle.CompoundLimited, Bowstyle.CompoundBarebow,
];

export interface Category {
  bowstyle: Bowstyle;
  gender: Gender;
  ageGroup: Age;
}
