#!/usr/bin/env python3
"""Static allocation guard: all represented choices preserve source model counts.
Does not certify source option completeness or New Recruit runtime behaviour."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Wolf_Brothers.cat").getroot()
expected = json.loads((ROOT / "reference/wolf-brothers-defaults.json").read_text())["units"]
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
print(f"PASS Wolf Brothers static allocation: {len(units)} units, {group_count} choice groups, {weapon_count} model-owned weapon profiles.")
