#!/usr/bin/env python3
"""Compare visible Wolf Brothers weapon profiles; clipped source row is unverified."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT
data=json.loads((ROOT/"reference/wolf-brothers-weapon-profiles.json").read_text())
root=ET.parse(ROOT/"Wolf_Brothers.cat").getroot()
units={u.get("name"):u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type")=="unit"}
assert set(units)==set(data["units"])
unverified={(r["unit"],r["weapon"]) for r in data["unverified"]}
skipped=set()
def stat(p,n):
    return next((c.text or "" for c in p.findall(f"./{N}characteristics/{N}characteristic") if c.get("name")==n),"")
def sig(n,r,a,s):return (n,r,a,tuple(sorted(s)))
count=distinct=0
for n,u in units.items():
    profiles=[]
    for p in u.iter(N+"profile"):
        if p.get("typeName") not in ("Melee Weapon","Ranged Weapon"):continue
        key=(n,p.get("name"))
        if key in unverified:
            skipped.add(key)
            continue
        profiles.append(p)
    actual={sig(p.get("name"),stat(p,"Range"),stat(p,"Attacks"),[x.strip() for x in stat(p,"Special Rules").split(",") if x.strip()]) for p in profiles}
    expected={sig(w["name"],w["range"],w["attacks"],w["rules"]) for w in data["units"][n]}
    assert actual==expected,(n,actual-expected,expected-actual)
    count+=len(profiles)
    distinct+=len(expected)
assert skipped==unverified
print(f"PASS Wolf Brothers: {count} weapon profiles, {distinct} distinct source signatures; {len(skipped)} explicitly unverified weapon signatures.")
