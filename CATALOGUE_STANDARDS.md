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
