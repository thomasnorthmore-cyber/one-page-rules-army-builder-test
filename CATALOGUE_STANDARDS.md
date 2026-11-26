# Grimdark Future catalogue standards (New Recruit / BattleScribe)

The **Master Destroyer** unit in `Battle_Brothers.cat` is the reference implementation. Apply the following to **every new army**, and when editing Battle Brothers or Robot Legions.

## Where data belongs

1. **Unit**: Quality, Defense, innate Special Rules, base points, force category, and Tough(n) in the **unit profile**. Do not remove `Tough(n)` from the unit profile: New Recruit uses it to display the correct wounds. Avoid a redundant `Tough(X)` *rule link* on the unit.
2. **Model(s)**: Every individual model must carry its actual equipped ranged and melee weapons (plus permanent equipment) through its selected loadout. No weapons only on the parent unit if they are supposed to show on each model.
3. **Weapon choice**: Weapon/upgrade **selection names must be clean, human-readable names only**, e.g. `Heavy Ion Blade`, not `Heavy Ion Blade (A6, Shred)`; use `Fusion Pulse Gun + Dual Ion Blades` for bundled selections. Keep Range, Attacks, AP and keywords in the weapon profiles and linked rules instead, never in the selectable item's label. Put weapon profiles and their rules `infoLinks` on the *selectable entry that equips that weapon*. Choose-one replacements use one selection group (min=1, max=1, default entry set). A rule from an unselected alternative must not appear under Rules.
4. **Innate rules**: Keep Battleborn, Fearless, Hero, Self-Repair, etc. on the unit when they are native abilities. Model abilities and ability-granting upgrades retain their own rule links. Never remove innate rules just to hide unselected weapon rules.
5. **Squad-wide changes**: When the source says “replace all”, the selected option must create/equip the correct weapon profiles on **each** squad model, while its points cost is paid **once**. When “replace one/any” is allowed, implement the permitted per-model choices and their limits without forcing the rest of the squad to change.
6. **References**: Only link rule definitions that exist in the catalogue/game-system data. Parameterised weapon rules such as AP(X), Blast(X), Deadly(X) must be linked to the selected weapon entries. Rule links on the squad parent that merely collect rules from every possible weapon are prohibited. Avoid redundant rule links on both a parent loadout and its nested weapon entries.
7. **Categories**: Distinguish `Heroes` from `Epic Heroes`. Use Epic Heroes for the source's unique/named heroes; preserve any one-per-army restrictions.

## Permanent rule-link audit

For every unit, compare direct parent-level `infoLinks` with the permanent rules in its Unit profile. **Do not place rules granted only by optional equipment, weapons, mobility upgrades, transport upgrades, or spell selections on the parent unit.** Keep those rule links on the selection that grants them. Preserve source-native abilities (including parameterized rules such as `Fear(2)` or `Ravage(6)`) and avoid changing weapon profiles, Tough/wounds, or points as part of a rules-display cleanup. Use `scripts/validate_robot_rules.py` as the reference regression check.

## Required verification before committing

- XML parses, has unique IDs, and has no dangling `targetId` or `defaultSelectionEntryId`.
- All unit names, starting points, Quality, Defense, Tough/wounds, and default weapons match the supplied army PDF, including named heroes and aircraft.
- Every model has its correct default weapons; count all models in a squad, and validate at least one whole-squad upgrade and one single-model upgrade.
- Each selectable weapon with a defined special rule has a matching rule link, only while equipped. Rule links for unselected weapons do not appear on the parent unit.
- Permanent unit abilities persist when equipment changes.
- The catalogue revision increments; test the refreshed catalogue in New Recruit's editor **and Force Organisation** view before declaring the visual behaviour confirmed.

## Current catalogues

- `Battle_Brothers.cat`: Master Destroyer reference and existing Battle Brothers units.
- `Robot_Legions.cat`: model-level armaments, including Eternals, Bot Swarms, and the other v3.6.0 units.
- `Grimdark_Future.gst`: shared profiles, force categories, and point type.

If any newly imported PDF has an ambiguous or conditional option, document it rather than silently invent a loadout. These are data and structure standards; passing an XML audit alone is not proof of the exact New Recruit UI output.

## Exhaustive equipped-rule and replacement validation

- For **every** Ranged/Melee Weapon profile on a selectable entry (including individual models), normalize parameterized keywords (e.g. AP(4) → AP(X)) and ensure each keyword has a corresponding **direct** rule `infoLink` on that selected entry. Do not substitute a permanent parent-unit link.
- For every selectable, leaf-type nonweapon equipment upgrade, require a direct rule link or profile; never leave an inert selection with points but no effect. Confirm each ability from the relevant source PDF rather than inferring it from the equipment name.
- If a weapon can be replaced, **do not retain its profile or rule links on the parent loadout**. Use an exactly-one selection group with a zero-cost default that equips the original profile and alternative options carrying their own weapon profiles, rule links and incremental points.
- Keep shared baseline abilities on their valid owners. When default gear is replaced (e.g. Rapid Skimmer Module/Scout → Advanced Jet Thrusters/Fast), move default-gear rules into the default entry rather than leaving them permanently on the unit.
- Run `python3 scripts/validate_all_equipped_weapon_rules.py` and `python3 scripts/validate_equipped_rules.py` for **all three armies**. Structural passing still requires visual verification in New Recruit.


