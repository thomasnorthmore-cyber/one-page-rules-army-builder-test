import { mkdir, writeFile } from 'node:fs/promises';
import * as opr from 'opr-army-db';

const bookId = process.env.OPR_BOOK_ID || '78qp9l5alslt6yj8';
const revision = Number(process.env.OPR_BOOK_REVISION || 2);
const outDir = 'import-data';
if (!/^[a-zA-Z0-9_-]{8,40}$/.test(bookId)) throw new Error('Invalid book ID');
if (!Number.isInteger(revision) || revision < 1 || revision > 100) throw new Error('Invalid revision');

console.log('Available package exports:', Object.keys(opr).join(', '));
if (typeof opr.getArmyBook !== 'function') throw new Error('getArmyBook is not exported');

const fn = opr.getArmyBook;
console.log('getArmyBook declared argument count:', fn.length);
console.log('getArmyBook function signature/source (first 700 chars):', String(fn).slice(0, 700));
let response;
try {
  response = await fn(bookId, revision);
} catch (err) {
  console.error('getArmyBook call failed:', String(err));
  if (err?.stack) console.error(err.stack);
  throw err;
}
if (!response || typeof response !== 'object') {
  console.error('Response type:', typeof response);
  throw new Error('Unexpected empty or non-object result from getArmyBook');
}
const candidate = response.armyBook ?? response.book ?? response.data ?? response;
console.log('Top-level response keys:', Object.keys(response).slice(0, 40));
console.log('Candidate keys:', Object.keys(candidate).slice(0, 40));
const units = candidate.units ?? candidate.unitList ?? candidate.armyUnits ?? response.units;
const count = Array.isArray(units) ? units.length : 0;
console.log('Units located:', count);
if (count < 10) throw new Error('Army-book schema unrecognised or incomplete; no file written');
await mkdir(outDir, { recursive: true });
await writeFile(`${outDir}/battle-brothers-source.json`, JSON.stringify(response, null, 2));
await writeFile(`${outDir}/validation-report.json`, JSON.stringify({
  bookId, revision, retrievedAt: new Date().toISOString(),
  units: count, unitNames: units.map(u => u?.name ?? u?.unitName ?? '(unknown)'),
  status: 'raw-source-only', note: 'Manual review required before generating New Recruit catalogues.'
}, null, 2));
console.log('Saved unmodified source and validation summary; live catalogues untouched.');
