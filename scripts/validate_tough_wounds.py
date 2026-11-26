#!/usr/bin/env python3
"""Check that parent unit profiles retain Tough(X), the source of wounds in New Recruit."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

NS = {"c": "http://www.battlescribe.net/schema/catalogueSchema"}

CASES = {
    "Robot_Legions.cat": {
        "Robot Lord": 3,
        "Tri-Scorpion Lord": 6,
        "Annihilator Lord": 6,
        "Bot Swarms": 3,
    }
}
for filename, expected in CASES.items():
    root = ET.parse(Path(filename)).getroot()
    for unit_name, tough in expected.items():
        units = [e for e in root.findall(".//c:selectionEntry", NS)
                 if e.get("type") == "unit" and e.get("name") == unit_name]
        assert len(units) == 1, f"{filename}: missing or duplicate {unit_name}"
        unit = units[0]
        profiles = unit.findall("./c:profiles/c:profile", NS)
        assert len(profiles) == 1, f"{unit_name}: missing/duplicate unit profile"
        rules = profiles[0].find("./c:characteristics/c:characteristic[@name='Special Rules']", NS)
        assert rules is not None, f"{unit_name}: missing Special Rules"
        match = re.search(r"\bTough\((\d+)\)", rules.text or "")
        assert match and int(match.group(1)) == tough, (
            f"{unit_name}: expected Tough({tough}) on unit profile, got {rules.text!r}"
        )
        links = unit.findall("./c:infoLinks/c:infoLink", NS)
        assert not any((link.get("name") or "").startswith("Tough") for link in links), (
            f"{unit_name}: redundant Tough rule link"
        )
        print(f"PASS {unit_name}: canonical Tough({tough}) retained, no redundant Tough rule link")
print("NOTE: Unit-profile presence is not proof of New Recruit's Force Organisation display.")
