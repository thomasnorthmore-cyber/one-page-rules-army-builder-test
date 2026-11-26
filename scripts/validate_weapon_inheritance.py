#!/usr/bin/env python3
"""Check scoped New Recruit profile modifiers against recorded grant sources.
Evaluates XML conditions offline; does not substitute for New Recruit UI testing.
"""
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

N = "{http://www.battlescribe.net/schema/catalogueSchema}"
manifest = json.loads(Path("reference/weapon-inheritance.json").read_text())
assert set(manifest) == {p.name for p in Path(".").glob("*.cat")}
total = cases = 0

def test_condition(c, selected):
    assert c.get("field") == "selections" and c.get("value") == "0"
    assert c.get("includeChildSelections") == "true"
    assert c.get("includeChildForces") == "false"
    key = (c.get("scope"), c.get("childId"))
    assert c.get("type") in ("greaterThan", "equalTo")
    return (key in selected) == (c.get("type") == "greaterThan")

def test_modifier(m, selected):
    return (all(test_condition(c, selected) for c in m.findall(f"./{N}conditions/{N}condition"))
        and all(g.get("type") == "or" and any(test_condition(c, selected) for c in g.findall(f"./{N}conditions/{N}condition")) for g in m.findall(f"./{N}conditionGroups/{N}conditionGroup")))

for filename, records in manifest.items():
    root = ET.parse(filename).getroot()
    by_id = {e.get("id"): e for e in root.iter() if e.get("id")}
    parents = {child: parent for parent in root.iter() for child in parent}
    def ancestors(e):
        while e in parents:
            e = parents[e]
            yield e
    profiles = {p.get("id"): p for p in root.iter(N+"profile")}
    seen = set()
    for record in records:
        p = profiles[record["profile"]]
        assert p.get("id") not in seen
        seen.add(p.get("id"))
        assert p.get("typeName") in ("Melee Weapon", "Ranged Weapon")
        assert p.get("name") == record["weapon"]
        field = record["field"]
        ch = p.find(f"./{N}characteristics/{N}characteristic[@typeId='{field}']")
        assert ch is not None and ch.get("name") == "Special Rules"
        assert (ch.text or "") == record["base"]
        native = [x.strip() for x in record["base"].split(",") if x.strip() not in ("", "-", "undefined")]
        conditions = record["conditional"]
        keys = sorted({(c["scope"], c["child"]) for g in conditions for c in g["conditions"]})
        for scope, child in keys:
            assert by_id[scope] in set(ancestors(p)), (filename, p.get("name"), scope)
            assert by_id[scope] in set(ancestors(by_id[child])), (filename, scope, child)
            assert by_id[scope].get("type") in ("unit", "model")
        mods = p.findall(f"./{N}modifiers/{N}modifier")
        assert mods and all(m.get("type") == "set" and m.get("field") == field for m in mods)
        for m in mods:
            for c in m.iter(N+"condition"):
                assert (c.get("scope"), c.get("childId")) in keys
        for bits in itertools.product((False, True), repeat=len(keys)):
            selected = {k for k,b in zip(keys,bits) if b}
            active = record["fixed"] + [g["keyword"] for g in conditions if any((c["scope"],c["child"]) in selected for c in g["conditions"])]
            matched = [m for m in mods if test_modifier(m, selected)]
            assert len(matched) <= 1, (filename, p.get("name"), selected)
            actual = matched[0].get("value") if matched else record["base"]
            expected = ", ".join(native + active) if active else record["base"]
            assert actual == expected, (filename, p.get("name"), selected, actual, expected)
            assert len(set(native + active)) == len(native + active)
            cases += 1
        total += 1
    actual_profiles = {p.get("id") for p in profiles.values() if p.get("typeName") in ("Melee Weapon","Ranged Weapon") and p.find(f"./{N}modifiers") is not None}
    assert actual_profiles == seen, (filename, actual_profiles ^ seen)
    print(f"PASS {filename}: {len(records)} modified weapon profiles")
print(f"PASS {total} weapon profiles, {cases} selection combinations; offline modifier semantics only")
