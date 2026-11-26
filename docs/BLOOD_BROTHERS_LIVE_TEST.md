# Blood Brothers v3.6.0 — live acceptance test

Test the Draft catalogue in a separate New Recruit data copy before relying on it in play. Export the selected roster as .rosz and upload to the existing OPR short-code importer, then check the assigned models in Tabletop Simulator. Automated tests use synthetic XML, not a live New Recruit export.

| Unit | Configuration | Expected result |
| --- | --- | --- |
| Blood Death Brothers | Default rifles and strikes | 155 points, five models, Regeneration, no Flying or Ambush |
| Blood Death Brothers | Squad pistols + hand weapons, one plasma pistol, Airdrop Jetpack | 220 points (155+20+10+35), five models, exactly one plasma pistol, Regeneration, Flying, Ambush; no rifles or strikes |
| Blood Guard Brothers | One Burst Fusion Pistol, one separate Plasma Pistol, one Energy Sword, Aerial Drop | 265 points (185+45+10+5+20), five models, selected weapons only, Flying and Ambush |
| Blood Veteran Assault Brothers | Default shields, Jetpack | 125 points (115+10), three models, Armor(2), Flying |
| Blood Veteran Assault Brothers | Dual Energy Claws, Airdrop Jetpack | 220 points (115+85+20), three models, Flying and Ambush, no Armor(2) or hand weapons |
| Blood Veteran Battle Brothers | One Burst Battle Rifle with Flamer-Mod and Fusion-Mod, one Plasma Rifle, one default Flamer | 185 points (125+15+10+15+20), three models; both attachments belong only to rifle model |
| Blood Combat Walker | Default | 395 points, Tough(12), Stomp and two Walker Combat Fists |
| Blood Combat Walker | One Walker Claw, other arm Heavy Flamer + Light Walker Fist with Fusion Rifle replacement, Death Pilot | 510 points (395+20+15+30+50), Tough(12), Regeneration, Stomp, Claw, Fusion Rifle, Light Walker Fist; no default fists or Heavy Flamer |
| Blood Combat Walker | Default weapons, Archivist | 440 points, Caster(2), no Regeneration, Tough(12) |
| Blood Attack Vehicle | Cargo Space, Dozer Blade, Extra Armor | 245 points (165+20+30+30), Transport(6), Strider, Armor(2), Tough(6) |
| Blood Heavy Battle Tank | Cargo Space and Dozer Blade | 850 points (720+35+95), Transport(11), Strider, Tough(18) |
| Blood Veteran Master Brother | Combat Shield, Archivist, Airdrop Jetpack | 155 points (90+0+45+20), Armor(2), Caster(2), Ambush, Flying |
| Spell reference | Open faction spell category | Six spells, no playable model and no points |

For each check, revert the choices and confirm the corresponding effects disappear. Compare the actual .rosz profiles and model counts with both application displays. Check assigned model wound counters independently, including Walker 12 and Attack Vehicle 6. Capture any discrepancies and retain the exported roster for debugging.

Known limitations: Pathfinder Biker sergeant wording, Heavy Gunship Cargo Space grouping and unrestricted co-location of specialist upgrades have not been fully resolved. Do not mark Completed until source interpretations and runtime behavior are verified.

Status: not executed in either application.
