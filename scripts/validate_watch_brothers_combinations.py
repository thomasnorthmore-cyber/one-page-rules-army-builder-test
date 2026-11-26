#!/usr/bin/env python3
"""Enumerate reachable Watch Brothers unit-rule states from source PDF pp.4–8.
Static model of selection trees, not the New Recruit runtime."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Watch_Brothers.cat").getroot()
defaults = json.loads((ROOT / "reference/watch-brothers-defaults.json").read_text())["units"]
units = {u.get("name"): u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type") == "unit"}
def entries(n): return n.findall(f"./{N}selectionEntries/{N}selectionEntry")
def groups(n): return n.findall(f"./{N}selectionEntryGroups/{N}selectionEntryGroup")
def optional(n):
    return any(c.get("type") == "min" and float(c.get("value")) == 0 for c in n.findall(f"./{N}constraints/{N}constraint"))
def combine(a,b): return {x|y for x in a for y in b}
def variants(n, ids):
    if n.tag == N+"selectionEntryGroup":
        out = {frozenset()} if optional(n) else set()
        for e in entries(n): out |= variants(e, ids)
        return out
    out = {frozenset({n.get("id")} & ids)}
    for e in entries(n):
        v = variants(e, ids)
        if optional(e): v.add(frozenset())
        out = combine(out, v)
    for g in groups(n): out = combine(out, variants(g, ids))
    return out

def tokens(s): return {x.strip() for x in s.split(",") if x.strip()}
def expected(name, selected):
    r = set(defaults[name]["rules"])
    for item in selected:
        if item in ("Orbital Drop", "Aerial Drop"): r.add("Ambush")
        elif item in ("Jetpack", "Airdrop Jetpack"):
            r.add("Flying")
            if item == "Airdrop Jetpack": r.add("Ambush")
        elif item.startswith(("Combat Bike","Assault Bike")):
            r.discard("Tough(3)")
            r.update(("Fast","Tough(6)"))
        elif item in ("Hand Weapons + Combat Shields","Hand Weapon + Combat Shield","Combat Shield","Combat Shields","Extra Armor"): r.add("Armor(2)")
        elif item == "Archivist": r.add("Caster(2)")
        elif item == "Master Archivist": r.add("Caster(3)")
        elif item == "Death-Munitions Keeper": r.add("Enhanced Watchborn Aura")
        elif item == "Targeting Array": r.add("Unstoppable Mark")
        elif item == "Dozer Blade": r.add("Strider")
        elif item == "Cargo Space": r.add("Transport(6)" if name == "Watch Attack Vehicle" else "Transport(11)")
        else: raise AssertionError((name,item,"unknown source transition"))
    return r

cases = modifier_count = affected = 0
for name,u in units.items():
    p = u.find(f"./{N}profiles/{N}profile")
    mods = [m for m in p.findall(f"./{N}modifiers/{N}modifier") if m.get("field") == "b174-c09d-3660-f013"]
    if not mods: continue
    affected += 1
    modifier_count += len(mods)
    conds = [m.findall(f"./{N}conditions/{N}condition") for m in mods]
    assert all(conds), name
    by_id = {e.get("id"):e.get("name") for e in u.iter(N+"selectionEntry")}
    ids = {c.get("childId") for cs in conds for c in cs}
    assert ids <= by_id.keys(), name
    for cs in conds:
        for c in cs:
            assert c.get("type") in ("greaterThan","equalTo") and float(c.get("value")) == 0, (name,c.attrib)
            assert c.get("scope") == u.get("id") and c.get("includeChildSelections") == "true", (name,c.attrib)
    base = next(c.text or "" for c in p.findall(f"./{N}characteristics/{N}characteristic") if c.get("name") == "Special Rules")
    hit = set()
    for state in variants(u,ids):
        matches = [i for i,cs in enumerate(conds) if all((c.get("childId") in state) == (c.get("type") == "greaterThan") for c in cs)]
        assert len(matches) <= 1, (name,state,"overlap")
        hit.update(matches)
        got = tokens(mods[matches[0]].get("value") if matches else base)
        want = expected(name,{by_id[i] for i in state})
        assert got == want, (name,state,got,want)
        cases += 1
    assert hit == set(range(len(mods))), (name,"unreachable modifier")


assert affected == 10, affected

assert cases == 98 and modifier_count == 88
for name,capacity in [("Watch Attack Vehicle",6),("Watch Heavy Battle Tank",11),("Watch Deathstar Gunship",11)]:
    matches=[e for e in units[name].iter(N+"selectionEntry") if e.get("name")=="Cargo Space"]
    assert len(matches)==1, name
    assert any(l.get("name")==f"Transport({capacity})" and l.get("type")=="rule" for l in matches[0].findall(f"./{N}infoLinks/{N}infoLink")), name
spells={"Watch Dome (1)","Psychic Terror (1)","Watch Sight (2)","Lightning Fog (2)","Blessed Ammo (3)","Watch Trauma (3)"}
for name in ("Watch Master Destroyer","Watch Master Brother"):
    for role,rule in [("Archivist","Caster(2)"),("Master Archivist","Caster(3)"),("Death-Munitions Keeper","Enhanced Watchborn Aura")]:
        matches=[e for e in units[name].iter(N+"selectionEntry") if e.get("name")==role]
        assert len(matches)==1, (name,role)
        linked={l.get("name") for l in matches[0].findall(f"./{N}infoLinks/{N}infoLink")}
        assert linked==({rule}|spells if role!="Death-Munitions Keeper" else {rule}), (name,role,linked)
# Conditional source effects must remain abilities; they must not be
# unconditional weapon-rule modifiers triggered by their equipment.
for name,u in units.items():
    conditional_ids={e.get("id") for e in u.iter(N+"selectionEntry") if e.get("name") in ("Death-Munitions Keeper","Targeting Array")}
    for p in u.iter(N+"profile"):
        if p.get("typeName") in ("Melee Weapon","Ranged Weapon"):
            for m in p.iter(N+"modifier"):
                assert not any(c.get("childId") in conditional_ids for c in m.iter(N+"condition")), (name,p.get("name"))
print(f"PASS Watch Brothers: {cases} reachable rule states, {modifier_count} modifiers, {affected} units, exact caster/spell links and transport capacities; conditional source abilities preserved.")
