#!/usr/bin/env python3
"""Enumerate reachable unit-rule states; check source-based squad replacement gates.
Static model of selection trees, not the New Recruit runtime."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Wolf_Brothers.cat").getroot()
defaults = json.loads((ROOT / "reference/wolf-brothers-defaults.json").read_text())["units"]
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
        if item == "Orbital Drop": r.add("Ambush")
        elif item in ("Jetpack", "Airdrop Jetpack", "Jetpacks"):
            r.add("Flying")
            if item != "Jetpack": r.add("Ambush")
        elif item in ("Camo Cloak", "Camo Cloaks"): r.add("Stealth")
        elif item in ("Forward Sentry", "Forward Sentries"): r.add("Scout")
        elif item == "Camo Sentry": r.update(("Scout","Stealth"))
        elif item == "Cyborg Body": r.add("Regeneration")
        elif item.startswith(("Combat Bike", "Assault Bike", "Wolf Mount", "Off-Road Bike")):
            r.discard("Tough(3)")
            r.add("Tough(6)")
            r.add("Scout" if item.startswith("Off-Road Bike") else "Fast")
            if item.startswith("Wolf Mount"): r.add("Strider")
        elif item.endswith("Off-Road Tires"):
            r.discard("Fast"); r.update(("Scout","Strider"))
        elif item.endswith("High-Speed Tires"): pass
        elif item.startswith("Energy Hammers + Combat Shields"): r.add("Armor(3)")
        elif item == "Hand Weapons + Combat Shields": r.add("Armor(2)")
        elif item == "Walker Axe + Combat Shield": r.add("Fortified")
        else: raise AssertionError((name,item,"unknown source transition"))
    if name == "Wolf Veteran Assault Brothers" and "Hand Weapons + Combat Shields" not in selected: r.discard("Armor(2)")
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

# PDF pages 7–10: replacement slots may appear only where their original
# weapons exist. The Pathfinder Bikers sergeant row says Hand Weapon rather
# than Strike: interpretation retained provisionally, not certified here.
def group(n,name): return next(g for g in groups(n) if g.get("name") == name)
def branches(name): return entries(group(units[name],"Squad loadout"))
def model_groups(branch,name):
    return [g for model in entries(branch) if model.get("type") == "model" for g in groups(model) if g.get("name") == name]
for name,eligible,slots in [
    ("Wolf Pathfinders",lambda s:s=="Heavy Rifles",["Replace Heavy Rifle","Sergeant weapon loadout"]),
    ("Wolf Rookies",lambda s:s=="Heavy Pistols",["Special weapon loadout","Sergeant weapon loadout"]),
    ("Wolf Brother Bikers",lambda s:s.endswith("Heavy Rifles + Strikes"),["Replace Heavy Rifle","Sergeant weapon loadout"]),
    ("Wolf Destroyers",lambda s:s=="Burst Cyclic Rifles + Hand Weapons",["Replace Burst Cyclic Rifle"]),
]:
    for branch in branches(name):
        for slot in slots:
            assert len(model_groups(branch,slot)) == int(eligible(branch.get("name"))), (name,branch.get("name"),slot)
for branch in branches("Werewolf Brothers"):
    name = branch.get("name")
    assert len(model_groups(branch,"Replace Energy Were-Claws")) == (0 if "Hammers" in name else 3)
    assert sum(e.get("name")=="Backpack-GL" for m in entries(branch) for e in entries(m)) == (3 if "Backpack-GLs" in name else 0)
for branch in branches("Wolf Veteran Assault Brothers"):
    name=branch.get("name")
    assert len(model_groups(branch,"Replace Flamer Pistol")) == (3 if name=="Flamer Pistols + Hand Weapons" else 0)
    assert len(model_groups(branch,"Replace Hand Weapon")) == (3 if "Hand Weapons" in name else 0)
for branch in branches("Wolf Riders"):
    name=branch.get("name")
    assert len(model_groups(branch,"Replace Heavy Pistol")) == (3 if name=="Heavy Pistols + Hand Weapons" else 0)
    assert len(model_groups(branch,"Replace Hand Weapon")) == (0 if name=="Dual Energy Claws" else 3)
print(f"PASS Wolf Brothers: {cases} reachable rule states, {modifier_count} modifiers, {affected} units; targeted squad replacement gates.")
