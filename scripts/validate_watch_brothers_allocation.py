#!/usr/bin/env python3
"""Static allocation guard: all represented choices preserve source model counts.
Does not certify source option completeness or New Recruit runtime behaviour."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Watch_Brothers.cat").getroot()
expected = json.loads((ROOT / "reference/watch-brothers-defaults.json").read_text())["units"]
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
print(f"PASS Watch Brothers static allocation: {len(units)} units, {group_count} choice groups, {weapon_count} model-owned weapon profiles.")

# PDF pp.4–8: verify replacement prerequisites and independent model choices.
def group(node,name):
    matches=[g for g in groups(node) if g.get("name")==name]
    assert len(matches)==1,(node.get("name"),name)
    return matches[0]
def names(node):
    return {o.get("name") for o in entries(node)}
def slots(branch,name):
    return [g for m in entries(branch) if m.get("type")=="model" for g in groups(m) if g.get("name")==name]
def branches(name):
    return entries(group(units[name],"Squad loadout"))
def find_option(g,name):
    matches=[e for e in entries(g) if e.get("name")==name]
    assert len(matches)==1,(g.get("name"),name)
    return matches[0]
def attachment(option,base_weapon,allowed):
    g=group(option,base_weapon+" attachment")
    assert limits(g)==(0,1) and names(g)==allowed,(base_weapon,names(g))
mods={"Flamer-Mod","Plasma-Mod","Arc-Charger-Mod","Fusion-Mod","Anti-Matter-Mod"}
for name in ("Watch Master Brother","Watch Battle Brothers","Watch Vanguard"):
    unit=units[name]
    models=[m for m in entries(unit) if m.get("type")=="model"]
    assert len(models)==expected[name]["models"]
    for m in models:
        loadout=group(m,"Weapon loadout")
        for o in entries(loadout):
            label=o.get("name")
            group_names={g.get("name") for g in groups(o)}
            assert ("Replace Flamer" in group_names)==(label in ("Flamer + Hand Weapon","Flamer + Strike"))
            assert ("Replace Flamer Pistol" in group_names)==(label=="Flamer Pistol + Hand Weapon")
            assert ("Replace Hand Weapon" in group_names)==(label in ("Flamer + Hand Weapon","Flamer Pistol + Hand Weapon"))
            if "Replace Flamer" in group_names:
                rifles=group(o,"Replace Flamer")
                attachment(find_option(rifles,"Burst Heavy Rifle"),"Burst Heavy Rifle",mods)
                if name=="Watch Battle Brothers":
                    attachment(find_option(rifles,"Heavy Machinegun"),"Heavy Machinegun",{"Flamer-Mod"})
                for rifle in entries(rifles):
                    for g in groups(rifle):
                        assert g.get("name")==rifle.get("name")+" attachment", (name,rifle.get("name"),g.get("name"))
        if name=="Watch Vanguard":
            assert names(loadout)=={"Flamer Pistol + Hand Weapon","Dual Energy Claws","Great Energy Hammer"}
    if name!="Watch Master Brother":
        assert len(slots(unit,"Squad specialist"))==1
        assert limits(slots(unit,"Squad specialist")[0])==(0,1)
for name,gear in [("Watch Battle Brothers","Combat Shield"),("Watch Vanguard","Combat Shields")]:
    assert limits(group(units[name],gear))==(0,1)
assert limits(group(units["Watch Vanguard"],"Aerial Drop"))==(0,1)
master=entries(units["Watch Master Destroyer"])[0]
for o in entries(group(master,"Weapon loadout")):
    assert any(g.get("name")=="Replace Hand Weapon" for g in groups(o))==("Hand Weapon" in o.get("name"))
for branch in branches("Watch Destroyers"):
    label=branch.get("name")
    assert len(slots(branch,"Replace Hand Weapon"))==(0 if label=="Dual Energy Claws" else 3)
    assert len(slots(branch,"Replace Burst Cyclic Rifle"))==int(label=="Burst Cyclic Rifles + Hand Weapons")
    assert len(slots(branch,"Combat Shield"))==(3 if label=="Hand Weapons + Combat Shields" else 0)
    assert len(slots(branch,"Squad specialist"))==1
for branch in branches("Watch Brother Bikers"):
    label=branch.get("name")
    rifle=label.endswith("Heavy Rifles + Strikes")
    bike="Assault Heavy Bike-Rifle" if label.startswith("Assault") else "Heavy Bike-Rifle"
    assert len(slots(branch,bike))==3
    assert len(slots(branch,"Replace Heavy Rifle"))==int(rifle)
    assert len(slots(branch,"Sergeant weapon loadout"))==int(rifle)
    if rifle:
        sergeant=find_option(slots(branch,"Sergeant weapon loadout")[0],"Sergeant loadout")
        assert names(group(sergeant,"Replace Sgt. Arc-Charger Pistol"))=={"Sgt. Arc-Charger Pistol","Heavy Pistol","Anti-Matter Pistol","Plasma Pistol"}
        assert names(group(sergeant,"Replace Sgt. Hand Weapon"))=={"Sgt. Hand Weapon","Energy Sword","Energy Fist"}
    else:
        assert len(slots(branch,"Heavy Pistol"))==3 and len(slots(branch,"Hand Weapon"))==3
arms=slots(units["Watch Combat Walker"],"Replace Walker Combat Fist")
assert len(arms)==2
for arm in arms:
    for o in entries(arm):
        label=o.get("name")
        assert any(g.get("name")=="Replace Heavy Flamer" for g in groups(o))==label.startswith("Heavy Flamer +")
        assert any(g.get("name")=="Replace Assault Heavy Flamer" for g in groups(o))==label.startswith("Assault Heavy Flamer +")
# Duplicate Targeting Array source row provisionally represented once.
assert len(slots(units["Watch Drop Pod"],"Targeting Array"))==1
assert limits(slots(units["Watch Drop Pod"],"Targeting Array")[0])==(0,1)
# The source prints cargo in the linked-rifle replacement group; retain that
# interpretation provisionally and ensure mutually exclusive choices.
gunship=entries(units["Watch Deathstar Gunship"])[0]
g=group(gunship,"Replace Strafing Linked Heavy Rifle-Arrays")
assert limits(g)==(1,1)
assert names(g)=={"Strafing Linked Heavy Rifle-Arrays","Cluster Bombs","Cargo Space"}
print("PASS Watch Brothers: source-specific attachment, specialist, shield, biker, walker and gunship replacement gates.")
