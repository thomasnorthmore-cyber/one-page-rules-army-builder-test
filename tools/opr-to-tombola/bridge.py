#!/usr/bin/env python3
"""Independent New Recruit (.ros/.rosz) to Tombola TTS-compatible JSON bridge."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def kids(node, plural, singular):
    return [x for parent in node if parent.tag.rsplit('}',1)[-1] == plural
            for x in parent if x.tag.rsplit('}',1)[-1] == singular]

def parse_profile(p):
    return {'name':p.get('name',''), 'type':p.get('typeName',''),
            'stats':{c.get('name',''):(c.text or '').strip() for c in kids(p,'characteristics','characteristic')}}

def selection(s):
    return {'name':s.get('name',''), 'type':s.get('type',''), 'number':int(s.get('number','1')),
            'profiles':[parse_profile(p) for p in kids(s,'profiles','profile')],
            'rules':[{'name':r.get('name',''), 'description':' '.join(''.join(r.itertext()).split())}
                    for r in kids(s,'rules','rule')],
            'children':[selection(c) for c in kids(s,'selections','selection')]}

def walk(s):
    yield s
    for c in s['children']:yield from walk(c)

def read(path):
    if path.suffix.lower()=='.rosz':
        with zipfile.ZipFile(path) as f:
            matches=[i for i in f.infolist() if i.filename.lower().endswith(('.ros','.xml'))]
            if len(matches)!=1 or matches[0].file_size>15_000_000:
                raise ValueError('Expected one .ros in .rosz, under 15MB')
            data=f.read(matches[0])
    else:data=path.read_bytes()
    if len(data)>15_000_000 or b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('Invalid, too-large or DTD-containing roster')
    root=ET.fromstring(data)
    if root.tag.rsplit('}',1)[-1]!='roster':raise ValueError('Expected a roster XML document')
    return root

def model_priority(m):
    s=m['name'].lower()
    if 'fixed' in s or 'standard models' in s:return (0,0)
    if 'specialist' in s or 'fifth' in s or 'customisable' in s:return (2,0)
    match=re.search(r'\bmodel\s+(\d+)',s)
    return (1,int(match.group(1)) if match else 0)

def build(path):
    root=read(path)
    selected=[]
    for force in kids(root,'forces','force'):
        for s in kids(force,'selections','selection'):
            selected.extend(x for x in walk(selection(s)) if x['type']=='unit')
    if not selected:raise ValueError('No units found')
    units=[]
    for index,unit in enumerate(selected,1):
        stats={}
        for p in unit['profiles']:
            if p['type']=='Unit':stats=p['stats'];break
        models=sorted((x for x in walk(unit) if x['type']=='model'),key=model_priority)
        if not models:models=[unit]
        output=[]
        for model in models:
            for _ in range(model['number']):
                gear=[p for node in walk(model) for p in node['profiles']
                      if p['type'] in ('Ranged Weapon','Melee Weapon')]
                rules={r['name']:r['description'] for node in (unit,*walk(model))
                       for r in node['rules'] if r['name']}
                model_name=model['name']
                if 'four standard models' in model_name.lower() or 'fixed equipment' in model_name.lower():
                    model_name=unit['name']+' — standard model'
                count= len(output)+1
                model_name=re.sub(r'\bModel\s+\d+\b',f'Model {count}',model_name, flags=re.I)
                descriptions=[f"Quality {stats.get('Quality','?')} | Defense {stats.get('Defense','?')}",'WEAPONS']
                for item in gear:
                    values=item['stats'];details=[values.get('Range','Melee'), values.get('Attacks',''), values.get('Special Rules','')]
                    descriptions.append(item['name']+': '+', '.join(v for v in details if v))
                descriptions+=['RULES']+[name+': '+description for name,description in rules.items()]
                tough=re.search(r'Tough\((\d+)\)', stats.get('Special Rules',''))
                output.append({'name':model_name,'loadoutCSV':', '.join(p['name'] for p in gear),
                    'ttsNameOutput':model_name+'\r\nQuality '+stats.get('Quality','?')+' | Defense '+stats.get('Defense','?'),
                    'ttsDescriptionOutput':'\r\n'.join(descriptions),
                    'originalToughValue':int(tough.group(1)) if tough else 0,'originalCasterValue':0})
        units.append({'name':unit['name'],'unitId':f'newrecruit-unit-{index}',
            'selectionId':f'newrecruit-{index}','modelDefinitions':output})
    payload={'gameSystem':'gf','rulesVersion':'3.6','listName':root.get('name','OPR army'),'units':units}
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:12]
    return {'listId':'newrecruit-'+digest,'listJson':payload}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('roster',type=Path)
    p.add_argument('-o','--output',type=Path)
    args=p.parse_args()
    data=build(args.roster)
    path=args.output or args.roster.with_suffix('.tombola-response.json')
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
    print(f"Saved {path}: {len(data['listJson']['units'])} units")
    print('WARNING: This does not check mutually exclusive weapon upgrades.')
    print('WARNING: Tombola TTS loading requires a publicly reachable HTTPS JSON URL.')

if __name__=='__main__':main()
