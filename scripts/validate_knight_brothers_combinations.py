#!/usr/bin/env python3
"""Enumerate reachable Knight Brothers unit-rule states from source PDF pp.4–8.
Static model of selection trees, not the New Recruit runtime."""
import json
from xml.etree import ElementTree as ET
from validation_common import N, ROOT

root = ET.parse(ROOT / "Knight_Brothers.cat").getroot()
defaults = json.loads((ROOT / "reference/knight-brothers-defaults.json").read_text())["units"]
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
        if item in ("Orbital Drop", "Striker", "Strikers"): r.add("Ambush")
        elif item in ("Jetpack", "Airdrop Jetpack"):
            r.add("Flying")
            if item == "Airdrop Jetpack": r.add("Ambush")
        elif item.startswith(("Combat Bike","Assault Bike")):
            r.discard("Tough(3)")
            r.update(("Fast","Tough(6)"))
        elif item in ("Inceptor","Inceptors","Teleport Engine"): r.add("Teleport")
        elif item == "Purifier": r.add("Ravage(3)")
        elif item == "Purifiers": r.add("Ravage(1)")
        elif item == "Paladin": r.add("Ravage(6)")
        elif item == "Paladins": r.add("Ravage(2)")
        elif item == "Power Shield": r.add("Stealth")
        elif item in ("Hand Weapon + Combat Shield","Combat Shield","Extra Armor"): r.add("Armor(2)")
        elif item == "Archivist": r.add("Caster(2)")
        elif item == "Master Archivist": r.add("Caster(3)")
        elif item == "Dozer Blade": r.add("Strider")
        elif item == "Cargo Space": r.add("Transport(6)" if name == "Knight Attack Vehicle" else "Transport(11)")
        else: raise AssertionError((name,item,"unknown source transition"))
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


assert affected == 11, affected
# Psychic is a one-model upgrade, not a common squad rule. Validate its exact
# model ownership and caster/spell links; no unit profile may grant Caster(1).
spell_names = {"Knight Dome (1)", "Doom Strike (1)", "Knight Sight (2)", "Purge the Impure (2)", "Banishing Sigil (3)", "Knight Trauma (3)"}
psychic_units = {"Knight Battle Brothers","Knight Veteran Brothers","Knight Purgation Brothers","Knight Destroyers"}
def walk(node, in_model=False):
    in_model = in_model or node.get("type")=="model"
    yield node, in_model
    for child in entries(node)+groups(node):
        yield from walk(child,in_model)
psychics = 0
seen = set()
for name,u in units.items():
    for node,in_model in walk(u):
        if node.tag != N+"selectionEntry" or node.get("name")!="Psychic": continue
        assert name in psychic_units and in_model, name
        assert {l.get("name") for l in node.findall(f"./{N}infoLinks/{N}infoLink")} == spell_names | {"Caster(1)"}, name
        psychics += 1
        seen.add(name)
    for p in u.findall(f"./{N}profiles/{N}profile"):
        assert all("Caster(1)" not in (c.text or "") for c in p.findall(f"./{N}characteristics/{N}characteristic")), name
        assert all("Caster(1)" not in m.get("value","") for m in p.findall(f"./{N}modifiers/{N}modifier")), name
assert seen==psychic_units and psychics==12
for name,capacity in [("Knight Attack Vehicle",6),("Knight Heavy Battle Tank",11),("Knight Heavy Gunship",11)]:
    matches=[e for e in units[name].iter(N+"selectionEntry") if e.get("name")=="Cargo Space"]
    assert len(matches)==1, name
    assert any(l.get("name")==f"Transport({capacity})" and l.get("type")=="rule" for l in matches[0].findall(f"./{N}infoLinks/{N}infoLink")), name
print(f"PASS Knight Brothers: {cases} reachable rule states, {modifier_count} modifiers, {affected} units, {psychics} model-owned Psychic entries; three exact transport capacities.")
