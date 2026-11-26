#!/usr/bin/env python3
"""Enumerate reachable unit-rule states from Blood Brothers PDF pp.5–14.
Static model of selection trees, not the New Recruit runtime."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Blood_Brothers.cat").getroot()
defaults = json.loads((ROOT / "reference/blood-brothers-defaults.json").read_text())["units"]
units = {u.get("name"): u for u in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if u.get("type") == "unit"}
def entries(n): return n.findall(f"./{N}selectionEntries/{N}selectionEntry")
def groups(n): return n.findall(f"./{N}selectionEntryGroups/{N}selectionEntryGroup")
def optional(n):
    return any(c.get("type") == "min" and float(c.get("value")) == 0 for c in n.findall(f"./{N}constraints/{N}constraint"))
def combine(a,b): return {x|y for x in a for y in b}
def variants(n, ids):
    if n.tag == N+"selectionEntryGroup":
        out = {frozenset()} if optional(n) else set()
        for e in entries(n): out |= variants(e, ids)
        return out
    out = {frozenset({n.get("id")} & ids)}
    for e in entries(n):
        v = variants(e, ids)
        if optional(e): v.add(frozenset())
        out = combine(out, v)
    for g in groups(n): out = combine(out, variants(g, ids))
    return out

def tokens(s): return {x.strip() for x in s.split(",") if x.strip()}
def expected(name, selected):
    r = set(defaults[name]["rules"])
    for item in selected:
        if item in ("Orbital Drop", "Aerial Drop"): r.add("Ambush")
        elif item in ("Jetpack", "Airdrop Jetpack", "Jetpacks"):
            r.add("Flying")
            if item != "Jetpack": r.add("Ambush")
        elif item in ("Camo Cloak", "Camo Cloaks"): r.add("Stealth")
        elif item in ("Forward Sentry", "Forward Sentries"): r.add("Scout")
        elif item == "Camo Sentry": r.update(("Scout","Stealth"))
        elif item == "Death Pilot": r.add("Regeneration")
        elif item.startswith(("Combat Bike", "Assault Bike", "Wolf Mount", "Off-Road Bike")):
            r.discard("Tough(3)")
            r.add("Tough(6)")
            r.add("Scout" if item.startswith("Off-Road Bike") else "Fast")
            if item.startswith("Wolf Mount"): r.add("Strider")
        elif item.endswith("Off-Road Tires"):
            r.discard("Fast"); r.update(("Scout","Strider"))
        elif item.endswith("High-Speed Tires"): pass
        elif item.startswith("Energy Hammers + Combat Shields"): r.add("Armor(3)")
        elif item in ("Hand Weapons + Combat Shields", "Hand Weapon + Combat Shield", "Combat Shield", "Extra Armor"): r.add("Armor(2)")
        elif item == "Archivist": r.add("Caster(2)")
        elif item == "Master Archivist": r.add("Caster(3)")
        elif item == "Dozer Blade": r.add("Strider")
        elif item in ("Cargo Space", "Open Sides"):
            r.add("Transport(6)" if name in ("Blood Attack Vehicle","Blood Attack Speeder") else "Transport(11)")
        elif item == "Walker Axe + Combat Shield": r.add("Fortified")
        else: raise AssertionError((name,item,"unknown source transition"))
    if name == "Blood Veteran Assault Brothers" and "Hand Weapons + Combat Shields" not in selected: r.discard("Armor(2)")
    return r

cases = modifier_count = affected = 0
for name,u in units.items():
    p = u.find(f"./{N}profiles/{N}profile")
    mods = [m for m in p.findall(f"./{N}modifiers/{N}modifier") if m.get("field") == "b174-c09d-3660-f013"]
    if not mods: continue
    affected += 1
    modifier_count += len(mods)
    conds = [m.findall(f"./{N}conditions/{N}condition") for m in mods]
    assert all(conds), name
    by_id = {e.get("id"):e.get("name") for e in u.iter(N+"selectionEntry")}
    ids = {c.get("childId") for cs in conds for c in cs}
    assert ids <= by_id.keys(), name
    for cs in conds:
        for c in cs:
            assert c.get("type") in ("greaterThan","equalTo") and float(c.get("value")) == 0, (name,c.attrib)
            assert c.get("scope") == u.get("id") and c.get("includeChildSelections") == "true", (name,c.attrib)
    base = next(c.text or "" for c in p.findall(f"./{N}characteristics/{N}characteristic") if c.get("name") == "Special Rules")
    hit = set()
    for state in variants(u,ids):
        matches = [i for i,cs in enumerate(conds) if all((c.get("childId") in state) == (c.get("type") == "greaterThan") for c in cs)]
        assert len(matches) <= 1, (name,state,"overlap")
        hit.update(matches)
        got = tokens(mods[matches[0]].get("value") if matches else base)
        want = expected(name,{by_id[i] for i in state})
        assert got == want, (name,state,got,want)
        cases += 1
    assert hit == set(range(len(mods))), (name,"unreachable modifier")


assert affected == 20, affected
for name, gear, capacity in [
    ("Blood Attack Vehicle","Cargo Space",6),
    ("Blood Attack Speeder","Open Sides",6),
    ("Blood Heavy Battle Tank","Cargo Space",11),
    ("Blood Heavy Gunship","Cargo Space",11),
]:
    matches = [e for e in units[name].iter(N+"selectionEntry") if e.get("name")==gear]
    assert len(matches)==1, (name,gear)
    assert any(l.get("name")==f"Transport({capacity})" and l.get("type")=="rule" for l in matches[0].findall(f"./{N}infoLinks/{N}infoLink")), (name,gear)
def walk(node, ancestors=()):
    yield node, ancestors
    for child in entries(node)+groups(node):
        yield from walk(child, ancestors+(node,))
attachments = 0
for name,unit in units.items():
    for node,parents in walk(unit):
        if node.tag!=N+"selectionEntryGroup" or not node.get("name","").endswith("-Mod"): continue
        assert any(p.tag==N+"selectionEntry" and p.get("type")=="model" for p in parents), (name,node.get("name"))
        assert any(p.tag==N+"selectionEntry" and "Burst" in p.get("name","") and "Rifle" in p.get("name","") for p in parents), (name,node.get("name"))
        attachments += 1
assert attachments >= 15
print(f"PASS Blood Brothers: {cases} reachable rule states, {modifier_count} modifiers, {affected} units, {attachments} rifle attachment groups; four transport capacities.")
