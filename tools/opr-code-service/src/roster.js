import { unzipSync, strFromU8 } from 'fflate';
import { XMLParser } from 'fast-xml-parser';

const arr = x => x == null ? [] : Array.isArray(x) ? x : [x];
const val = x => x && typeof x === 'object' ? String(x['#text'] ?? '') : String(x ?? '');
const children = x => arr(x?.selections?.selection);
const descendants = x => children(x).flatMap(c => [c,...descendants(c)]);
const prof = (x,t) => arr(x?.profiles?.profile).filter(p => p.typeName === t);
const stat = (p,n) => val(arr(p?.characteristics?.characteristic).find(c=>c.name===n)).trim();

// Only explicit, unconditional weapon-rule grants are projected onto weapon profiles.
const grants = new Map([
  ['Rending in Melee',['Melee Weapon','Rending']],
  ['Shred in Melee',['Melee Weapon','Shred']],
  ['Unstoppable in Melee',['Melee Weapon','Unstoppable']],
  ['Shred when Shooting',['Ranged Weapon','Shred']],
  ['Anti-Cover when Shooting',['Ranged Weapon','Anti-Cover']],
  ['Counter in Melee Aura',['Melee Weapon','Counter']],
  ['Shred in Melee Aura',['Melee Weapon','Shred']],
  ['Unstoppable in Melee Aura',['Melee Weapon','Unstoppable']],
  ['Shred when Shooting Aura',['Ranged Weapon','Shred']],
  ['Bane in Melee Aura',['Melee Weapon','Bane']],
  ['Bane when Shooting Aura',['Ranged Weapon','Bane']],
  ['Anti-Cover when Shooting Aura',['Ranged Weapon','Anti-Cover']],
  ['Anti-Cover Aura',['Ranged Weapon','Anti-Cover']],
  ['Unstoppable when Shooting Aura',['Ranged Weapon','Unstoppable']],
]);
const splitRules = text => String(text||'').split(/,\s*(?![^()]*\))/).map(s=>s.trim()).filter(s=>s && s!=='-');
const namesOn = sel => [...arr(sel?.rules?.rule).map(r=>r.name), ...prof(sel,'Unit').flatMap(p=>splitRules(stat(p,'Special Rules')))].filter(Boolean);
const nonModelSelections = sel => children(sel).filter(c=>c.type!=='model' && c.type!=='unit').flatMap(c=>[c,...nonModelSelections(c)]);
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
    const commonRules=[unit,...nonModelSelections(unit)].flatMap(namesOn);
    const auraRules=models.flatMap(m=>[m,...nonModelSelections(m)].flatMap(namesOn)).filter(n=>n.endsWith(' Aura'));
    for(const model of models.length?models:[unit]){
      const gear=[model,...descendants(model)].flatMap(x=>arr(x?.profiles?.profile)).filter(p=>['Ranged Weapon','Melee Weapon'].includes(p.typeName));
      // Tabletop Simulator tooltip BB codes; short model name on normal hover.
      const green = text => '[A4FF61]'+text+'[-]';
      const red = text => '[FF6565][b]'+text+'[/b][-]';
      const yellow = text => '[FFE477][b]'+text+'[/b][-]';
      const purple = text => '[F48BDD][b]'+text+'[/b][-]';
      const pale = text => '[E8EDF2]'+text+'[-]';
      const baseName = String(model.name||unit.name||'Model');
      const unitSingular = String(unit.name||'Model').replace(/Brothers$/,'Brother').replace(/Snipers$/,'Sniper').replace(/Pathfinders$/,'Pathfinder').replace(/Bikers$/,'Biker').replace(/s$/,'');
      const name = /fixed equipment|standard models|four standard|three models/i.test(baseName)
        ? unitSingular
        : /specialist model/i.test(baseName)
          ? unitSingular+' Specialist'
          : baseName.replace(/\s*[—–-]\s*(fixed equipment|model \d+)$/i,'').trim();
      const descriptions=[];
      const activeGrants=new Set([...commonRules,...auraRules,...[model,...nonModelSelections(model)].flatMap(namesOn)].filter(n=>grants.has(n)));
      const effectiveRules=p=>[...new Set([...splitRules(stat(p,'Special Rules')),...[...activeGrants].map(n=>grants.get(n)).filter(([kind])=>kind===p.typeName).map(([,rule])=>rule)])].join(', ');
      descriptions.push(green('Quality '+qua+'   Defense '+def));
      const ranged=gear.filter(p=>p.typeName==='Ranged Weapon');
      const melee=gear.filter(p=>p.typeName==='Melee Weapon');
      const writeWeapon=(p)=>{
        const info=[stat(p,'Range'),stat(p,'Attacks'),effectiveRules(p)].filter(Boolean).join('  ');
        descriptions.push(yellow(String(p.name)));
        if(info)descriptions.push(pale(info));
      };
      if(ranged.length){descriptions.push('',red('Ranged weapons'));ranged.forEach(writeWeapon)}
      if(melee.length){descriptions.push('',red('Melee weapons'));melee.forEach(writeWeapon)}
      // List abilities by name only. Do not repeat long rule definitions or
      // weapon rules in the Abilities section.
      const abilityNames=new Set();
      for(const rule of String(unitRules||'').split(/,\s*(?![^()]*\))/).map(x=>x.trim()))if(rule)abilityNames.add(rule);
      for(const sel of [unit,model,...descendants(model)]){
        const selectionRules=arr(sel?.rules?.rule);
        for(const rule of selectionRules)if(rule.name && !/^AP\(X\)|Blast\(X\)|Deadly\(X\)$/i.test(String(rule.name)))abilityNames.add(String(rule.name));
      }
      // Rule links on weapon selection entries are not model-level abilities.
      const weaponNames=new Set(gear.flatMap(p=>splitRules(effectiveRules(p))));
      for(const w of weaponNames)abilityNames.delete(w);
      for(const n of activeGrants)if(!n.endsWith(' Aura') && gear.some(p=>p.typeName===grants.get(n)[0]))abilityNames.delete(n);
      if(abilityNames.size)descriptions.push('',purple('Abilities'),...Array.from(abilityNames,x=>pale(x)));
      const details=descriptions.join('\r\n');
      const quantity=Number(model.number??1);
      if(!Number.isInteger(quantity)||quantity<1||quantity>100)throw Error('Invalid model quantity');
      const tough=Number(unitRules.match(/Tough\((\d+)\)/i)?.[1]||0);
      for(let i=0;i<quantity;i++){
        definitions.push({name,loadoutCSV:gear.map(p=>p.name).join(', '),ttsNameOutput:name,ttsDescriptionOutput:details,originalToughValue:tough,originalCasterValue:0});
      }
    }
    units.push({name:String(unit.name||'Unit'),selectionId:String(unit.id||unit.entryId||'unit'),unitId:crypto.randomUUID(),modelDefinitions:definitions});
  }
  if(!units.length)throw Error('No units found');
  if(units.reduce((n,u)=>n+u.modelDefinitions.length,0)>500)throw Error('More than 500 models');
  return {gameSystem:'gf',rulesVersion:'3.6',listName:String(roster.name||'New Recruit list'),units};
}