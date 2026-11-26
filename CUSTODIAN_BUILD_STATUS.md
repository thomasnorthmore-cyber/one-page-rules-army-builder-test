# Custodian Brothers v3.6.0 — catalogue build status

Source: user-supplied `Custodian_Brothers_3.6.0.pdf` (10 content pages, OPR v3.6.0). This catalogue uses the same `Grimdark_Future.gst` as Battle Brothers and Robot Legions.

## Implemented
- All 22 roster entries with source starting points, Quality, Defense, Tough and default weapons.
- Explicit individual model entries, one selected weapon profile for each equipped default slot, and scoped rule links.
- Model-level individual replacements for supported weapon slots.
- Squad-wide configurations with single total upgrade prices for Vigilant Sisters, Prosecution Sisters, Hunter Sisters, Custodian Brothers, Veteran Custodian Brothers and Jetpack Custodian Brothers.
- Linked complete replacements on Master Destroyer, Destroyer and Veteran Destroyer.
- Officer, banner, transport and optional wargear selections.
- Automated `scripts/validate_custodian.py` file and GitHub Actions integration.
- Structural audit confirms 22 units, unique IDs, intact XML tag structure, resolved rule targets and valid default IDs.

## Remaining before claiming full source parity
- Fully conditional Master Custodian/Veteran Master Custodian jetbike upgrades and follow-on weapon substitutions.
- Great Sister's alternative role loadouts and conditional pistol/hand-weapon replacement trees.
- Conditional and paired weapon swaps on Custodian Combat Walker and Assault Walker, and all other special-case walker alternatives.
- Full per-model vs whole-squad upgrade verification of every PDF option, including banners and equipment interactions.
- Additional verification of all source weapon/rule descriptions against the PDF and the current rules system; some shared core rules use cross-faction definitions or generic descriptions.
- Real New Recruit editor, Force Organisation, points totals, and export testing.

**Do not label this source-complete or New Recruit UI-verified until the remaining conditions have been tested.**
