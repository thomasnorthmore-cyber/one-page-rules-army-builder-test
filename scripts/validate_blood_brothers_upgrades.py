#!/usr/bin/env python3
"""Source cost coverage for all nontrivial Blood Brothers equipment groups."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT
root=ET.parse(ROOT/"Blood_Brothers.cat").getroot()
data=json.loads((ROOT/"reference/blood-brothers-upgrade-checks.json").read_text())
units={u.get("name"):u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type")=="unit"}
fixtures={(r["unit"],r["group"]):r for r in data["groups"]}
assert set(u for u,g in fixtures)==set(units)
def signature(d):return tuple(sorted(d.items()))
seen={}
n=groups=0
for unit,u in units.items():
    for g in u.iter(N+"selectionEntryGroup"):
        key=(unit,g.get("name"))
        opts=g.findall(f"./{N}selectionEntries/{N}selectionEntry")
        got={o.get("name"):int(o.find(f"./{N}costs/{N}cost").get("value")) for o in opts}
        assert len(got)==len(opts),(key,"duplicate option name")
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
print(f"PASS Blood Brothers: {n} option costs in {groups} instantiated groups, {len(fixtures)} source group fixtures; no uncovered nontrivial choice groups.")
