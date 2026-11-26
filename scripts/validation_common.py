"""Shared catalogue validation helpers; game-system definitions are not local copies."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
N = "{http://www.battlescribe.net/schema/catalogueSchema}"
G = "{http://www.battlescribe.net/schema/gameSystemSchema}"
SYSTEM = ET.parse(ROOT / "Grimdark_Future.gst").getroot()
CORE = {x.get("id"): x for x in SYSTEM.findall(f"./{G}sharedRules/{G}rule")}
SYSTEM_IDS = {x.get("id") for x in SYSTEM.iter() if x.get("id")}
def rule_definitions(root):
    return {**CORE, **{x.get("id"): x for x in root.findall(f"./{N}sharedRules/{N}rule")}}
def factions():
    for path in sorted(ROOT.glob("*.cat")):
        root = ET.parse(path).getroot()
        if root.findall(f"./{N}selectionEntries/{N}selectionEntry[@type='unit']"):
            yield path, root
def models(unit):
    return unit.findall(f".//{N}selectionEntry[@type='model']")
def active_profiles(entry):
    """Follow fixed children and the selected default of each required group."""
    yield from entry.findall(f"./{N}profiles/{N}profile")
    for item in entry.findall(f"./{N}selectionEntries/{N}selectionEntry"):
        limits = {c.get("type"): float(c.get("value","0")) for c in item.findall(f"./{N}constraints/{N}constraint")}
        if limits.get("min",0)>0:
            yield from active_profiles(item)
    for group in entry.findall(f"./{N}selectionEntryGroups/{N}selectionEntryGroup"):
        default = group.get("defaultSelectionEntryId")
        if default:
            for option in group.findall(f"./{N}selectionEntries/{N}selectionEntry"):
                if option.get("id")==default:
                    yield from active_profiles(option)
def norm(value):
    value=(value or "").strip()
    return re.sub(r"^(AP|Blast|Deadly|Fear|Caster|Impact|Tough|Transport|Ravage|Self-Destruct|Takedown Strike|Piercing Target|Retaliate|Deathstrike)\(\d+\)$",r"\1(X)",value)
