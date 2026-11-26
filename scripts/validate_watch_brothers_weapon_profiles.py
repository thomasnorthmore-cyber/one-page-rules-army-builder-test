#!/usr/bin/env python3
"""Compare every weapon profile against the unit's independently transcribed PDF signatures."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT
data=json.loads((ROOT/"reference/watch-brothers-weapon-profiles.json").read_text())
root=ET.parse(ROOT/"Watch_Brothers.cat").getroot()
units={u.get("name"):u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type")=="unit"}
assert set(units)==set(data["units"])
def stat(p,n):
    return next((c.text or "" for c in p.findall(f"./{N}characteristics/{N}characteristic") if c.get("name")==n),"")
def sig(n,r,a,s):return (n,r,a,tuple(sorted(s)))
count=distinct=0
for n,u in units.items():
    profiles=[p for p in u.iter(N+"profile") if p.get("typeName") in ("Melee Weapon","Ranged Weapon")]
    actual={sig(p.get("name"),stat(p,"Range"),stat(p,"Attacks"),[x.strip() for x in stat(p,"Special Rules").split(",") if x.strip()]) for p in profiles}
    expected={sig(w["name"],w["range"],w["attacks"],w["rules"]) for w in data["units"][n]}
    assert actual==expected,(n,actual-expected,expected-actual)
    count+=len(profiles)
    distinct+=len(expected)
print(f"PASS Watch Brothers: {count} weapon profiles, {distinct} distinct unit-specific source signatures.")
