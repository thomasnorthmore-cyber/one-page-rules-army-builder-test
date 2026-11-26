# Wolf Brothers v3.6.0 — live acceptance test

Use a separate local test copy of the wolf-brothers-build branch, not the main game data. The catalogue is Draft. These checks require the actual New Recruit UI, its .rosz export, and the deployed OPR importer in Tabletop Simulator. The automated selected-roster fixtures are synthetic and cannot substitute for this test.

## New Recruit and actual exported roster
| Case | Select | Expected |
| --- | --- | --- |
| Default Werewolves | Werewolf Brothers, no upgrades | 205 pts, three models, each one Energy Were-Claws A3 Rending, Tough(3), no shield/backpack/regeneration |
| Upgraded Werewolves | All Energy Hammers + Combat Shields, all Backpack-GL, Cyborg Body | 280 pts (205+5+40+30), three models, hammer and backpack on each, Armor(3), Regeneration; no claws |
| Battle Brothers | One Fusion Rifle, one separate sergeant with Arc-Charger Pistol and Energy Sword | 175 pts (140+25+5+5), five models, only one fusion rifle and one sergeant, three unmodified rifle models |
| Walker default | Wolf Combat Walker | 400 pts, Tough(12), one Stomp and two fists |
| Walker shield | Replace both fists with axe and shield | 400 pts, Tough(12), Stomp, axe, Fortified, no fists |
| Walker mixed arms | One Fusion Rifle replacing Heavy Flamer on Light Walker Fist arm, other arm unchanged | 435 pts (400+15+20), Tough(12), Stomp, Light Walker Fist, Fusion Rifle and one Walker Combat Fist; no Heavy Flamer |
| Veteran Assault Brothers | Flamer Pistols + Hand Weapons; Airdrop Jetpack | 165 pts (115+30+20), three models, Flying/Ambush, no Armor(2) |
| Veteran Battle Brothers | Burst Battle Rifle on one model plus Fusion-Mod; other two unchanged | 145 pts (120+10+15), three models, attachment only on rifle-equipped model |
| Pathfinder Bikers | Off-Road Tires, no weapon changes | 205 pts (185+20), Scout and Strider, no Fast |
| Spells | Open faction spell reference | Six spells, zero points, no playable model |

For each case confirm selected-only rules and exact model allocation in both New Recruit and the exported roster. Revert choices and confirm removed equipment and conditional rules disappear. Do not test clipped Battle Tank upgrades as verified source data. Pathfinder Biker sergeant wording remains provisional.

## ForceOrg
Export the test roster as .rosz; upload to the existing OPR code service; enter the resulting code in the importer and assign models to miniatures. Check each model's ranged and melee descriptions, selected-only rules, quantities and starting wounds (Werewolves 3, Walker 12, ordinary Battle Brothers 1 in TTS). Change one model's wounds and verify the others are unaffected. Record pass/fail and retain the actual exported .rosz as evidence.

Status: not executed in either application. Do not mark Completed based on automated CI alone.
