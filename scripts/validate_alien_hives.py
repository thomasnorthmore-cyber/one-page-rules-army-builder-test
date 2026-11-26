#!/usr/bin/env python3
"""Alien Hives 3.6.0 catalogue baseline regression check (not PDF-completeness)."""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

N = "{http://www.battlescribe.net/schema/catalogueSchema}"
catalogue = ET.parse(Path(__file__).resolve().parents[1] / "Alien_Hives.cat").getroot()
assert catalogue.get("gameSystemId") == "b174-c09d-3660-f001"
assert "Completed" not in catalogue.get("name", ""), "Unverified army marked Completed"

ids = [x.get("id") for x in catalogue.iter() if x.get("id")]
counts = Counter(ids)
assert all(n == 1 for n in counts.values()), "Duplicate XML IDs"
known = set(ids)
for link in catalogue.iter(N + "infoLink"):
    assert link.get("targetId") in known, "Dangling rule target: " + str(link.get("targetId"))
for group in catalogue.iter(N + "selectionEntryGroup"):
    default = group.get("defaultSelectionEntryId")
    if default:
        assert default in known, "Dangling default selection: " + default
        choices = group.findall("./" + N + "selectionEntries/" + N + "selectionEntry")
        assert any(choice.get("id") == default for choice in choices), "Default outside group"
    limits = {c.get("type"): int(c.get("value")) for c in group.findall("./" + N + "constraints/" + N + "constraint")}
    if limits:
        assert limits.get("max", 0) >= limits.get("min", 0), "Broken group limits"
units = [e for e in catalogue.findall("./" + N + "selectionEntries/" + N + "selectionEntry") if e.get("type") == "unit"]
assert len(units) == 41, f"Expected 41 source units, got {len(units)}"
epic = {"Drekhor the Vengeful", "Ksi'adoz Smokeborn", "Troseis", "Vradhez", "Druzhak", "Nisuv"}
for unit in units:
    name = unit.get("name")
    profiles = unit.findall("./" + N + "profiles/" + N + "profile")
    assert len(profiles) == 1 and profiles[0].get("typeName") == "Unit", f"{name}: invalid unit profile"
    chars = {c.get("name"): c.text for c in profiles[0].findall("./" + N + "characteristics/" + N + "characteristic")}
    assert chars.get("Quality") and chars.get("Defense"), f"{name}: missing characteristics"
    assert chars.get("Special Rules"), f"{name}: missing innate rules"
    links = unit.findall("./" + N + "categoryLinks/" + N + "categoryLink")
    assert len(links) == 1, f"{name}: missing primary category"
    if name in epic:
        assert links[0].get("targetId") == "b174-c09d-3660-f048", f"{name}: not Epic Hero"
    models = unit.findall("./" + N + "selectionEntries/" + N + "selectionEntry")
    assert models, f"{name}: missing model entries"
    for model in models:
        weapons = model.findall("./" + N + "selectionEntries/" + N + "selectionEntry")
        groups = model.findall("./" + N + "selectionEntryGroups/" + N + "selectionEntryGroup")
        assert weapons or groups, f"{name}: unequipped model {model.get('name')}"
        if groups:
            # A replaced starting weapon may live under the group's default choice.
            for group in groups:
                if group.get("defaultSelectionEntryId"):
                    default = next(x for x in group.findall("./" + N + "selectionEntries/" + N + "selectionEntry") if x.get("id") == group.get("defaultSelectionEntryId"))
                    assert default.findall("./" + N + "profiles/" + N + "profile"), f"{name}: default loadout empty"
    if "Tough(" in chars["Special Rules"]:
        assert not any(x.get("name","").startswith("Tough(") for x in unit.findall("./" + N + "infoLinks/" + N + "infoLink")), f"{name}: redundant Tough rule link"

print(f"PASS Alien Hives: {len(units)} units, {sum(len(u.findall('./'+N+'selectionEntries/'+N+'selectionEntry')) for u in units)} models, {len(ids)} unique IDs.")
print("NOTE: Full PDF equipment parity and New Recruit visual tests are still required before marking Completed.")
