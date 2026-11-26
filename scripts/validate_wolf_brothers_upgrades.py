#!/usr/bin/env python3
"""Verify Wolf Brothers visible PDF equipment prices; explicitly exclude clipped rows."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT
data=json.loads((ROOT/"reference/wolf-brothers-upgrade-checks.json").read_text())
root=ET.parse(ROOT/"Wolf_Brothers.cat").getroot()
units={u.get("name"):u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type")=="unit"}
fixtures={(r["unit"],r["group"]):r for r in data["groups"]}
unverified={(r["unit"],r["group"]) for r in data["unverified"]}
assert set(u for u,g in fixtures)==set(units)
def signature(d):return tuple(sorted(d.items()))
seen={}
skipped=set()
n=groups=0
for unit,u in units.items():
    for g in u.iter(N+"selectionEntryGroup"):
        key=(unit,g.get("name"))
        opts=g.findall(f"./{N}selectionEntries/{N}selectionEntry")
        got={o.get("name"):int(o.find(f"./{N}costs/{N}cost").get("value")) for o in opts}
        assert len(got)==len(opts),(key,"duplicate option name")
        if key in unverified:
            skipped.add(key)
            continue
        if key not in fixtures:
            assert len(got)==1 and list(got.values())==[0],(key,"uncovered nontrivial choice",got)
            continue
        row=fixtures[key]
        expected={signature(v) for v in [row["costs"],*row.get("variants",[])]}
        assert signature(got) in expected,(key,got,expected)
        seen.setdefault(key,set()).add(signature(got))
        n+=len(got)
        groups+=1
for key,row in fixtures.items():
    assert seen.get(key)=={signature(v) for v in [row["costs"],*row.get("variants",[])]},(key,"missing source variant")
assert skipped==unverified
print(f"PASS Wolf Brothers: {n} option costs in {groups} groups, {len(fixtures)} source fixtures; {len(skipped)} explicitly unverified clipped groups.")
