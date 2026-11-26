#!/usr/bin/env python3
"""Audit parent-level Robot Legions rule links against permanent unit rules."""
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

N = {"c": "http://www.battlescribe.net/schema/catalogueSchema"}
root = ET.parse(Path("Robot_Legions.cat")).getroot()
def norm(text):
    import re
    return re.sub(r"\(\d+\)", "(X)", text.strip())
ids = [n.attrib["id"] for n in root.iter() if "id" in n.attrib]
duplicates = [name for name, total in Counter(ids).items() if total > 1]
assert not duplicates, f"Duplicate IDs: {duplicates[:10]}"
from validation_common import SYSTEM_IDS, rule_definitions
known = set(ids) | SYSTEM_IDS
units = root.findall("./c:selectionEntries/c:selectionEntry[@type='unit']", N)
assert len(units) == 32, f"Expected 32 units, found {len(units)}"
for node in root.iter():
    if node.tag.endswith("infoLink"):
        assert node.attrib.get("targetId") in (rule_definitions(root) if node.get("type")=="rule" else known), f"Dangling rule: {node.attrib}"
for unit in units:
    names = {
        norm(piece)
        for characteristic in unit.findall("./c:profiles/c:profile/c:characteristics/c:characteristic[@name='Special Rules']", N)
        for piece in (characteristic.text or "").split(",")
    }
    for link in unit.findall("./c:infoLinks/c:infoLink", N):
        label = norm(link.attrib["name"])
        is_unique_hero = label == "Hero" and "Unique Hero" in names
        is_ravage = label == "Ravage" and any(r.startswith("Ravage(") for r in names)
        assert label in names or is_unique_hero or is_ravage, (
            f"{unit.attrib['name']} has non-innate parent rule: {link.attrib['name']}"
        )
    for group in unit.findall(".//c:selectionEntryGroup", N):
        default = group.attrib.get("defaultSelectionEntryId")
        if default:
            children = {x.attrib["id"] for x in group.findall("./c:selectionEntries/c:selectionEntry", N)}
            assert default in children, f"Bad default in {unit.attrib['name']}: {group.attrib.get('name')}"

# Conditional armour must be visible only when its actual upgrade is selected.
armour_upgrades = {
    "rl36p-e17fc28e3f14": "Guardians individual Combat Shield",
    "rl36-3607fed05ccf": "Guardians squad Combat Shield configuration",
    "rl36-b5c114cc5206": "Tripod Walker Extra Armor",
    "rl36-5cf99b598f53": "Transport Tank Extra Armor",
}
for entry_id, description in armour_upgrades.items():
    upgrade = root.find(f".//c:selectionEntry[@id='{entry_id}']", N)
    assert upgrade is not None, f"Missing {description}"
    links = upgrade.findall("./c:infoLinks/c:infoLink", N)
    assert any(l.attrib.get("name") == "Armor(2+)" for l in links), (
        f"Missing equipped-only Armor(2+) rule on {description}"
    )

print("PASS: 32 Robot Legions units; no stray parent-rule links, duplicate IDs, dangling rule targets or invalid group defaults.")
print("NOTE: Visual New Recruit verification and source-to-PDF ability comparison remain separate.")
