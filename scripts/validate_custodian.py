#!/usr/bin/env python3
"""Validate Custodian Brothers v3.6.0 structural integrity and source base roster."""
import collections
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"c": "http://www.battlescribe.net/schema/catalogueSchema"}
CAT = Path("Custodian_Brothers.cat")
root = ET.parse(CAT).getroot()
expected = {
    "Master Destroyer": 245,
    "Veteran Master Custodian": 170,
    "Master Custodian": 155,
    "Great Sister": 55,
    "Vigilant Sisters": 80,
    "Prosecution Sisters": 90,
    "Hunter Sisters": 90,
    "Custodian Brothers": 225,
    "Veteran Custodian Brothers": 250,
    "Jetpack Custodian Brothers": 265,
    "Support Custodian Brothers": 335,
    "Destroyer": 160,
    "Custodian APC": 195,
    "Anti-Grav Attack Vehicle": 210,
    "Veteran Destroyer": 215,
    "Custodian Jetbiker": 245,
    "Custodian Combat Walker": 385,
    "Custodian Assault Walker": 415,
    "Anti-Grav Battle Tank": 505,
    "Custodian Heavy Combat Walker": 585,
    "Heavy Anti-Grav Carrier": 790,
    "Custodian Heavy Tank": 815,
}
ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
duplicate = [id_ for id_, n in collections.Counter(ids).items() if n > 1]
assert not duplicate, f"Duplicate IDs: {duplicate[:10]}"
all_ids = set(ids)
for node in root.iter():
    if node.tag.endswith("infoLink"):
        assert node.attrib.get("targetId") in all_ids, f"Unresolved rule: {node.attrib}"
    if node.tag.endswith("selectionEntryGroup"):
        default = node.attrib.get("defaultSelectionEntryId")
        if default:
            children = {c.attrib["id"] for c in node.findall("./c:selectionEntries/c:selectionEntry", NS)}
            assert default in children, f"Invalid default selection: {node.attrib.get('name')}"
    if node.tag.endswith("selectionEntry"):
        for c in node.findall("./c:constraints/c:constraint", NS):
            if c.attrib.get("type") == "min" and c.attrib.get("value") == "1":
                assert any(x.tag.endswith(("selectionEntries", "selectionEntryGroups", "profiles")) for x in node), f"Empty required selection {node.attrib.get('name')}"
units = root.findall("./c:selectionEntries/c:selectionEntry", NS)
assert {u.attrib["name"] for u in units} == set(expected), "Mismatch with 22 Custodian PDF units"
for unit in units:
    points = unit.find("./c:costs/c:cost", NS)
    assert points is not None and float(points.attrib["value"]) == expected[unit.attrib["name"]], f"Wrong base cost: {unit.attrib['name']}"
    models = unit.findall(".//c:selectionEntry[@type='model']", NS)
    assert models, f"No models in {unit.attrib['name']}"
print(f"PASS: {len(units)} units, {len(ids)} unique IDs, valid default loadouts and base points")
print("NOTE: XML validation does not establish complete upgrade coverage or New Recruit presentation.")
