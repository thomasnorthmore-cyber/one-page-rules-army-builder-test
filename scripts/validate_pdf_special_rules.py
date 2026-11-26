#!/usr/bin/env python3
"""Ensure every faction's PDF-listed special rule has a readable catalogue definition.

Source: reference/pdf-special-rule-checks.json, transcribed from the ARMY-WIDE
SPECIAL RULE, SPECIAL RULES and AURA SPECIAL RULES sections (PDF p.3).
Core rules absent from the faction PDF are checked by other validators.
"""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
N="{http://www.battlescribe.net/schema/catalogueSchema}"
G="{http://www.battlescribe.net/schema/gameSystemSchema}"
CORE={r.get("id"):r for r in ET.parse(ROOT/"Grimdark_Future.gst").getroot().findall(f"./{G}sharedRules/{G}rule")}
def description(r):
    return r.findtext(N+"description") or r.findtext(G+"description") or ""
DATA=json.loads((ROOT/"reference/pdf-special-rule-checks.json").read_text())
ERRORS=[]
def normalize(s):
    s=(s or "").replace("&amp;","&").strip()
    return re.sub(r"\((?:\d+|X)\)$","",s).strip()

from validation_common import factions
for path, root in factions():
    file=path.name
    if file not in DATA:
        ERRORS.append(f"{file}: missing PDF rule fixture")
        continue
    expected=DATA[file]
    defs={r.get("id"):r for r in root.findall(f"./{N}sharedRules/{N}rule")}
    defs.update(CORE)
    byname={}
    for definition in defs.values():
        byname.setdefault(normalize(definition.get("name")),[]).append(definition)
    for name in expected:
        candidates=byname.get(name,[])
        if not candidates:
            ERRORS.append(f"{file}: missing PDF special-rule definition: {name}")
            continue
        if not any(description(r).strip() for r in candidates):
            ERRORS.append(f"{file}: empty definition: {name}")
    for name,markers in DATA.get("_effect_markers",{}).get(file,{}).items():
        definitions=byname.get(name,[])
        if not definitions:continue
        descriptions=" ".join(description(r) for r in definitions)
        for marker in markers:
            if marker.lower() not in descriptions.lower():
                ERRORS.append(f"{file}: rule {name} missing PDF effect {marker!r}")
    allids={node.get("id") for node in root.iter() if node.get("id")}
    for link in root.iter(N+"infoLink"):
        if link.get("type")!="rule":continue
        target=link.get("targetId")
        if target not in defs:
            ERRORS.append(f"{file}: {link.get('name')} links to nonexistent rule {target}")
        elif not description(defs[target]).strip():
            ERRORS.append(f"{file}: {link.get('name')} links to blank definition")
    print(f"{file}: {len(expected)} PDF special/aura rules; {len(defs)} catalogue definitions; all source rules present: {all(x in byname for x in expected)}")
for message in ERRORS[:150]:print("FAIL:",message)
print(f"PDF rule coverage: {len(ERRORS)} errors")
sys.exit(bool(ERRORS))
