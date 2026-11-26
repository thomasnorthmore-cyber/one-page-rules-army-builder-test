#!/usr/bin/env python3
"""Build a YellowScribe-oriented .rosz without changing New Recruit catalogues.

Usage: python scripts/prepare_yellowscribe_rosz.py army.rosz
Only selected, explicitly supported ability upgrades are promoted.
"""
import argparse
import copy
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ABILITY_UPGRADES = {"Re-Animator"}

def local(node):
    return node.tag.rsplit("}", 1)[-1]

def children(node, name):
    return [child for child in node if local(child) == name]

def adapt(raw):
    root = ET.fromstring(raw)
    ns = root.tag.split("}")[0][1:] if root.tag.startswith("{") else ""
    if ns:
        ET.register_namespace("", ns)
    changed = []
    for unit in root.iter():
        if local(unit) != "selection" or unit.get("type") != "unit":
            continue
        upgrades = []
        def selected_descendants(node):
            for group in children(node, "selections"):
                for selected in children(group, "selection"):
                    if selected.get("type") == "upgrade" and selected.get("name") in ABILITY_UPGRADES:
                        upgrades.append(selected)
                    selected_descendants(selected)
        selected_descendants(unit)
        if not upgrades:
            continue
        rules = next(iter(children(unit, "rules")), None)
        if rules is None:
            rules = ET.Element(f"{{{ns}}}rules" if ns else "rules")
            unit.insert(0, rules)
        existing_ids = {x.get("id") for x in children(rules, "rule")}
        existing_names = {x.get("name") for x in children(rules, "rule")}
        new_names = []
        for upgrade in upgrades:
            for block in children(upgrade, "rules"):
                for rule in children(block, "rule"):
                    name = rule.get("name")
                    if name and name not in new_names:
                        new_names.append(name)
                    if rule.get("id") not in existing_ids and name not in existing_names:
                        rules.append(copy.deepcopy(rule))
                        existing_ids.add(rule.get("id"))
                        existing_names.add(name)
        for profiles in children(unit, "profiles"):
            for profile in children(profiles, "profile"):
                if profile.get("typeName") != "Unit":
                    continue
                for chars in children(profile, "characteristics"):
                    for char in children(chars, "characteristic"):
                        if char.get("name") == "Special Rules":
                            listed = [v.strip() for v in (char.text or "").split(",") if v.strip()]
                            listed.extend(name for name in new_names if name not in listed)
                            char.text = ", ".join(listed)
        changed.append((unit.get("name"), new_names))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    if not zipfile.is_zipfile(args.input):
        parser.error("Input must be a .rosz ZIP file")
    output = args.output or args.input.with_name(args.input.stem + "-yellowscribe.rosz")
    with zipfile.ZipFile(args.input) as source, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as dest:
        files = [name for name in source.namelist() if name.lower().endswith(".ros")]
        if len(files) != 1:
            parser.error("Expected exactly one .ros file in the archive")
        changes = []
        for member in source.infolist():
            data = source.read(member.filename)
            if member.filename == files[0]:
                data, changes = adapt(data)
            dest.writestr(member.filename, data)
    print(f"Created: {output}")
    for unit, rules in changes:
        print(f"{unit}: {', '.join(rules)}")
    if not changes:
        print("No supported selected upgrades found; roster preserved")

if __name__ == "__main__":
    main()
