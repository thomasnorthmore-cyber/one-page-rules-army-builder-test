# Knight Brothers v3.6.0 — live acceptance test

Test the Draft catalogue in New Recruit and export a real .rosz roster. Import the roster through the OPR short-code service, assign the models in TTS and compare with the source. Synthetic fixtures do not validate the live exporter. The shared converter caster metadata fix must be deployed before testing that behavior.

| Unit | Configuration | Expected |
| --- | --- | --- |
| Knight Battle Brothers | Default | 140 pts, five Cyclic Rifles and five Strikes on individual models |
| Knight Battle Brothers | One Slayer Chain-Cannon, one Dual Energy Sabres specialist, Inceptors, Psychic | 205 pts (140+30+10+10+15), five models, Teleport; Caster(1) and six spell links only on Psychic model |
| Knight Battle Brothers | All Assault Cyclic Rifles and Energy Halberds | 155 pts (140+10+5), five models, each has both weapons, no Strike or Cyclic Rifle specialist option |
| Knight Veteran Brothers | Purifiers, default Dual Energy Sabres | 140 pts, three models, Ravage(1) |
| Knight Veteran Brothers | Slayer Blaze-Flamer/Strike squad, one Fusion-Beamer, one Volley-Gun, Strikers | 195 pts (130+15+15+25+10), three different ranged loadouts, Ambush, no Sabres or Ravage(1) |
| Knight Purgation Brothers | One Fusion-Beamer, one Volley-Gun, one Chain-Cannon, Psychic | 215 pts (140+15+20+25+15), three models, only one Caster(1) |
| Knight Destroyers | Burst Cyclic Rifles, one Slayer Chain-Cannon, Paladins, Orbital Drop, Psychic | 370 pts (210+40+50+20+35+15), three Tough(3) models, Ravage(2), Ambush and one Caster(1) |
| Knight Nemesis Walker | Default | 740 pts, two Heavy Walker Slayer Hammers, Stomp, Tough(18), Caster(2) |
| Knight Nemesis Walker | Assault Slayer Volley-Gun with Walker Sword, other arm Heavy Walker Fist, Teleport Engine and Power Shield | 905 pts (740+70+5+15+30+45), Tough(18), Caster(2), Ambush, Teleport, Stealth, selected arms and Stomp only |
| Knight Veteran Master Brother | Shield, Combat Bike, Inceptor, Master Archivist | 270 pts (95+5+110+5+55), Tough(6), Fast, Teleport, Armor(2), Caster(3), hand weapon and bike rifle |
| Knight Attack Vehicle | Cargo Space, Dozer Blade, Extra Armor | 255 pts (175+20+30+30), Tough(6), Transport(6), Strider, Armor(2) |
| Knight Heavy Battle Tank | Cargo Space, Dozer Blade | 875 pts (745+35+95), Tough(18), Transport(11), Strider |
| Spell reference | Open faction spell category | Six spells; zero points; no playable model |

Revert each selected upgrade and verify its equipment and conditional effects disappear. Verify independent model wound counters and caster metadata where the importer supports it. Retain real .rosz fixtures and record pass/fail for both applications.

Known limitations: Heavy Gunship Cargo Space grouping and unrestricted specialist co-location remain provisional. Do not mark Completed until those and actual runtime behavior are verified.

Status: not executed in either application; converter correction not deployed.
