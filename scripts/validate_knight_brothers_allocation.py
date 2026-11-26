#!/usr/bin/env python3
"""Static allocation guard: all represented choices preserve source model counts.
Does not certify source option completeness or New Recruit runtime behaviour."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Knight_Brothers.cat").getroot()
expected = json.loads((ROOT / "reference/knight-brothers-defaults.json").read_text())["units"]
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
print(f"PASS Knight Brothers static allocation: {len(units)} units, {group_count} choice groups, {weapon_count} model-owned weapon profiles.")

# PDF pp.4–8: source-specific replacement gates.
def group(node, name):
    found=[g for g in groups(node) if g.get("name")==name]
    assert len(found)==1, (node.get("name"),name)
    return found[0]
def names(node):
    return {o.get("name") for o in entries(node)}
def slots(branch, name):
    return [g for m in entries(branch) if m.get("type")=="model" for g in groups(m) if g.get("name")==name]
def branches(name):
    return entries(group(units[name],"Squad loadout"))
def psychic(branch):
    assert len(slots(branch,"Psychic"))==1
    assert limits(slots(branch,"Psychic")[0])==(0,1)
for branch in branches("Knight Battle Brothers"):
    name=branch.get("name")
    rifle=name=="Cyclic Rifles + Strikes"
    assert len(slots(branch,"Replace Cyclic Rifle"))==int(rifle)
    assert len(slots(branch,"Special weapon loadout"))==int(rifle)
    if rifle:
        assert names(slots(branch,"Replace Cyclic Rifle")[0])=={"Cyclic Rifle","Slayer Blaze-Flamer","Slayer Chain-Cannon","Slayer Volley-Gun"}
        assert names(slots(branch,"Special weapon loadout")[0])=={"Cyclic Rifle + Strike","Dual Energy Sabres","Assault Cyclic Rifle + Slayer Hammer"}
    else:
        assert name.startswith("Assault Cyclic Rifles + ")
        assert len(slots(branch,"Assault Cyclic Rifle"))==5
        assert len(slots(branch,name.split(" + ")[1]))==5
    psychic(branch)
    assert len(slots(branch,"Squad specialist"))==1
for branch in branches("Knight Veteran Brothers"):
    name=branch.get("name")
    assert len(slots(branch,"Replace Slayer Blaze-Flamer"))==(3 if name=="Slayer Blaze-Flamers + Strikes" else 0)
    assert len(slots(branch,"Replace Hand Weapon"))==(3 if name=="Assault Cyclic Rifles + Hand Weapons" else 0)
    psychic(branch)
    assert len(slots(branch,"Squad specialist"))==1
for branch in branches("Knight Destroyers"):
    name=branch.get("name")
    assert len(slots(branch,"Replace Hand Weapon"))==(0 if name=="Dual Energy Sabres" else 3)
    assert len(slots(branch,"Replace Burst Cyclic Rifle"))==int(name=="Burst Cyclic Rifles + Hand Weapons")
    psychic(branch)
    assert len(slots(branch,"Squad specialist"))==1
assert len(slots(units["Knight Purgation Brothers"],"Replace Slayer Blaze-Flamer"))==3
psychic(units["Knight Purgation Brothers"])
for name in ("Knight Master Destroyer","Knight Veteran Master Brother","Knight Master Brother"):
    model=entries(units[name])[0]
    for option in entries(group(model,"Weapon loadout")):
        label=option.get("name")
        assert any(g.get("name")=="Replace Hand Weapon" for g in groups(option))==("Hand Weapon" in label)
        assert any(g.get("name")=="Burst Heavy Rifle attachment" for g in groups(option))==label.startswith("Burst Heavy Rifle")
        assert any(g.get("name")=="Replace Flamer Pistol" for g in groups(option))==label.startswith("Flamer Pistol")
for name in ("Knight Combat Walker","Knight Veteran Combat Walker"):
    arms=slots(units[name],"Replace Walker Combat Fist")
    assert len(arms)==2
    for arm in arms:
        for option in entries(arm):
            label=option.get("name")
            assert any(g.get("name")=="Replace Heavy Flamer" for g in groups(option))==label.startswith("Light Walker Fist +")
            assert any(g.get("name")=="Replace Assault Heavy Flamer" for g in groups(option))==label.startswith("Walker Fist +")
arms=slots(units["Knight Nemesis Walker"],"Replace Heavy Walker Slayer Hammer")
assert len(arms)==2
for arm in arms:
    for option in entries(arm):
        assert any(g.get("name")=="Replace Walker Slayer Hammer" for g in groups(option))==option.get("name").endswith(" + Walker Slayer Hammer")
print("PASS Knight Brothers: ten targeted source replacement gate checks.")
