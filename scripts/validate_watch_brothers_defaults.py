#!/usr/bin/env python3
"""Source-based Watch Brothers default-loadout test; does not certify optional combinations."""
import json
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

data=json.loads((ROOT/"reference/watch-brothers-defaults.json").read_text())
root=ET.parse(ROOT/"Watch_Brothers.cat").getroot()
units={u.get("name"):u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type")=="unit"}
assert set(units)==set(data["units"])
def selected(e):
    yield e
    for c in e.findall(f"./{N}selectionEntries/{N}selectionEntry"):
        if any(x.get("type")=="min" and float(x.get("value","0"))>0 for x in c.findall(f"./{N}constraints/{N}constraint")):
            yield from selected(c)
    for g in e.findall(f"./{N}selectionEntryGroups/{N}selectionEntryGroup"):
        d=g.get("defaultSelectionEntryId")
        if d:
            yield from selected(next(c for c in g.findall(f"./{N}selectionEntries/{N}selectionEntry") if c.get("id")==d))
def stat(p,name):
    return next((c.text or "" for c in p.findall(f"./{N}characteristics/{N}characteristic") if c.get("name")==name),"")
def tokens(s):return tuple(sorted(x.strip() for x in s.split(",") if x.strip()))
def weapon(p):
    return (p.get("name"),stat(p,"Range"),stat(p,"Attacks"),tokens(stat(p,"Special Rules")))
def effect(p,ids):
    base=stat(p,"Special Rules")
    matched=[]
    for m in p.findall(f"./{N}modifiers/{N}modifier"):
        if m.get("field")!="b174-c09d-3660-f013":continue
        cond=m.findall(f"./{N}conditions/{N}condition")
        assert cond, "Expected selection-dependent modifier"
        if all((c.get("childId") in ids)==(c.get("type")=="greaterThan") for c in cond):
            matched.append(m.get("value"))
    assert len(matched)<=1, "Overlapping unit-rule modifiers"
    return matched[0] if matched else base
total=0
for name,expected in data["units"].items():
    unit=units[name]
    act=list(selected(unit))
    models=[m for m in act if m.get("type")=="model"]
    assert len(models)==expected["models"], (name,"model count",len(models))
    unit_prof=unit.find(f"./{N}profiles/{N}profile")
    actual=set(tokens(effect(unit_prof,{x.get("id") for x in act})))
    assert actual==set(expected["rules"]), (name,"default unit rules",actual,set(expected["rules"]))
    want=Counter((w["name"],w["range"],w["attacks"],tuple(sorted(w["rules"]))) for w in expected["weapons"])
    for m in models:
        profiles=[p for e in selected(m) for p in e.findall(f"./{N}profiles/{N}profile") if p.get("typeName") in ("Melee Weapon","Ranged Weapon")]
        got=Counter(map(weapon,profiles))
        assert got==want,(name,m.get("name"),got,want)
        total+=1
print(f"PASS Watch Brothers: {len(units)} units, {total} default models; exact default weapon names, ranges, attacks, rules and multiplicities.")
