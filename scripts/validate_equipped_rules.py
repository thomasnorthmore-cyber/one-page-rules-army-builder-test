#!/usr/bin/env python3
"""Cross-army test: rules from equipped wargear must be linked to its selection."""
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET

ns = {"c": "http://www.battlescribe.net/schema/catalogueSchema"}
cases = {
    "Battle_Brothers.cat": {
        "Armor(2+)": ["opr36-18ac7", "opr36-18ae5"],
        "Unstoppable Mark": ["opr36-18a92", "opr36-18aa6"],
        "Flying": [
            "opr36c-494c4", "opr36c-494c5", "opr36c-4944a", "opr36c-4944b",
            "opr36d-61b90", "opr36d-61b91", "opr36f-92802", "opr36f-92803",
            "opr36f-9288d", "opr36f-9288e", "opr36f-928ac", "opr36f-928ad",
            "opr36f-928d1", "opr36f-928d2"
        ]
    },
    "Robot_Legions.cat": {
        "Armor(2+)": [
            "rl36p-e17fc28e3f14", "rl36-3607fed05ccf",
            "rl36-b5c114cc5206", "rl36-5cf99b598f53"
        ],
        "Fast": ["rl36-c463bce13f8b"],
        "Transport(X)": ["rl36-545603846b8e", "rl36-0847519da596"],
        "Ambush": ["rl36-c39895bc7269", "rl36-37489482468f", "rl36-eedea5b8ced2", "rl36-60457b72a6ac", "rl36-1e89450e48e7"],
        "Fear(X)": ["rl36-f992c773ee2a"],
        "Rending in Melee": ["rl36-ced1734a694d", "rl36-4f71817c1b09"],
        "Scout": ["rl36-rapid-skimmer-standard", "rl36-94709f164b0e"]
    },
    "Custodian_Brothers.cat": {}
}
for path, expected in cases.items():
    root = ET.parse(Path(path)).getroot()
    ids = [n.attrib["id"] for n in root.iter() if "id" in n.attrib]
    assert len(ids) == len(set(ids)), f"{path}: duplicate XML IDs"
    known = set(ids)
    for node in root.iter():
        if node.tag.endswith("infoLink"):
            assert node.attrib["targetId"] in known, f"{path}: dangling rule target"
    for rule, entry_ids in expected.items():
        for entry_id in entry_ids:
            entry = root.find(f".//c:selectionEntry[@id='{entry_id}']", ns)
            assert entry is not None, f"{path}: missing equipment {entry_id}"
            linked = [n.attrib["name"] for n in entry.findall("./c:infoLinks/c:infoLink", ns)]
            assert rule in linked, f"{path}: {entry_id} missing equipped {rule}"
    print(f"PASS {path}: unique IDs, valid rule targets, conditional upgrades checked")
print("Reminder: New Recruit display and PDF/source-by-source parity require separate checks")


# Check that a purchased replacement never leaves its starting weapon active.
replacement_cases = {
    "Battle_Brothers.cat": {"opr36c-49558": "Hand Weapon"},
    "Robot_Legions.cat": {
        "rl36-f00197c26637": "Burst Wrist-Spark",
        "rl36-5eded7729c0b": "Hand Weapon",
        "rl36-1aee7a53976e": "Hand Weapon",
        "rl36-base-c99d7c1-a7a7d9a": "Hand Weapon",
        "rl36-0a06d06666aa": "Hand Weapon",
        "rl36-090dfa340707": "Hand Weapon",
        "rl36-8da5e915b607": "Hand Weapon",
        "rl36-7a20140900b5": "Radium Cannon",
        "rl36-7d2c1d45ad13": "Radium Cannon",
    },
}
for path, cases in replacement_cases.items():
    root = ET.parse(path).getroot()
    for entry_id, weapon_name in cases.items():
        entry = root.find(f".//c:selectionEntry[@id='{entry_id}']", ns)
        assert entry is not None, f"{path}: lost equipment selection {entry_id}"
        assert entry.find(f"./c:profiles/c:profile[@name='{weapon_name}']", ns) is None, (
            f"{path}: {entry_id} still permanently equips replaced {weapon_name}"
        )
        groups = entry.findall("./c:selectionEntryGroups/c:selectionEntryGroup", ns)
        groups = [g for g in groups if (g.get("name") or "").startswith("Replace ")]
        assert groups, f"{path}: missing replacement group {entry_id}"
        group = groups[0]
        default_id = group.get("defaultSelectionEntryId")
        options = group.findall("./c:selectionEntries/c:selectionEntry", ns)
        default = next((o for o in options if o.get("id") == default_id), None)
        assert default is not None, f"{path}: no default equipped weapon for {entry_id}"
        assert default.find(f"./c:profiles/c:profile[@name='{weapon_name}']", ns) is not None, (
            f"{path}: default option does not equip {weapon_name}"
        )
        constraints = {c.get("type"): c.get("value") for c in group.findall("./c:constraints/c:constraint", ns)}
        assert constraints.get("min") == "1" and constraints.get("max") == "1", (
            f"{path}: replacement must be exactly one choice for {entry_id}"
        )
print("PASS: 10 conditional weapon replacements do not retain their unequipped weapons.")
