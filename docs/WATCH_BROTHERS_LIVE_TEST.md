# Watch Brothers v3.6.0 — live acceptance test

Test the Draft catalogue in New Recruit, export a real .rosz and import through the OPR short-code service into TTS. The shared converter corrections must be deployed before live verification. Synthetic tests do not certify either application.

| Unit | Configuration | Expected |
| --- | --- | --- |
| Watch Battle Brothers | Default | 110 pts, three models each with Flamer and Strike |
| Watch Battle Brothers | Burst Heavy Rifle + Fusion-Mod; Heavy Machinegun + Flamer-Mod; Plasma Pistol + Energy Sword; squad Combat Shield | 215 pts (110+20+15+30+5+5+10+10+10), three distinct loadouts, Armor(2) on all; attachments only on their owning model |
| Watch Vanguard | One Dual Energy Claws, one Great Energy Hammer, one Fusion Pistol + Energy Fist; Combat Shields and Aerial Drop | 210 pts (135+15+15+10+15+10+10), three models, Flying, Armor(2), Ambush |
| Watch Destroyers | All Hand Weapons and Combat Shields | 225 pts, three Tough(3) models, Armor(2), no ranged weapons |
| Watch Destroyers | Burst Cyclic Rifles, one Missile Rack, one Energy Sword, Orbital Drop | 350 pts (225+30+50+10+35), three Tough(3) models, one Missile Rack and Ambush, no Armor(2) |
| Watch Brother Bikers | Assault Heavy Bike-Rifles, one Fusion Rifle, sergeant upgrade with Plasma Pistol and Energy Sword | 335 pts (275+20+25+5+5+5), three Tough(3) models, Fast, each retains own bike weapon |
| Watch Master Brother | Master Archivist, Combat Shield, Combat Bike | 255 pts (75+70+15+95), Tough(6), Fast, Armor(2), Caster(3), six spells |
| Watch Master Brother | Death-Munitions Keeper, otherwise default | 120 pts (75+45), Enhanced Watchborn Aura, no permanent AP increase, no caster |
| Watch Drop Pod | Targeting Array | 150 pts (130+20), Unstoppable Mark as ability, Transport(11) |
| Watch Attack Vehicle | Cargo Space, Dozer Blade, Extra Armor, Targeting Array | 270 pts (170+20+30+30+20), Transport(6), Strider, Armor(2), Unstoppable Mark, Tough(6) |
| Watch Combat Walker | First arm Heavy Flamer + Light Walker Fist, replace flamer with Fusion Rifle; second arm Twin Laser Cannon | 530 pts (395+20+25+90), independent arms and Stomp, Tough(12) |
| Watch Deathstar Gunship | Cluster Bombs replace linked heavy rifle arrays | 435 pts (400+35), original other guns retained, A3 AP(1) Crossing Strike Surge, no ordinary melee grouping in converter |
| Watch Deathstar Gunship | Cargo Space replaces linked heavy rifle arrays | 445 pts (400+45), Transport(11), no Cluster Bombs or replaced rifle arrays |
| Spell reference | Open faction spell category | Six spells, no playable model |

Remove each upgrade and confirm that its effects disappear. Verify actual roster metadata, model wound counters and model-specific gear. Keep the source wording of Enhanced Watchborn and Enhanced Versatile Warrior unchanged pending clarification.

Provisional interpretations: duplicate Drop Pod Targeting Array represented once; Deathstar Gunship cargo occupies the printed replacement group; designated specialist slots limit unrestricted co-location. New Recruit's no-range Cluster Bombs profile remains unchanged, even though the converter now handles Crossing Strike independently.

Status: not executed in either live application. Converter correction not deployed.
