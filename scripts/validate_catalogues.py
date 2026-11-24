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
    models=unit.findall("./"+NS+"selectionEntries/"+NS+"selectionEntry")
    if not models or not all(m.attrib.get("type")=="model" for m in models):
        raise AssertionError(f"{unit.attrib['name']} is missing model entries")
    for m in models:
        if not (m.find("./"+NS+"selectionEntries") is not None or m.find("./"+NS+"selectionEntryGroups") is not None or m.find("./"+NS+"profiles") is not None):
            raise AssertionError(f"{unit.attrib['name']} has an unequipped model")
        constraints=m.find("./"+NS+"constraints")
        if constraints is None: raise AssertionError(f"Missing model quantity constraints in {unit.attrib['name']}")
print(f"VALID: {len(units)} units, {len(ids)} unique catalogue IDs, game system and rule/profile/category links resolved")
print("NOTE: This validates catalogue structure, not New Recruit or YellowScribe export compatibility.")
