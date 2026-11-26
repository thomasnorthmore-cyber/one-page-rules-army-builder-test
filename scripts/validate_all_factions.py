#!/usr/bin/env python3
"""Validate every faction catalogue, with explicit independent-source coverage."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

N="{http://www.battlescribe.net/schema/catalogueSchema}"
G="{http://www.battlescribe.net/schema/gameSystemSchema}"
PLACEHOLDER=re.compile(r"refer to|as defined|consult (?:the )?(?:rules|book)|follow OPR|use (?:the )?(?:official|grimdark future|alien hives).*rule|TODO|TBD|see (?:the )?rulebook",re.I)
PARAM=re.compile(r"^([^()]+)\((\d+)\)$")
def norm(s):
    s=(s or "").strip()
    m=PARAM.fullmatch(s)
    return m.group(1)+"(X)" if m and m.group(1) in {"AP","Blast","Deadly","Fear","Caster","Ravage","Transport","Self-Destruct","Takedown Strike","Piercing Target","Retaliate"} else s
def tokens(s):
    return [x.strip() for x in re.split(r",\s*(?![^()]*\))",s or "") if x.strip() not in {"","-","undefined"}]
def rules(e):
    return [x for x in e.findall(f"./{N}infoLinks/{N}infoLink") if x.get("type")=="rule"]
def stat(profile,key):
    if profile is None:return ""
    return next(((x.text or "").strip() for x in profile.findall(f"./{N}characteristics/{N}characteristic") if x.get("name")==key),"")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--output",type=Path,default=Path("validation-report.json"))
    ap.add_argument("--strict",action="store_true")
    a=ap.parse_args();base=a.root
    system=ET.parse(base/"Grimdark_Future.gst").getroot()
    systemids={x.get("id") for x in system.iter() if x.get("id")}
    manifest_path=base/"reference/source-checks.json"
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    glossary_path=base/"reference/shared-rules.json"
    glossary=json.loads(glossary_path.read_text()) if glossary_path.exists() else {}
    regression_path=base/"reference/regressions.json"
    regressions=json.loads(regression_path.read_text()).get("cases",{}) if regression_path.exists() else {}
    report={"factions":[],"totals":{},"note":"Structural validation is not a New Recruit/ForceOrg visual test. Unverified source coverage is not a pass."}
    totals=Counter()
    for path in sorted(base.glob("*.cat")):
        issues=[];counts=Counter()
        def add(level,code,unit,detail):
            issues.append({"severity":level,"code":code,"unit":unit,"detail":detail})
        try:root=ET.parse(path).getroot()
        except ET.ParseError as e:
            add("error","XML_PARSE",path.name,str(e))
            report["factions"].append({"file":path.name,"findings":issues});totals["error"]+=1
            continue
        units=[x for x in root.findall(f"./{N}selectionEntries/{N}selectionEntry") if x.get("type")=="unit"]
        if not units:continue
        counts["units"]=len(units)
        items=list(root.iter());ids=[x.get("id") for x in items if x.get("id")]
        counts["models"]=sum(x.tag==N+"selectionEntry" and x.get("type")=="model" for x in items)
        counts["weapon_profiles"]=sum(x.tag==N+"profile" and x.get("typeName") in {"Ranged Weapon","Melee Weapon"} for x in items)
        known=set(ids)|systemids
        if root.get("gameSystemId")!=system.get("id"):add("error","GAME_SYSTEM",path.name,"Wrong game system")
        for ident,n in Counter(ids).items():
            if n>1:add("error","DUPLICATE_ID",ident,str(n))
        for node in items:
            if node.tag in {N+"infoLink",N+"categoryLink"} and node.get("targetId") not in known:
                add("error","DANGLING_REFERENCE",node.get("name","?"),str(node.get("targetId")))
            if node.tag==N+"selectionEntryGroup":
                options={o.get("id") for o in node.findall(f"./{N}selectionEntries/{N}selectionEntry")}
                default=node.get("defaultSelectionEntryId")
                if default and default not in options:add("error","INVALID_DEFAULT",node.get("name","?"),default)
                limits={x.get("type"):int(float(x.get("value","0"))) for x in node.findall(f"./{N}constraints/{N}constraint")}
                if limits.get("min",0)>limits.get("max",999):add("error","GROUP_LIMITS",node.get("name","?"),str(limits))
                if limits.get("min",0)>=1 and not default:add("warning","NO_DEFAULT",node.get("name","?"),"Required choice without default")
            if node.tag==N+"rule":
                desc=node.findtext(N+"description") or ""
                if not desc.strip() or PLACEHOLDER.search(desc):
                    add("error","PLACEHOLDER_RULE",node.get("name","?"),desc[:130])
                key=(node.get("name") or "").split("(")[0]
                if key in glossary:
                    for phrase in glossary[key]["required_phrases"]:
                        if phrase.lower() not in desc.lower():
                            add("error","SHARED_RULE_SEMANTIC_DRIFT",node.get("name","?"),"Missing expected effect: "+phrase)
        for fixture in regressions.get(path.name, []):
            entry=next((x for x in items if x.tag==N+"selectionEntry" and x.get("id")==fixture["id"]),None)
            if entry is None:
                add("error","REGRESSION_MISSING_ENTRY",fixture["name"],fixture["id"])
            elif not any(x.get("name")==fixture["rule"] for x in rules(entry)):
                add("error","REGRESSION_RULE_MISSING",fixture["name"],fixture["rule"])
        for unit in units:
            uname=unit.get("name","?")
            profile=next((x for x in unit.findall(f"./{N}profiles/{N}profile") if x.get("typeName")=="Unit"),None)
            if profile is None:add("error","MISSING_UNIT_PROFILE",uname,"No unit profile");continue
            actual={k:stat(profile,k) for k in ("Quality","Defense","Special Rules")}
            native=tokens(actual["Special Rules"]);linked={norm(x.get("name")) for x in rules(unit)}
            for special in native:
                if not special.startswith("Tough(") and norm(special) not in linked and special.split("(")[0] not in linked:
                    add("error","MISSING_INNATE_LINK",uname,special)
            if not unit.findall(f".//{N}selectionEntry[@type='model']"):
                add("error","MISSING_MODELS",uname,"No model entries")
            expected=manifest.get(path.name,{}).get("units",{}).get(uname)
            if expected is None:add("error","SOURCE_BASELINE_MISSING",uname,"New unit has no independent PDF-verified source entry")
            else:
                for field in ("Quality","Defense","points"):
                    if field not in expected:
                        add("error","SOURCE_FIELD_MISSING",uname,f"Source baseline lacks {field}")
                counts["source_verified"]+=1
                for field in ("Quality","Defense"):
                    if field in expected and actual[field]!=expected[field]:
                        add("error","SOURCE_MISMATCH",uname,f"{field}: expected {expected[field]}, found {actual[field]}")
                for rule in expected.get("rules",[]):
                    if rule not in native:add("error","SOURCE_RULE_MISSING",uname,rule)
                if "points" in expected:
                    cost=unit.find(f"./{N}costs/{N}cost")
                    value=float(cost.get("value")) if cost is not None else None
                    if value!=float(expected["points"]):add("error","SOURCE_POINTS",uname,f"Expected {expected['points']}, found {value}")
        for entry in (x for x in items if x.tag==N+"selectionEntry"):
            label=entry.get("name","?")
            linked={norm(x.get("name")) for x in rules(entry)}
            if re.search(r"\bA\d+\b|\b(?:AP|Blast|Deadly)\(\d+\)",label):
                add("warning","UNCLEAN_EQUIPMENT_NAME",label,"Stats in selectable name")
            if any(x.get("name")=="Caster(X)" for x in rules(entry)):
                add("warning","GENERIC_CASTER_VALUE",label,"Use exact source-based Caster value")
            for weapon in entry.findall(f"./{N}profiles/{N}profile"):
                if weapon.get("typeName") not in {"Ranged Weapon","Melee Weapon"}:continue
                for special in tokens(stat(weapon,"Special Rules")):
                    if norm(special) not in linked:
                        add("error","WEAPON_RULE_MISSING",label,f"{weapon.get('name')}: {special}")
            if entry.get("type")=="upgrade":
                meaningful=bool(rules(entry) or entry.findall(f"./{N}profiles/{N}profile") or entry.findall(f"./{N}selectionEntries/{N}selectionEntry") or entry.findall(f"./{N}selectionEntryGroups/{N}selectionEntryGroup"))
                if not meaningful:add("warning","INERT_UPGRADE",label,"No rule, profile or child selection")
        counts["coverage_percent"]=round(100*counts["source_verified"]/max(1,len(units)),1)
        levels=Counter(x["severity"] for x in issues)
        totals.update(levels);totals["units"]+=len(units)
        totals["weapon_profiles"]+=counts["weapon_profiles"]
        report["factions"].append({"file":path.name,"revision":root.get("revision"),"counts":dict(counts),"findings":issues})
        print(f"{path.name} v{root.get('revision')}: {len(units)} units, {levels['error']} errors, {levels['warning']} warnings, {counts['coverage_percent']}% independently source-checked")
        for x in issues:
            if x["severity"]=="error":print(f"  ERROR [{x['code']}] {x['unit']}: {x['detail']}")
    known_path=base/"reference/known-issues.json"
    known_data=json.loads(known_path.read_text()) if known_path.exists() else {}
    known={(x["file"],x["code"],x["unit"]) for x in known_data.get("allow",[])}
    baseline_hits=set()
    introduced=[]
    for faction in report["factions"]:
        for issue in faction["findings"]:
            if issue["severity"]!="error":continue
            key=(faction["file"],issue["code"],issue["unit"])
            if key in known:
                issue["known_issue"]=True
                baseline_hits.add(key)
            else:
                introduced.append(key)
    unused=known-baseline_hits
    if unused:
        print("Resolved/stale known issue exceptions (remove from reference/known-issues.json):",sorted(unused))
    report["new_errors"]=len(introduced)
    report["known_errors"]=len(baseline_hits)
    report["totals"]=dict(totals)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(f"Report: {a.output}; {len(report['factions'])} factions; {totals['error']} confirmed structural errors; {totals['review']} awaiting source parity")
    print(f"Strict CI gate: {len(introduced)} unbaselined errors; {len(baseline_hits)} known unresolved errors.")
    return int(bool(a.strict and introduced))
if __name__=="__main__":sys.exit(main())
