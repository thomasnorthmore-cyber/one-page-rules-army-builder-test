#!/usr/bin/env python3
"""Validate optional, points-free spell-reference entries for all four Grimdark Future factions."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
N="{http://www.battlescribe.net/schema/catalogueSchema}"
G="{http://www.battlescribe.net/schema/gameSystemSchema}"
SYSTEM=ET.parse(ROOT/"Grimdark_Future.gst").getroot()
cat=SYSTEM.find(f"./{G}categoryEntries/{G}categoryEntry[@id='opr-spell-catalogue-category']")
assert cat is not None and cat.get("name")=="Spell Catalogue"
force=SYSTEM.find(f"./{G}forceEntries/{G}forceEntry/{G}categoryLinks")
assert force is not None and force[0].get("targetId")=="opr-spell-catalogue-category", "Spell Catalogue must be first"
entries={"Alien_Hives.cat":"ah","Battle_Brothers.cat":"bb","Custodian_Brothers.cat":"cust","Robot_Legions.cat":"rl"}
for file,slug in entries.items():
    root=ET.parse(ROOT/file).getroot()
    units=[x for x in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if x.get("type")=="unit"]
    ref=root.find(f"./{N}selectionEntries/{N}selectionEntry[@id='opr-spellcat-{slug}-entry']")
    assert ref is not None and ref.get("type")=="upgrade",file+": missing reference"
    assert list(root.find(N+"selectionEntries"))[0] is ref,file+": spell reference not first"
    assert ref.find(f"./{N}categoryLinks/{N}categoryLink").get("targetId")=="opr-spell-catalogue-category"
    assert not ref.findall(f".//{N}cost"),file+": spell reference must be free"
    assert not ref.findall(f".//{N}profile"),file+": spell reference must not add unit stats"
    assert not ref.findall(f".//{N}selectionEntry"),file+": spell reference must not add models"
    links=ref.findall(f"./{N}infoLinks/{N}infoLink")
    assert len(links)==6,file+": expected exactly 6 spells"
    defs={r.get("id"):r for r in root.findall(f"./{N}sharedRules/{N}rule")}
    for link in links:
        assert link.get("targetId") in defs,file+": missing spell definition"
        assert defs[link.get("targetId")].get("name")==link.get("name"),file+": spell name mismatch"
        assert defs[link.get("targetId")].findtext(N+"description"),file+": empty description"
    assert len(units)=={"ah":41,"bb":27,"cust":22,"rl":32}[slug]
    print(f"PASS {file}: first-category spell reference, 6 links, no points or models")