## Continuous validation (all factions)

The required cross-faction entry point is `python3 scripts/validate_all_factions.py --strict --output validation-report.json`.
It automatically discovers every root-level `.cat` containing units; do not maintain a fixed list of factions in validation scripts. GitHub Actions runs this entry point on catalogue, game-system, reference-data, or validator changes and uploads the JSON report even on failure.

The independent PDF-grounded reference is `reference/source-checks.json`. Every unit must have source-verified **Quality, Defense and base points** before CI can pass. As of 2026-11-26 this covers 122/122 currently listed units. **This is not a full source-parity certificate**: model equipment options, special-rule text, permitted upgrade limits, points for upgrades, and named-character exceptions still need additional independent source fixtures and targeted checks.

`reference/shared-rules.json` records the central core-rule interpretation and required effects. Definitions that are placeholders, missing an expected effect, or missing an associated link are errors. When a regression is found, add its stable entry ID and expected rule to `reference/regressions.json` so it cannot be silently reintroduced.

`reference/known-issues.json` must contain **only explicitly confirmed existing exceptions**. They remain errors in the report, but are temporarily exempt from strict CI failure; new errors are blocked. Remove an exception immediately after fixing it. Never automatically add new errors to this list.

Manual test before claiming a faction complete: refresh New Recruit, test each unit's default models and both ranged and melee profiles, try each weapon and gear choice (including replacement of base weapons), verify selectable rule descriptions are conditional, verify squad vs model points, then export `.rosz` and check ForceOrg wounds, rules and model assignments. A passing CI result is not evidence of a successful visual or ForceOrg test.

Legacy single-faction scripts are maintained only for historical diagnostics and may have stale fixtures. The unified check is authoritative. If a legacy script disagrees, repair its assumptions and report the difference rather than altering correct catalogue data to satisfy an outdated test.


## Faction PDF special-rules coverage (mandatory)

Every newly supplied Grimdark Future army PDF is the source of truth for its faction's **ARMY-WIDE SPECIAL RULE**, **SPECIAL RULES**, **AURA SPECIAL RULES** and **ARMY SPELLS** page. Inspect the actual supplied PDF before changing rules; do not substitute older Army Forge cached data or a different game mode.

- Add every faction-specific special/aura rule printed on the PDF page to the faction catalogue's `sharedRules`, even if no current model selects it. Preserve exact parameters and key conditions (range, wounds, timing, Fatigued, limits, dice, unit/model ownership). Link all rules used by innate unit entries and selected weapon or gear entries to existing nonempty definitions.
- Keep selectable gear rules on the option which grants them; never give a permanently visible parent rule merely because an optional choice can provide it. Maintain nonredundant ForceOrg outputs and per-model weapon ownership.
- Add/update `reference/pdf-special-rule-checks.json` when a new faction PDF or edition arrives. The `scripts/validate_pdf_special_rules.py` check must pass, as well as unified validation and spell-catalogue validation. The PDF rule manifest establishes **presence and representative effects**; it is not a guarantee of verbatim description parity. Compare complete new/changed wording manually against the original PDF before claiming exact verification.
- Core rules not defined on the faction PDF's special-rule page must be checked against the matching core rules, not inferred from an older catalogue. A missing or unclear core definition is a source-review issue, not permission to invent it.
- When introducing a PDF rule, retain the original PDF rule name in the reference and allow numbered parameters in linked instances. Add regression fixtures for previously missed rules.

## Universal core rules ownership (v3.6.0)

The 37 universal special rules from Grimdark Future Core Rules v3.6.0 page 2 live exclusively in `Grimdark_Future.gst` sharedRules. All factions link to those stable `opr-core-*` IDs, including parameterized instances; keep their displayed numeric values and existing equipment ownership. Never copy these definitions into a faction. Faction-specific rules, auras and spells remain in the relevant faction catalogue. Core descriptions preserve the supplied PDF's effects in readable paraphrase. The unified validator and PDF validator must resolve both game-system and local rules. Do not add redundant Tough links or alter ForceOrg export behavior.

## Faction rule hygiene

Use one definition per exact local rule name. Automatic spell catalogue and caster entries must reference the same spell IDs. Remove inherited foreign definitions only when not used and not present in the faction source manifest. Preserve source-defined rules even with zero direct links, and preserve referenced legacy equipment rules pending source verification. Do not merge parameterized rules with different named payloads without source review.
