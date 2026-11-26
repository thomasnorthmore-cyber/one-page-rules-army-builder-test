# Alien Hives v3.6.0 — testing status

Source: user-supplied **Alien_Hives_3.6.0.pdf** (army profiles, upgrades, and unique heroes).

**New Recruit catalogue:** `Alien_Hives.cat` → `Alien Hives (Testing v3.6.0)`.

## Implemented
- All 41 unit/hero entries, including 6 Unique Heroes in the Epic Heroes category.
- Baseline Quality, Defense, source points, native Special Rules and Tough/wounds.
- 89 individual model entries, each with its starting equipment.
- Four/dual Claws on Hive Lord / Prime Warrior remain separate weapon profiles.
- 41 source-priced conditional ability upgrades (20 selection groups).
- 57 source-priced alternate loadouts in 18 baseline-vs-replacement groups.
- Selected-weapon rule links, no permanent unit-level links for optional abilities.
- One-per-army maximum for each named Unique Hero.
- Compatible with the **same** YellowScribe post-export converter used for other armies.

## Not yet complete
- The source PDF contains 297 priced upgrade options; 98 priced selections are currently represented. Remaining squad-wide and dependent weapon-replacement options must be mapped to their prerequisites and individual models.
- Need comparison of every weapon profile and conditional wargear rule against the PDF.
- Need New Recruit visual tests (especially Force Organisation and individual models), and live YellowScribe/TTS testing.

This catalogue intentionally does **not** have the `(Completed)` label.
Do not infer that passing structural checks establishes full PDF parity.

## Regression checks
```sh
python scripts/validate_alien_hives.py
```

Existing catalogues are tagged `(Completed)` in their display names while preserving the original catalogue IDs and faction data.
