#!/usr/bin/env python3
"""Independent source costs for selected Blood Brothers upgrade groups."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT
root=ET.parse(ROOT/"Blood_Brothers.cat").getroot()
data=json.loads((ROOT/"reference/blood-brothers-upgrade-checks.json").read_text())
units={u.get("name"):u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type")=="unit"}
n=0
for row in data["groups"]:
    groups=[g for g in units[row["unit"]].iter(N+"selectionEntryGroup") if g.get("name")==row["group"]]
    assert groups,(row["unit"],row["group"],"missing group")
    for g in groups:
        got={o.get("name"):int(o.find(f"./{N}costs/{N}cost").get("value")) for o in g.findall(f"./{N}selectionEntries/{N}selectionEntry")}
        assert got==row["costs"],(row["unit"],row["group"],got,row["costs"])
        n+=len(got)
print(f"PASS Blood Brothers: {n} optional equipment cost assertions across {len(data['groups'])} source group fixtures.")
