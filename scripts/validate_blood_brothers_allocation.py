#!/usr/bin/env python3
"""Static allocation guard: all represented choices preserve source model counts.
Does not certify source option completeness or New Recruit runtime behaviour."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Blood_Brothers.cat").getroot()
expected = json.loads((ROOT / "reference/blood-brothers-defaults.json").read_text())["units"]
units = {u.get("name"): u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type") == "unit"}
assert set(units) == set(expected)
group_count = weapon_count = 0

def entries(node):
    return node.findall(f"./{N}selectionEntries/{N}selectionEntry")

def groups(node):
    return node.findall(f"./{N}selectionEntryGroups/{N}selectionEntryGroup")

def limits(node):
    cs = node.findall(f"./{N}constraints/{N}constraint")
    assert len(cs) == 2 and {c.get("type") for c in cs} == {"min", "max"}, node.get("name")
    assert all(c.get("scope") == "parent" and c.get("field") == "selections" for c in cs), node.get("name")
    return tuple(int(float(next(c.get("value") for c in cs if c.get("type") == kind))) for kind in ("min", "max"))

def add(a, b):
    return {x+y for x in a for y in b}

def choice(group, in_model):
    global group_count
    group_count += 1
    opts = entries(group)
    lo, hi = limits(group)
    assert (lo, hi) in {(0, 1), (1, 1)} and opts, group.get("name")
    default = group.get("defaultSelectionEntryId")
    assert (default in {o.get("id") for o in opts}) if lo else not default, group.get("name")
    assert len({o.get("id") for o in opts}) == len(opts), group.get("name")
    result = {0} if lo == 0 else set()
    for option in opts:
        result |= count(option, in_model)
    return result

def count(node, in_model=False):
    global weapon_count
    is_model = node.get("type") == "model"
    if is_model:
        assert not in_model and limits(node) == (1, 1), node.get("name")
    in_model = in_model or is_model
    for p in node.findall(f"./{N}profiles/{N}profile"):
        if p.get("typeName") in ("Melee Weapon", "Ranged Weapon"):
            assert in_model, (node.get("name"), p.get("name"), "weapon outside model")
            weapon_count += 1
    possible = {int(is_model)}
    for child in entries(node):
        result = count(child, in_model)
        lo, hi = limits(child)
        assert hi == 1 and lo in (0, 1), child.get("name")
        if lo == 0:
            result.add(0)
        possible = add(possible, result)
    for group in groups(node):
        possible = add(possible, choice(group, in_model))
    return possible

for name, unit in units.items():
    assert count(unit) == {expected[name]["models"]}, (name, "model count changes with equipment")
print(f"PASS Blood Brothers static allocation: {len(units)} units, {group_count} choice groups, {weapon_count} model-owned weapon profiles.")

# Source pages 7–10: targeted replacement gate checks. Designated model
# slots are not a proof that every legal co-location of upgrades is supported.
def named_group(node, name):
    return next(g for g in groups(node) if g.get("name") == name)
def branches(name):
    return entries(named_group(units[name], "Squad loadout"))
def model_slots(node, name):
    return [g for m in entries(node) if m.get("type") == "model"
            for g in groups(m) if g.get("name") == name]
def options(group):
    return {o.get("name") for o in entries(group)}
for unit_name, eligible, slots in [
    ("Blood Pathfinders", lambda n:n=="Heavy Rifles", ("Replace Heavy Rifle","Sergeant weapon loadout")),
    ("Blood Brother Bikers", lambda n:n.endswith("Heavy Rifles + Strikes"), ("Replace Heavy Rifle","Sergeant weapon loadout")),
    ("Blood Destroyers", lambda n:n=="Burst Cyclic Rifles + Hand Weapons", ("Replace Burst Cyclic Rifle",)),
]:
    for branch in branches(unit_name):
        for slot in slots:
            assert len(model_slots(branch,slot)) == int(eligible(branch.get("name"))), (unit_name,branch.get("name"),slot)
for branch in branches("Blood Death Brothers"):
    rifle = branch.get("name") == "Heavy Rifles + Strikes"
    assert len(model_slots(branch,"Special weapon loadout")) == int(rifle)
    assert len(model_slots(branch,"Replace Heavy Pistol")) == int(not rifle)
    if rifle:
        special = next(o for o in entries(model_slots(branch,"Special weapon loadout")[0]) if o.get("name") == "Heavy Pistol + Energy Hammer")
        assert "Replace Heavy Pistol" in {g.get("name") for g in groups(special)}
        assert "Replace Energy Hammer" in {g.get("name") for g in groups(special)}
for branch in branches("Blood Veteran Assault Brothers"):
    name = branch.get("name")
    assert len(model_slots(branch,"Replace Flamer Pistol")) == (3 if name=="Flamer Pistols + Hand Weapons" else 0)
    assert len(model_slots(branch,"Replace Hand Weapon")) == (3 if "Hand Weapons" in name else 0)
guard = units["Blood Guard Brothers"]
pistols = model_slots(guard,"Replace Heavy Pistol")
assert len(pistols)==5 and all("Plasma Pistol" in options(g) for g in pistols)
assert sum("Burst Fusion Pistol" in options(g) for g in pistols)==1
assert len(model_slots(guard,"Replace Energy Lance"))==5
assault = units["Blood Assault Brothers"]
special = model_slots(assault,"Special weapon loadout")[0]
for o in entries(special):
    if o.get("name").startswith("Heavy Pistol + "):
        assert "Plasma Pistol" in options(named_group(o,"Replace Heavy Pistol")), o.get("name")
    else:
        assert not any(g.get("name")=="Replace Heavy Pistol" for g in groups(o)), o.get("name")
assert len(model_slots(assault,"Sergeant weapon loadout"))==1
assert len(model_slots(assault,"Replace Heavy Pistol"))==3
battle = units["Blood Battle Brothers"]
for slot in ("Replace Heavy Rifle","Sergeant weapon loadout","Squad specialist"):
    assert len(model_slots(battle,slot))==1, slot
print("PASS Blood Brothers: eight targeted squad replacement and allocation checks.")
