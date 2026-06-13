const ALIAS_TO_DEF: Record<string, string> = {
  Yard: 'yard', yard: 'yard', Yards: 'yard', yards: 'yard',
  Y: 'yard', y: 'yard', Yd: 'yard', yd: 'yard', Yds: 'yard', yds: 'yard',
  Metre: 'metre', metre: 'metre', Metres: 'metre', metres: 'metre',
  M: 'metre', m: 'metre', Ms: 'metre', ms: 'metre',
  Centimetre: 'cm', centimetre: 'cm', Centimetres: 'cm', centimetres: 'cm',
  CM: 'cm', cm: 'cm', CMs: 'cm', cms: 'cm',
  Inch: 'inch', inch: 'inch', Inches: 'inch', inches: 'inch',
};

const TO_METRES: Record<string, number> = {
  metre: 1.0,
  yard: 0.9144,
  cm: 0.01,
  inch: 0.0254,
};

export function toMetres(value: number, unit: string): number {
  const def = ALIAS_TO_DEF[unit];
  if (!def) throw new Error(`unit "${unit}" not recognised`);
  return TO_METRES[def] * value;
}

export function fromMetres(value: number, unit: string): number {
  const def = ALIAS_TO_DEF[unit];
  if (!def) throw new Error(`unit "${unit}" not recognised`);
  return value / TO_METRES[def];
}

export function definitiveUnit(alias: string): string {
  const def = ALIAS_TO_DEF[alias];
  if (!def) throw new Error(`unit "${alias}" not recognised`);
  return def;
}

export const SUPPORTED_DIAM_UNITS = new Set(['cm', 'inch', 'metre', ...Object.keys(ALIAS_TO_DEF).filter(k => {
  const d = ALIAS_TO_DEF[k];
  return d === 'cm' || d === 'inch' || d === 'metre';
})]);

export const SUPPORTED_DIST_UNITS = new Set([...Object.keys(ALIAS_TO_DEF).filter(k => {
  const d = ALIAS_TO_DEF[k];
  return d === 'yard' || d === 'metre';
})]);
