import { mkdir, writeFile } from 'node:fs/promises';
import * as opr from 'opr-army-db';

const bookId = process.env.OPR_BOOK_ID || '78qp9l5alslt6yj8';
if (!/^[a-zA-Z0-9_-]{8,40}$/.test(bookId)) throw Error('Invalid book ID');
if (typeof opr.getArmyBook !== 'function') throw Error('getArmyBook is not exported');
await mkdir('import-data', { recursive: true });

const report = {
  bookId,
  expectedGameSystem: 'grimdark-future',
  expectedMajorMinor: '3.6',
  retrievedAt: new Date().toISOString(),
  attempts: [],
  status: 'not-verified',
};
const sourceText = String(opr.getArmyBook);
console.log('getArmyBook signature:', sourceText.slice(0, 1500));

const attempts = [
  { label: 'no second argument', args: [bookId] },
  { label: 'second argument 2', args: [bookId, 2] },
  { label: 'second argument 3', args: [bookId, 3] },
  { label: 'second argument 9', args: [bookId, 9] },
  { label: 'second argument 10', args: [bookId, 10] },
];
let verified = null;
for (const attempt of attempts) {
  try {
    const data = await opr.getArmyBook(...attempt.args);
    if (!data || typeof data !== 'object') throw Error('Empty or nonobject response');
    const candidate = data.armyBook ?? data.book ?? data.data ?? data;
    const units = candidate.units ?? candidate.unitList ?? candidate.armyUnits;
    const summary = {
      label: attempt.label,
      gameSystemId: candidate.gameSystemId ?? null,
      gameSystemSlug: candidate.gameSystemSlug ?? null,
      versionString: candidate.versionString ?? null,
      unitCount: Array.isArray(units) ? units.length : 0,
      upgrades: Array.isArray(candidate.upgradePackages) ? candidate.upgradePackages.length : 0,
    };
    report.attempts.push(summary);
    console.log('Probe:', JSON.stringify(summary));
    if (summary.gameSystemSlug === 'grimdark-future' &&
        String(summary.versionString).startsWith('3.6') &&
        summary.unitCount >= 10 && summary.upgrades > 0) {
      verified = data;
      report.status = 'verified-source';
      report.chosenAttempt = attempt.label;
      break;
    }
  } catch (error) {
    const summary = { label: attempt.label, error: String(error) };
    report.attempts.push(summary);
    console.log('Probe failure:', JSON.stringify(summary));
  }
}
await writeFile('import-data/validation-report.json', JSON.stringify(report, null, 2));
if (!verified) {
  console.error('No matching GF 3.6 army book found. Only the probe report will be uploaded.');
  process.exitCode = 2;
} else {
  await writeFile('import-data/battle-brothers-source.json', JSON.stringify(verified, null, 2));
  console.log('Saved verified Grimdark Future 3.6 source. Existing New Recruit files unchanged.');
}
