#!/usr/bin/env python3
"""Check BattleScribe catalogue integrity before testing in New Recruit."""
import sys, xml.etree.ElementTree as ET
from collections import Counter

NS = "{http://www.battlescribe.net/schema/catalogueSchema}"
GT = "{http://www.battlescribe.net/schema/gameSystemSchema}"
root = ET.parse("Battle_Brothers.cat").getroot()
game = ET.parse("Grimdark_Future.gst").getroot()
catalogue_id = root.attrib["gameSystemId"]
if catalogue_id != game.attrib["id"]:
    raise AssertionError("Catalogue game system ID mismatch")
ids = [x.attrib["id"] for x in root.iter() if "id" in x.attrib]
dupes = [k for k,v in Counter(ids).items() if v>1]
if dupes: raise AssertionError("Duplicate IDs: "+", ".join(dupes[:10]))
rule_ids={x.attrib["id"] for x in root.findall(".//"+NS+"sharedRules/"+NS+"rule")}
rule_ids |= {x.attrib["id"] for x in game.findall(".//"+GT+"sharedRules/"+GT+"rule")}
cat_ids={x.attrib["id"] for x in game.findall(".//"+GT+"categoryEntries/"+GT+"categoryEntry")}
types={x.attrib["id"] for x in game.findall(".//"+GT+"profileTypes/"+GT+"profileType")}
for link in root.findall(".//"+NS+"infoLink"):
    if link.attrib.get("type")=="rule" and link.attrib.get("targetId") not in rule_ids:
        raise AssertionError("Unresolved rule link: "+str(link.attrib))
for link in root.findall(".//"+NS+"categoryLink"):
    if link.attrib.get("targetId") not in cat_ids:
        raise AssertionError("Unresolved category link: "+str(link.attrib))
for profile in root.findall(".//"+NS+"profile"):
    if profile.attrib.get("typeId") not in types:
        raise AssertionError("Unknown profile type: "+str(profile.attrib))
entries=root.findall(".//"+NS+"selectionEntries/"+NS+"selectionEntry")
units=[x for x in entries if x.attrib.get("type")=="unit"]
if len(units)!=27: raise AssertionError(f"Expected 27 units, got {len(units)}")
for unit in units:
    # Squad-wide alternatives may nest model entries beneath selectable loadout upgrades.
    models=[m for m in unit.findall(".//"+NS+"selectionEntry") if m.attrib.get("type")=="model"]
    if not models:
        raise AssertionError(f"{unit.attrib['name']} has no model entries, including its alternate loadouts")
    for m in models:
        if not any(m.find("./"+NS+tag) is not None for tag in ("selectionEntries","selectionEntryGroups","profiles")):
            raise AssertionError(f"{unit.attrib['name']} contains an unequipped model")
        if m.find("./"+NS+"constraints") is None:
            raise AssertionError(f"Missing model quantity constraints in {unit.attrib['name']}")
# Every required choice must have a valid, selectable default.
for group in root.findall(".//"+NS+"selectionEntryGroup"):
    constraints=group.find("./"+NS+"constraints")
    limits={c.attrib.get("type"):c.attrib.get("value") for c in constraints} if constraints is not None else {}
    required=limits.get("min")=="1"
    default=group.attrib.get("defaultSelectionEntryId")
    if required and not default:
        raise AssertionError(f"Required equipment group missing default: {group.attrib.get('name')}")
    if default:
        child_ids={x.attrib.get("id") for x in group.findall("./"+NS+"selectionEntries/"+NS+"selectionEntry")}
        if default not in child_ids:
            raise AssertionError(f"Default selection not in group {group.attrib.get('name')}: {default}")
print(f"VALID: {len(units)} units, {len(ids)} unique catalogue IDs, game system and rule/profile/category links resolved")
print("NOTE: This validates catalogue structure, not New Recruit or YellowScribe export compatibility.")
