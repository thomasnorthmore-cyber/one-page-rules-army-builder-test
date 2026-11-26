#!/usr/bin/env python3
"""Exhaustive structural audit for equipped weapon rule links in all OPR catalogues.

Walk every model, unit, equipment and upgrade entry, inspecting ONLY directly
owned weapon profiles. Weapon keywords must be linked on the same selectable
entry, not on its parent unit or an unselected sibling.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

N = "{http://www.battlescribe.net/schema/catalogueSchema}"
FILES = ("Battle_Brothers.cat", "Robot_Legions.cat", "Custodian_Brothers.cat")
CORE_RULES = {"AP", "Blast", "Deadly"}
EXCEPTIONS = {
    # These special-rule cells contain combined vehicle/pilot wargear text,
    # NOT a list of weapon keywords. They require source-led remodeling.
    ("Robot_Legions.cat", "Thruster Bike", "Thruster Bike"),
    ("Robot_Legions.cat", "Skimmer Bike", "Skimmer Bike"),
    ("Robot_Legions.cat", "Overseer Pilot", "Overseer Pilot"),
}

def normalize(name: str) -> str:
    if re.fullmatch(r"(AP|Blast|Deadly)\(\d+\)", name):
        return re.sub(r"\(\d+\)", "(X)", name)
    return name

errors = []
warnings = []
count_profiles = 0
count_entries = 0
for filename in FILES:
    root = ET.parse(Path(filename)).getroot()
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    duplicates = [k for k, v in Counter(ids).items() if v > 1]
    if duplicates:
        errors.append(f"{filename}: duplicate XML IDs: {duplicates[:10]}")
    rule_ids = {node.get("id") for node in root.findall(f"./{N}sharedRules/{N}rule")}
    rule_names = {node.get("name") for node in root.findall(f"./{N}sharedRules/{N}rule")}
    for link in root.iter(f"{N}infoLink"):
        if link.get("type") == "rule" and link.get("targetId") not in rule_ids:
            errors.append(f"{filename}: invalid rule link {link.get('name')}: {link.get('targetId')}")
    for entry in root.iter(f"{N}selectionEntry"):
        count_entries += 1
        direct_links = {l.get("name") for l in entry.findall(f"./{N}infoLinks/{N}infoLink")}
        for prof in entry.findall(f"./{N}profiles/{N}profile"):
            if prof.get("typeName") not in ("Ranged Weapon", "Melee Weapon"):
                continue
            count_profiles += 1
            name = prof.get("name", "")
            label = entry.get("name", "")
            chars = prof.find(f"./{N}characteristics")
            raw = ""
            if chars is not None:
                for characteristic in chars:
                    if characteristic.get("name") == "Special Rules":
                        raw = (characteristic.text or "").strip()
                        break
            if (filename, label, name) in EXCEPTIONS:
                warnings.append(f"{filename}: malformed combined wargear profile {label} / {name} must be remodeled")
                continue
            traits = [t.strip() for t in raw.split(",") if t.strip() not in ("", "-", "undefined")]
            for trait in traits:
                norm = normalize(trait)
                if norm not in direct_links:
                    errors.append(f"{filename}: {label} / {name}: missing equipped-only rule link '{norm}'")
                if norm not in rule_names:
                    errors.append(f"{filename}: {label} / {name}: missing rule definition '{norm}'")
    print(f"{filename}: {len(root.findall(f'./{N}selectionEntries/{N}selectionEntry'))} units checked")
for msg in warnings:
    print("SOURCE REVIEW:", msg)
for err in errors[:100]:
    print("FAIL:", err)
print(f"Audited {count_entries} selection entries and {count_profiles} weapon profiles.")
print(f"Result: {len(errors)} errors; {len(warnings)} source-review items.")
sys.exit(1 if errors else 0)
