#!/usr/bin/env python3
"""Pure-stdlib regression tests for YellowScribe .rosz compatibility."""
import importlib.util
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

script = Path(__file__).with_name("prepare_yellowscribe_rosz.py")
spec = importlib.util.spec_from_file_location("prepare_yellowscribe_rosz", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

NS = "http://www.battlescribe.net/schema/rosterSchema"
N = "{" + NS + "}"


def rule(name):
    node = ET.Element(N + "rule", {"id": "r-" + name, "name": name})
    ET.SubElement(node, N + "description").text = "Test description"
    return node


def selected(name, type_="upgrade", rule_names=(), weapon_traits=()):
    item = ET.Element(N + "selection", {"name": name, "type": type_})
    if rule_names:
        rules = ET.SubElement(item, N + "rules")
        for rule_name in rule_names:
            rules.append(rule(rule_name))
    if weapon_traits:
        profiles = ET.SubElement(item, N + "profiles")
        profile = ET.SubElement(profiles, N + "profile", {"name": name, "typeName": "Ranged Weapon"})
        chars = ET.SubElement(profile, N + "characteristics")
        ET.SubElement(chars, N + "characteristic", {"name": "Special Rules"}).text = ", ".join(weapon_traits)
    return item


def make_roster(faction):
    root = ET.Element(N + "roster", {"name": faction})
    choices = ET.SubElement(root, N + "selections")
    unit = ET.SubElement(choices, N + "selection", {"name": faction + " test unit", "type": "unit"})
    profiles = ET.SubElement(unit, N + "profiles")
    profile = ET.SubElement(profiles, N + "profile", {"name": "Test", "typeName": "Unit"})
    chars = ET.SubElement(profile, N + "characteristics")
    ET.SubElement(chars, N + "characteristic", {"name": "Special Rules"}).text = "Hero, Tough(3)"
    model = selected("Model 1", "model")
    chosen = ET.SubElement(unit, N + "selections")
    chosen.append(model)
    equipped = ET.SubElement(model, N + "selections")
    equipped.append(selected("Selected aura", rule_names=("Reanimation Aura", "Reanimation")))
    equipped.append(selected("Shield", rule_names=("Armor(2+)",)))
    equipped.append(selected("Weapon", rule_names=("AP(X)", "Reliable"), weapon_traits=("AP(2)", "Reliable")))
    equipped.append(selected("Mixed weapon/ability", rule_names=("Shatter", "Flying"), weapon_traits=("Shatter",)))
    return ET.tostring(root, encoding="utf-8")


class ExportTests(unittest.TestCase):
    def test_all_three_factions(self):
        for faction in ("Battle Brothers", "Robot Legions", "Custodian Brothers"):
            with self.subTest(faction=faction):
                original = make_roster(faction)
                converted, changes = module.adapt(original)
                root = ET.fromstring(converted)
                unit = root.find(".//" + N + "selection[@type='unit']")
                values = [r.get("name") for r in unit.findall("./" + N + "rules/" + N + "rule")]
                self.assertEqual(values, ["Reanimation Aura", "Reanimation", "Armor(2+)", "Flying"])
                profile = unit.find("./" + N + "profiles/" + N + "profile/" + N + "characteristics/" + N + "characteristic")
                self.assertEqual(profile.text, "Hero, Tough(3), Reanimation Aura, Reanimation, Armor(2+), Flying")
                self.assertEqual(len(changes), 1)
                self.assertIsNone(ET.fromstring(original).find(".//" + N + "selection[@type='unit']/" + N + "rules"))
                again, repeated = module.adapt(converted)
                self.assertEqual(repeated, [])
                self.assertEqual(ET.tostring(ET.fromstring(again)), ET.tostring(ET.fromstring(converted)))

    def test_no_selected_ability_no_changes(self):
        original = ET.Element(N + "roster")
        unit = ET.SubElement(ET.SubElement(original, N + "selections"), N + "selection",
                             {"type": "unit", "name": "No Upgrade"})
        profile = ET.SubElement(ET.SubElement(unit, N + "profiles"), N + "profile",
                                {"typeName": "Unit"})
        ET.SubElement(ET.SubElement(profile, N + "characteristics"), N + "characteristic",
                      {"name": "Special Rules"}).text = "Tough(6)"
        adapted, changes = module.adapt(ET.tostring(original))
        self.assertEqual(changes, [])
        self.assertNotIn(b"Reanimation Aura", adapted)


if __name__ == "__main__":
    unittest.main()
