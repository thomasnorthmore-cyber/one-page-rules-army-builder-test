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
from validation_common import factions, rule_definitions, norm as normalize

errors = []
warnings = []
count_profiles = 0
count_entries = 0
for path, root in factions():
    filename = path.name
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    duplicates = [k for k, v in Counter(ids).items() if v > 1]
    if duplicates:
        errors.append(f"{filename}: duplicate XML IDs: {duplicates[:10]}")
    defs = rule_definitions(root)
    rule_ids = set(defs)
    rule_names = {normalize(node.get("name")) for node in defs.values()}
    for link in root.iter(f"{N}infoLink"):
        if link.get("type") == "rule" and link.get("targetId") not in rule_ids:
            errors.append(f"{filename}: invalid rule link {link.get('name')}: {link.get('targetId')}")
    for entry in root.iter(f"{N}selectionEntry"):
        count_entries += 1
        direct_links = {normalize(l.get("name")) for l in entry.findall(f"./{N}infoLinks/{N}infoLink")}
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
            traits = [t.strip() for t in raw.split(",") if t.strip() not in ("", "-", "undefined")]
            for trait in traits:
                norm = normalize(trait)
                if norm not in direct_links:
                    errors.append(f"{filename}: {label} / {name}: missing equipped-only rule link '{norm}'")
                if norm not in rule_names and not any(normalize(l.get("name"))==norm and l.get("targetId") in rule_ids for l in entry.findall(f"./{N}infoLinks/{N}infoLink")):
                    errors.append(f"{filename}: {label} / {name}: missing rule definition '{norm}'")
    for entry in root.iter(f"{N}selectionEntry"):
        if entry.get("type") != "upgrade":
            continue
        # A leaf wargear upgrade must grant a weapon profile, a rule link,
        # or contain another selected entry. Never silently accept an inert option.
        has_profile = entry.find(f"./{N}profiles/{N}profile") is not None
        has_rule = entry.find(f"./{N}infoLinks/{N}infoLink") is not None
        has_children = (
            entry.find(f"./{N}selectionEntries/{N}selectionEntry") is not None
            or entry.find(f"./{N}selectionEntryGroups/{N}selectionEntryGroup") is not None
        )
        if not (has_profile or has_rule or has_children):
            errors.append(f"{filename}: inert upgrade without profile or rule: {entry.get('name')}")
    print(f"{filename}: {len(root.findall(f'./{N}selectionEntries/{N}selectionEntry[@type="unit"]'))} units checked")
for msg in warnings:
    print("SOURCE REVIEW:", msg)
for err in errors[:100]:
    print("FAIL:", err)
print(f"Audited {count_entries} selection entries and {count_profiles} weapon profiles.")
print(f"Result: {len(errors)} errors; {len(warnings)} source-review items.")
sys.exit(1 if errors else 0)
