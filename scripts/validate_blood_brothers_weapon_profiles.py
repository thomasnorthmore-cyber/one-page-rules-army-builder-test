#!/usr/bin/env python3
"""Compare every Blood Brothers unit's weapon signatures to the PDF source fixture."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

data = json.loads((ROOT / "reference/blood-brothers-weapon-profiles.json").read_text())
root = ET.parse(ROOT / "Blood_Brothers.cat").getroot()
units = {u.get("name"): u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type") == "unit"}
assert set(units) == set(data["units"]), "source unit coverage"
def stat(p, name):
    return next((c.text or "" for c in p.findall(f"./{N}characteristics/{N}characteristic") if c.get("name") == name), "")
def sig(name, rng, attacks, rules):
    return name, rng, attacks, tuple(sorted(rules))
count = distinct = 0
for name, unit in units.items():
    profiles = [p for p in unit.iter(N+"profile") if p.get("typeName") in ("Melee Weapon", "Ranged Weapon")]
    got = {sig(p.get("name"), stat(p,"Range"), stat(p,"Attacks"), [x.strip() for x in stat(p,"Special Rules").split(",") if x.strip()]) for p in profiles}
    want = {sig(w["name"],w["range"],w["attacks"],w["rules"]) for w in data["units"][name]}
    assert got == want, (name, "unexpected", got-want, "missing", want-got)
    count += len(profiles)
    distinct += len(want)
print(f"PASS Blood Brothers: {len(units)} units, {count} weapon profiles, {distinct} distinct source signatures.")
