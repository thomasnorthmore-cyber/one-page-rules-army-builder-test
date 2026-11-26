#!/usr/bin/env python3
"""Diagnose which selected rules a New Recruit .ros/.rosz export contains.

Usage: python scripts/inspect_rosz_rules.py my-army.rosz
This tool is read-only. It never changes a catalogue or a roster.
"""
import argparse
import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag):
    return tag.rsplit("}", 1)[-1]


def read_roster(path):
    raw = path.read_bytes()
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = [n for n in archive.namelist() if n.lower().endswith(".ros")]
            if len(entries) != 1:
                raise ValueError(f"Expected one .ros file in archive; found {len(entries)}")
            raw = archive.read(entries[0])
    return ET.fromstring(raw)


def walk_selections(node, lineage=()):
    for child in node:
        if local(child.tag) == "selection":
            chain = lineage + (child.get("name", ""),)
            yield child, chain
            yield from walk_selections(child, chain)
        else:
            yield from walk_selections(child, lineage)


def direct_rule_names(selection):
    out = set()
    for child in selection:
        if local(child.tag) == "rules":
            out.update(x.get("name", "") for x in child if local(x.tag) == "rule")
        if local(child.tag) == "profiles":
            for profile in child:
                if local(profile.tag) == "profile" and profile.get("typeName", "").lower() in {"ability", "abilities", "rule", "rules"}:
                    out.add(profile.get("name", ""))
    return out


def inspect(path, unit="Robot Lord", upgrade="Re-Animator"):
    root = read_roster(path)
    matches = []
    for selected, chain in walk_selections(root):
        if selected.get("name", "").strip().lower() != upgrade.lower():
            continue
        if not any(unit.lower() in part.lower() for part in chain[:-1]):
            continue
        names = direct_rule_names(selected)
        # Some roster writers emit a rule on the containing model or unit instead.
        ancestors = []
        for other, other_chain in walk_selections(root):
            if len(other_chain) < len(chain) and chain[:len(other_chain)] == other_chain:
                ancestors.append((other, other_chain))
        inherited = set().union(*(direct_rule_names(a) for a, _ in ancestors)) if ancestors else set()
        matches.append((chain, names, inherited))
    print(f"Roster: {path}")
    if not matches:
        print(f"FAIL: no selected {upgrade} under {unit}. Check the exact exported list.")
        return 1
    expected = {"Reanimation Aura", "Reanimation"}
    status = 0
    for chain, rules, ancestor_rules in matches:
        print("Selected:", " > ".join(chain))
        print("Upgrade-local rules:", ", ".join(sorted(rules)) or "(none)")
        print("Parent/model rules:", ", ".join(sorted(ancestor_rules)) or "(none)")
        missing = expected - rules - ancestor_rules
        if missing:
            status = 1
            print("MISSING FROM ROSTER RULE DATA:", ", ".join(sorted(missing)))
            print("Diagnosis: export omitted these as explicit roster rules, although the catalogue links them.")
        else:
            print("PASS: both rules are present in roster rule data.")
            print("Diagnosis: if absent in TTS, inspect YellowScribe's conversion/mapping.")
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("roster", type=Path)
    parser.add_argument("--unit", default="Robot Lord")
    parser.add_argument("--upgrade", default="Re-Animator")
    args = parser.parse_args()
    raise SystemExit(inspect(args.roster, args.unit, args.upgrade))
