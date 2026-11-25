import { unzipSync, strFromU8 } from 'fflate';
import { XMLParser } from 'fast-xml-parser';

const arr = x => x == null ? [] : Array.isArray(x) ? x : [x];
const val = x => x && typeof x === 'object' ? String(x['#text'] ?? '') : String(x ?? '');
const children = x => arr(x?.selections?.selection);
const descendants = x => children(x).flatMap(c => [c,...descendants(c)]);
const prof = (x,t) => arr(x?.profiles?.profile).filter(p => p.typeName === t);
const stat = (p,n) => val(arr(p?.characteristics?.characteristic).find(c=>c.name===n)).trim();

export function convertRosz(bytes){
  if(bytes.length > 1048576) throw Error('Maximum file size is 1 MB');
  const files = Object.entries(unzipSync(bytes,{filter:f=>f.name.toLowerCase().endsWith('.ros')}));
  if(files.length!==1)throw Error('The .rosz must contain one .ros roster');
  if(files[0][1].length>5000000)throw Error('Extracted roster too large');
  const xml = strFromU8(files[0][1]);
  if(/<!DOCTYPE|<!ENTITY/i.test(xml))throw Error('Unsupported XML');
  const roster = new XMLParser({ignoreAttributes:false,attributeNamePrefix:'',textNodeName:'#text',parseAttributeValue:false}).parse(xml)?.roster;
  if(!roster)throw Error('Invalid New Recruit roster');
  const units=[];
  for(const force of arr(roster.forces?.force))for(const unit of children(force)){
    if(unit.type!=='unit')continue;
    const up=prof(unit,'Unit')[0],qua=stat(up,'Quality'),def=stat(up,'Defense'),unitRules=stat(up,'Special Rules');
    const models=descendants(unit).filter(x=>x.type==='model');
    const definitions=[];
    for(const model of models.length?models:[unit]){
      const gear=[model,...descendants(model)].flatMap(x=>arr(x?.profiles?.profile)).filter(p=>['Ranged Weapon','Melee Weapon'].includes(p.typeName));
      const rules=new Map();
      for(const x of [unit,model,...descendants(model)])for(const rule of arr(x?.rules?.rule)){
        const name=String(rule.name||''),description=val(rule.description).replace(/\s+/g,' ').trim();
        if(name&&description)rules.set(name,description);
      }
      const details=['Quality: '+qua+' | Defense: '+def,'WEAPONS',...gear.map(p=>p.name+': '+[stat(p,'Range'),stat(p,'Attacks'),stat(p,'Special Rules')].filter(Boolean).join(' | ')),'RULES',...Array.from(rules,([n,d])=>n+': '+d)].join('\r\n');
      const quantity=Number(model.number??1);
      if(!Number.isInteger(quantity)||quantity<1||quantity>100)throw Error('Invalid model quantity');
      const tough=Number(unitRules.match(/Tough\((\d+)\)/i)?.[1]||0);
      for(let i=0;i<quantity;i++){
        const name=String(model.name||unit.name||'Model');
        definitions.push({name,loadoutCSV:gear.map(p=>p.name).join(', '),ttsNameOutput:name+'\r\nQuality '+qua+' / Defense '+def,ttsDescriptionOutput:details,originalToughValue:tough,originalCasterValue:0});
      }
    }
    units.push({name:String(unit.name||'Unit'),selectionId:String(unit.id||unit.entryId||'unit'),unitId:crypto.randomUUID(),modelDefinitions:definitions});
  }
  if(!units.length)throw Error('No units found');
  if(units.reduce((n,u)=>n+u.modelDefinitions.length,0)>500)throw Error('More than 500 models');
  return {gameSystem:'gf',rulesVersion:'3.6',listName:String(roster.name||'New Recruit list'),units};
}