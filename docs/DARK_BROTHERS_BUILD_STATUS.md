# Dark Brothers v3.6.0 build status

Development branch; not complete or approved for main.

- 29 unit entries. Base Quality, Defense, points and default model counts checked against PDF pp. 2–3 and detailed unit headers.
- Initial selectable upgrade implementations across all 29 units, with squad-level alternate loadouts, per-model weapon choices, selected-only rule links, six spells, and hero Bane conditional weapon modifiers.
- PDF rule and spell reference manifests supplied. All local rule descriptions are paraphrases; complete wording review remains pending.
- Offline draft audit: 6489 unique IDs, 57 default models, 95 conditional weapon profiles, 0 errors in the checks described below. Audit checks XML nesting, target references, required group defaults, base stats and points, default model counts, default roster costs, weapon trait links, spell-reference cost/links, and Bane modifier values/scope.
- GitHub Actions full regression results still need review. Manual New Recruit and ForceOrg export tests not performed.

## Remaining source/behavior audit

- Verify every upgrade row and every valid combination independently, including all/any/one limits, specialised model and sergeant interactions, weapon-dependent replacements, and Free choices. Current single-model options use designated model slots; confirm whether banner/specialist equipment must be allowed on the same model as other upgrades and implement additional allocation if needed.
- Verify squad-wide mobility and tire rules, the conditional Tough(6) for mounted heroes, shield ownership and display, and combined weapon modifiers in actual New Recruit rosters. Unit profile may not reflect optional gear in the same way as selected rule links.
- Validate equipment and source-rule wording against PDF and core rule definitions; check alternate default profiles and aircraft Crossing Strike output.
- Do not mark Completed or merge to main before outstanding checks are resolved.

## Revision 5

- Revision 4 CI confirmed zero strict errors across 12 factions and all general tests; one legacy Alien Hives name assertion failed. The revision 5 test now checks the actual catalogue identity independently of the Completed suffix; structural checks are unchanged.
- Added source default weapon/rule/model fixture and CI test. Added selection-dependent unit profile rule modifiers for squad mobility, shields, tires, and hero mobility; these are not a substitute for real New Recruit/ForceOrg visual testing.
- Optional equipment combinations and any remaining source discrepancies must still be independently audited before merging.
