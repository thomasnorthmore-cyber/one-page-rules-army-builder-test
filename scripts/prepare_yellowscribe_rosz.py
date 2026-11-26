#!/usr/bin/env python3
"""Promote selected non-weapon abilities into unit summary for YellowScribe.

Works with Battle Brothers, Robot Legions, Custodian Brothers and other
BattleScribe/New Recruit roster XML. Only the selected .ros/.rosz is read:
unchosen catalogue alternatives can never contribute rules.
The source roster and catalogue remain unmodified.

Usage: python scripts/prepare_yellowscribe_rosz.py list.rosz [-o converted.rosz]
"""
from __future__ import annotations

import argparse
import copy
import io
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def direct(element, tag):
    return [child for child in element if local(child) == tag]


def descendants_selected(selection):
    """Yield selected descendants, stopping at nested independent units."""
    for group in direct(selection, "selections"):
        for child in direct(group, "selection"):
            if child.get("type") == "unit":
                continue
            yield child
            yield from descendants_selected(child)


def rule_names_from_weapons(selection):
    """Weapon keywords are shown on the weapon, not as unit abilities."""
    names = set()
    for profiles in direct(selection, "profiles"):
        for profile in direct(profiles, "profile"):
            if profile.get("typeName") not in {"Ranged Weapon", "Melee Weapon"}:
                continue
            for chars in direct(profile, "characteristics"):
                for char in direct(chars, "characteristic"):
                    if char.get("name") != "Special Rules":
                        continue
                    for item in (char.text or "").split(","):
                        item = item.strip()
                        if item and item != "-":
                            names.add(item)
                            # e.g. AP(2) profile is represented by AP(X) rule
                            names.add(re.sub(r"\(\d+\)", "(X)", item))
    return names


def target_unit_profile(unit):
    for block in direct(unit, "profiles"):
        for profile in direct(block, "profile"):
            if profile.get("typeName") == "Unit":
                yield profile


def adapt(raw):
    """Return (modified roster XML, [(unit name, newly promoted rule names)])."""
    root = ET.fromstring(raw)
    ns = root.tag.split("}", 1)[0][1:] if root.tag.startswith("{") else ""
    if ns:
        ET.register_namespace("", ns)
    changes = []
    for unit in root.iter():
        if local(unit) != "selection" or unit.get("type") != "unit":
            continue
        own_rules = next(iter(direct(unit, "rules")), None)
        existing = ({r.get("name") for r in direct(own_rules, "rule")}
                    if own_rules is not None else set())
        profile_rules = set()
        profiles = list(target_unit_profile(unit))
        for profile in profiles:
            for chars in direct(profile, "characteristics"):
                for char in direct(chars, "characteristic"):
                    if char.get("name") == "Special Rules":
                        profile_rules.update(x.strip() for x in
                                             (char.text or "").split(",") if x.strip())
        promoted = []
        # Only rules carried by selections that were actually made.
        for selected in descendants_selected(unit):
            weapon_keywords = rule_names_from_weapons(selected)
            for block in direct(selected, "rules"):
                for rule in direct(block, "rule"):
                    name = (rule.get("name") or "").strip()
                    if not name or name in weapon_keywords:
                        continue
                    # Tough is sourced from the native unit profile, never links.
                    if name.startswith("Tough("):
                        continue
                    if name not in existing:
                        if own_rules is None:
                            own_rules = ET.Element(f"{{{ns}}}rules" if ns else "rules")
                            unit.insert(0, own_rules)
                        own_rules.append(copy.deepcopy(rule))
                        existing.add(name)
                    if name not in profile_rules and name not in promoted:
                        promoted.append(name)
        if not promoted:
            continue
        for profile in profiles:
            for chars in direct(profile, "characteristics"):
                for char in direct(chars, "characteristic"):
                    if char.get("name") == "Special Rules":
                        current = [x.strip() for x in (char.text or "").split(",") if x.strip()]
                        current.extend(name for name in promoted if name not in current)
                        char.text = ", ".join(current)
        changes.append((unit.get("name", "Unknown unit"), promoted))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changes


def convert(input_path, output_path):
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output must differ from the input (original must remain intact)")
    raw = input_path.read_bytes()
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        raise ValueError("Input must be a .rosz ZIP archive")
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        roster_files = [name for name in source.namelist()
                        if name.lower().endswith(".ros") and not name.endswith("/")]
        if len(roster_files) != 1:
            raise ValueError("Expected exactly one .ros roster in the archive")
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    prepared = []
    changes = []
    for info, data in members:
        if info.filename == roster_files[0]:
            data, changes = adapt(data)
        prepared.append((info, data))
    # Construct and validate before writing the destination.
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for info, data in prepared:
            archive.writestr(info, data)
    with zipfile.ZipFile(io.BytesIO(output.getvalue())) as archive:
        ET.fromstring(archive.read(roster_files[0]))
        if archive.testzip() is not None:
            raise ValueError("Converted archive failed ZIP integrity check")
    output_path.write_bytes(output.getvalue())
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.input.with_name(args.input.stem + "-yellowscribe.rosz")
    changes = convert(args.input, output)
    print(f"Created: {output}")
    for unit, names in changes:
        print(f"{unit}: {', '.join(names)}")
    if not changes:
        print("No new non-weapon rules to promote; input roster preserved.")


if __name__ == "__main__":
    main()
