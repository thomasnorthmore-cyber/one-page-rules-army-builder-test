import { mkdir, writeFile } from 'node:fs/promises';
import { OprApiClient } from 'opr-army-db';

const bookId = process.env.OPR_BOOK_ID || '78qp9l5alslt6yj8';
const game = 'grimdark-future';
const revision = Number(process.env.OPR_BOOK_REVISION || 2);
const outDir = 'import-data';

if (!/^[a-zA-Z0-9_-]{8,40}$/.test(bookId)) throw new Error('Unsafe army book ID');
if (!Number.isInteger(revision) || revision < 1 || revision > 100) throw new Error('Invalid revision');
const client = new OprApiClient();
console.log(`Requesting Army Forge book ${bookId}, revision ${revision}, game ${game}`);
const result = await client.getArmyBookDetails(bookId, revision, game);
if (!result || typeof result !== 'object') throw new Error('Invalid API result: missing book data');

const candidate = result.armyBook ?? result.book ?? result.data ?? result;
const units = candidate.units ?? candidate.unitList ?? candidate.armyUnits ?? result.units;
const unitCount = Array.isArray(units) ? units.length : 0;
const body = JSON.stringify(result, null, 2);
if (body.length < 1000 || unitCount < 10) {
  console.error('Received payload keys:', Object.keys(result));
  console.error('Candidate keys:', Object.keys(candidate));
  throw new Error(`Rejected incomplete or unrecognised army-book response (${unitCount} recognised units). No catalogue modified.`);
}
const names = units.map(x => x?.name ?? x?.unitName ?? '(unidentified)');
await mkdir(outDir, { recursive: true });
await writeFile(`${outDir}/battle-brothers-source.json`, body, 'utf8');
await writeFile(`${outDir}/validation-report.json`, JSON.stringify({
  bookId, revision, game, retrievedAt: new Date().toISOString(),
  unitCount, names, source: 'Army Forge through opr-army-db',
  status: 'raw-source-only',
  nextStep: 'Review equipment/upgrade schema and verify edition before generating .cat'
}, null, 2), 'utf8');
console.log(`Retrieved ${unitCount} units. Saved raw source for review; live catalogues unchanged.`);
