# One Page Rules — Grimdark Future (New Recruit test)
This is a **separate, unofficial community test project** for loading OPR Grimdark Future army catalogues in New Recruit, and investigating roster export interoperability with YellowScribe / Tabletop Simulator.

## Current stage (v0.1)
- `Grimdark_Future.gst`: baseline game system with points, Unit, Ranged Weapon and Melee Weapon profiles.
- `Integration_Test.cat`: **synthetic test data, not an official OPR army book**. The model values, weapon names and 100-point cost are invented for integration testing and MUST NOT be used as rules.
- No official faction rosters have been imported yet.
- YellowScribe / TTS compatibility is **not verified**.

## Try in New Recruit
Use **Systems → Add system → Import from GitHub** and enter this repository URL:
https://github.com/thomasnorthmore-cyber/one-page-rules-army-builder-test

This repository is currently private; GitHub import may require public access or an alternative authenticated/file import route. No need to change its visibility until we're ready for a controlled test.

## Next work
1. Validate that New Recruit loads both catalogues and creates a roster.
2. Replace synthetic faction data with version-verified OPR 3.6 faction data from a source we are permitted to use.
3. Add upgrade selection groups, unit-size constraints, force-organisation checks, and model-level equipment profiles.
4. Export a .rosz and inspect units, models, profiles, selected weapons, and rules.
5. Test YellowScribe in TTS. If unsupported, build a separate export adapter and document the supported workflow.

## Important
This is not affiliated with or endorsed by One Page Rules, New Recruit, or YellowScribe. OPR retains rights to its published content.
