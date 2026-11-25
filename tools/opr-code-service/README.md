# OPR ForceOrg 10-minute army codes

Independent New Recruit roster importer using Cloudflare Workers + KV. Each \`.rosz\` upload returns a new \`OPR-XXXXXXXXX\` code, and the converted roster is retained in KV with \`expirationTtl:600\`. Server checks expiry again on each read. Codes are not permanent.

## One-time setup
Install Node.js and create a Cloudflare account. Run \`npm install\`, \`npx wrangler login\`, \`npx wrangler kv namespace create ARMIES\`. Replace the KV namespace ID in \`wrangler.toml\`; run \`npm run deploy\`. Wrangler provides the website HTTPS URL. Enter that base URL just once into the OPR Importer object in the accompanying development TTS save.

## Normal workflow
Export \`.rosz\` from New Recruit → open your Worker website → upload roster → copy \`OPR-XXXXXXXXX\` → enter code in the OPR importer object → assign profiles to selected miniatures → save your TTS game. Re-upload for a new code if ten minutes pass.

API: POST /api/upload accepts binary \`.rosz\` up to 1 MB and returns code/expiry; GET /api/army?code=OPR-XXXXXXXXX returns the {listId,listJson} model data.

Note: Worker source has not yet been deployed or tested inside TTS. Cloudflare KV is eventually consistent. The independent importer attaches model names and descriptions; it does not reproduce original ForceOrg automation. Model loadouts reflect the roster's exported choices; re-export after fixing invalid equipment. Do not redistribute ForceOrg save assets without ensuring redistribution rights.
