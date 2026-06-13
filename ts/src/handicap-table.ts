import { type Scheme, scoreForRound } from './handicaps.js';
import { type Round } from './rounds.js';

const FILL = -9999;

export interface HandicapTableOptions {
  roundedScores?: boolean;
  intPrec?: boolean;
  cleanGaps?: boolean;
  arwD?: number;
}

export class HandicapTable {
  readonly scheme: Scheme;
  readonly handicaps: number[];
  readonly roundList: Round[];
  readonly roundedScores: boolean;
  readonly intPrec: boolean;
  readonly cleanGaps: boolean;

  private readonly tableF: number[][];
  private readonly tableI: number[][];

  constructor(
    s: Scheme,
    handicaps: number[],
    roundList: Round[],
    opts: HandicapTableOptions = {},
  ) {
    if (roundList.length === 0) throw new Error('no rounds provided for handicap table');
    if (handicaps.length === 0) throw new Error('no handicaps provided for handicap table');

    const {
      roundedScores = false,
      intPrec: rawIntPrec = false,
      cleanGaps = false,
      arwD = 0,
    } = opts;

    const intPrec = rawIntPrec || roundedScores;

    let hcs = [...handicaps];
    if (cleanGaps && hcs.length > 1) {
      const delta0 = hcs[1] - hcs[0];
      const deltaE = hcs[hcs.length - 1] - hcs[hcs.length - 2];
      hcs = [hcs[0] - delta0, ...hcs, hcs[hcs.length - 1] + deltaE];
    }

    const nrows = hcs.length;
    const ncols = roundList.length + 1;
    const tableF: number[][] = Array.from({ length: nrows }, (_, ri) => {
      const row = new Array<number>(ncols).fill(0);
      row[0] = hcs[ri];
      for (let ci = 0; ci < roundList.length; ci++) {
        row[ci + 1] = scoreForRound(s, hcs[ri], roundList[ci], arwD, roundedScores);
      }
      return row;
    });

    const tableI: number[][] = intPrec
      ? tableF.map(row => row.map((v, ci) => ci === 0 ? Math.round(v) : Math.trunc(v)))
      : [];

    if (cleanGaps) {
      this._cleanRepeated(tableF, tableI, s.descending(), intPrec);
      if (hcs.length > 2) {
        hcs = hcs.slice(1, hcs.length - 1);
        tableF.splice(0, 1);
        tableF.splice(tableF.length - 1, 1);
        if (intPrec) {
          tableI.splice(0, 1);
          tableI.splice(tableI.length - 1, 1);
        }
      }
    }

    this.scheme = s;
    this.handicaps = hcs;
    this.roundList = roundList;
    this.roundedScores = roundedScores;
    this.intPrec = intPrec;
    this.cleanGaps = cleanGaps;
    this.tableF = tableF;
    this.tableI = tableI;
  }

  private _cleanRepeated(tableF: number[][], tableI: number[][], descending: boolean, intPrec: boolean): void {
    const n = tableF.length;
    const ncols = this.roundList.length + 1;
    if (!descending) { tableF.reverse(); if (intPrec) tableI.reverse(); }
    for (let r = 0; r < n - 1; r++) {
      for (let c = 1; c < ncols; c++) {
        if (tableF[r][c] === tableF[r + 1][c]) {
          if (intPrec) tableI[r][c] = FILL;
          tableF[r][c] = NaN;
        }
      }
    }
    if (!descending) { tableF.reverse(); if (intPrec) tableI.reverse(); }
  }

  format(): string {
    const colW = 14;
    const rjust = (s: string) => s.padStart(colW);

    const abbreviate = (name: string) => {
      const abbrevs: Record<string, string> = {
        Compound: 'C', Recurve: 'R', Triple: 'Tr', Centre: 'C',
        Portsmouth: 'Ports', Worcester: 'Worc', Short: 'St',
        Long: 'Lg', Small: 'Sm', Gents: 'G', Ladies: 'L',
      };
      return name.split(' ').map(w => abbrevs[w] ?? w).join(' ');
    };

    const lines: string[] = [];
    lines.push(rjust('Handicap') + this.roundList.map(r => rjust(abbreviate(r.name))).join(''));

    let hcDP = 0;
    for (const h of this.handicaps) {
      const s = String(h);
      const dot = s.indexOf('.');
      if (dot >= 0 && s.length - dot - 1 > hcDP) hcDP = s.length - dot - 1;
    }

    for (let ri = 0; ri < this.handicaps.length; ri++) {
      const h = this.handicaps[ri];
      let row = hcDP === 0 ? String(Math.round(h)).padStart(colW) : h.toFixed(hcDP).padStart(colW);
      for (let ci = 0; ci < this.roundList.length; ci++) {
        if (this.intPrec) {
          const v = this.tableI[ri][ci + 1];
          row += (v === FILL ? '' : String(v)).padStart(colW);
        } else {
          const v = this.tableF[ri][ci + 1];
          row += (isNaN(v) ? '' : v.toFixed(8)).padStart(colW);
        }
      }
      lines.push(row);
    }
    return lines.join('\n');
  }

  print(): void {
    console.log(this.format());
  }

  toCSV(): string {
    const header = ['handicap', ...this.roundList.map(r => r.name)].join(',');
    const rows = this.handicaps.map((h, ri) => {
      const cells: string[] = [String(h)];
      for (let ci = 0; ci < this.roundList.length; ci++) {
        if (this.intPrec) {
          const v = this.tableI[ri][ci + 1];
          cells.push(v === FILL ? '' : String(v));
        } else {
          const v = this.tableF[ri][ci + 1];
          cells.push(isNaN(v) ? '' : v.toFixed(8));
        }
      }
      return cells.join(',');
    });
    return [header, ...rows].join('\n');
  }
}
