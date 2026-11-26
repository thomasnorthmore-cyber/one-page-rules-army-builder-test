#!/usr/bin/env python3
"""Validate required, points-free spell-reference entries for all Grimdark Future factions."""
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
import json
SPELL_SOURCE=json.loads((ROOT/"reference/spell-checks.json").read_text())
from validation_common import factions
SOURCE=json.loads((ROOT/"reference/source-checks.json").read_text())
for path,root in factions():
    file=path.name
    assert file in SPELL_SOURCE, file+": missing source spell fixture"
    units=[x for x in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if x.get("type")=="unit"]
    ref=root.find(f"./{N}selectionEntries/{N}selectionEntry[@name='Spell Catalogue']")
    assert ref is not None and ref.get("type")=="upgrade",file+": missing reference"
    assert list(root.find(N+"selectionEntries"))[0] is ref,file+": spell reference not first"
    assert ref.find(f"./{N}categoryLinks/{N}categoryLink").get("targetId")=="opr-spell-catalogue-category"
    constraints={x.get("type"):x for x in ref.findall(f"./{N}constraints/{N}constraint")}
    assert set(constraints)=={"min","max"},file+": expected one required reference per force"
    assert all(x.get("value")=="1" and x.get("scope")=="force" for x in constraints.values()),file+": spell reference must be required exactly once per force"
    assert not ref.findall(f".//{N}cost"),file+": spell reference must be free"
    assert not ref.findall(f".//{N}profile"),file+": spell reference must not add unit stats"
    assert not ref.findall(f".//{N}selectionEntry"),file+": spell reference must not add models"
    links=ref.findall(f"./{N}infoLinks/{N}infoLink")
    assert len(links)==6,file+": expected exactly 6 spells"
    expected=SPELL_SOURCE[file]
    assert len(links)==len(expected),file+": PDF spells count changed"

    defs={r.get("id"):r for r in root.findall(f"./{N}sharedRules/{N}rule")}
    for link,(name,cost,text_marker) in zip(links,expected):
        assert link.get("name")==f"{name} ({cost})",file+f": spell name/cost differs from supplied PDF: {name}"
        assert link.get("targetId") in defs,file+": missing spell definition"
        desc=defs[link.get("targetId")].findtext(N+"description") or ""
        assert text_marker in desc,file+f": spell effect differs from PDF: {name}"

        assert defs[link.get("targetId")].get("name")==link.get("name"),file+": spell name mismatch"
        assert defs[link.get("targetId")].findtext(N+"description"),file+": empty description"
    assert len(units)==len(SOURCE[file]["units"]),file+": source unit count mismatch"
    print(f"PASS {file}: first-category spell reference, 6 links, no points or models")
