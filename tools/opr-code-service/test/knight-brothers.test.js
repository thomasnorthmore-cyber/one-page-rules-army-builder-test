import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { zipSync, strToU8 } from 'fflate';
import { convertRosz } from '../src/roster.js';

// Synthetic selected-roster XML. Weapon stats come from the independently
// extracted Knight Brothers source fixture, not from the converter.
const source=JSON.parse(readFileSync(new URL('../../../reference/knight-brothers-weapon-profiles.json',import.meta.url),'utf8')).units;
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const selection=(name,type,body='',number=1)=>'<selection name="'+esc(name)+'" type="'+type+'" number="'+number+'">'+body+'</selection>';
const selections=(...items)=>'<selections>'+items.join('')+'</selections>';
const profile=(name,type,stats)=>'<profiles><profile name="'+esc(name)+'" typeName="'+type+'"><characteristics>'+Object.entries(stats).map(([k,v])=>'<characteristic name="'+k+'">'+esc(v)+'</characteristic>').join('')+'</characteristics></profile></profiles>';
const weapon=(unit,name,attacks)=>{
  const candidates=source[unit].filter(w=>w.name===name&&(!attacks||w.attacks===attacks));
  assert.equal(candidates.length,1,unit+' '+name);
  const w=candidates[0];
  return selection(name,'upgrade',profile(name,w.range?'Ranged Weapon':'Melee Weapon',{'Range':w.range,'Attacks':w.attacks,'Special Rules':w.rules.join(', ')}));
};
const rules=(...names)=>'<rules>'+names.map(name=>'<rule name="'+esc(name)+'"/>').join('')+'</rules>';
const gear=(name,...items)=>selection(name,'upgrade',selections(...items));
const model=(name,...items)=>selection(name,'model',selections(...items));
const unit=(name,special,...items)=>selection(name,'unit',profile(name,'Unit',{'Quality':'3+','Defense':'3+','Special Rules':special})+selections(...items));
const convert=(...units)=>convertRosz(zipSync({'Knight.ros':strToU8('<roster xmlns="http://www.battlescribe.net/schema/rosterSchema" name="Knight smoke test"><forces><force>'+selections(...units)+'</force></forces></roster>')}));
const definitions=u=>u.modelDefinitions;
const base='Knightborn, Fearless';
const named=(u,i)=>u+' — Model '+i;
const loadouts=(models)=>models.map(m=>m.loadoutCSV);
const spells=['Knight Dome (1)','Doom Strike (1)','Knight Sight (2)','Purge the Impure (2)','Banishing Sigil (3)','Knight Trauma (3)'];
const psychic=()=>selection('Psychic','upgrade',rules('Caster(1)',...spells));
test('Knight Battle Brothers Psychic stays on one model with selected special weapons',()=>{
  const n='Knight Battle Brothers',w=name=>weapon(n,name);
  const u=unit(n,base+', Teleport',gear('Cyclic Rifles + Strikes',
    model(named(n,1),w('Slayer Chain-Cannon'),w('Strike')),
    model(named(n,2),w('Dual Energy Sabres')),
    model(named(n,3),w('Cyclic Rifle'),w('Strike'),psychic()),
    ...Array.from({length:2},(_,i)=>model(named(n,i+4),w('Cyclic Rifle'),w('Strike')))));
  const ms=definitions(convert(u).units[0]);
  assert.equal(ms.length,5);
  assert.deepEqual(loadouts(ms),['Slayer Chain-Cannon, Strike','Dual Energy Sabres',...Array(3).fill('Cyclic Rifle, Strike')]);
  assert.deepEqual(ms.map(m=>m.originalCasterValue),[0,0,1,0,0]);
  for(const [i,m] of ms.entries()){
    assert.match(m.ttsDescriptionOutput,/Teleport/);
    if(i===2){assert.match(m.ttsDescriptionOutput,/Caster\(1\)/);for(const s of spells)assert.ok(m.ttsDescriptionOutput.includes(s));}
    else{assert.doesNotMatch(m.ttsDescriptionOutput,/Caster\(1\)|Knight Dome|Doom Strike|Knight Trauma/);}
  }
});
test('Knight Veteran Brothers squad replacement preserves distinct gear and selected order',()=>{
  const n='Knight Veteran Brothers',w=name=>weapon(n,name),r=base+', Versatile Expert';
  const a=unit(n,r+', Ravage(1)',gear('Dual Energy Sabres',...Array.from({length:3},(_,i)=>model(named(n,i+1),w('Dual Energy Sabres')))));
  const b=unit(n,r+', Ambush',gear('Slayer Blaze-Flamers + Strikes',model(named(n,1),w('Slayer Fusion-Beamer'),w('Strike')),model(named(n,2),w('Slayer Volley-Gun'),w('Strike')),model(named(n,3),w('Slayer Blaze-Flamer'),w('Strike'))));
  const [x,y]=convert(a,b).units.map(definitions);
  assert.deepEqual(loadouts(x),Array(3).fill('Dual Energy Sabres'));
  assert.deepEqual(loadouts(y),['Slayer Fusion-Beamer, Strike','Slayer Volley-Gun, Strike','Slayer Blaze-Flamer, Strike']);
  for(const m of x){assert.match(m.ttsDescriptionOutput,/Ravage\(1\)/);assert.doesNotMatch(m.ttsDescriptionOutput,/Ambush/);}
  for(const m of y){assert.match(m.ttsDescriptionOutput,/Ambush/);assert.doesNotMatch(m.ttsDescriptionOutput,/Ravage\(1\)|Dual Energy Sabres/);}
});
test('Knight Destroyers selected heavy weapon, Paladins and Orbital Drop preserve three Tough(3) models',()=>{
  const n='Knight Destroyers',w=(name,a)=>weapon(n,name,a);
  const u=unit(n,base+', Tough(3), Ravage(2), Ambush',gear('Burst Cyclic Rifles + Hand Weapons',model(named(n,1),w('Slayer Chain-Cannon'),w('Energy Sword')),model(named(n,2),w('Burst Cyclic Rifle'),w('Hand Weapon','A1'),psychic()),model(named(n,3),w('Burst Cyclic Rifle'),w('Hand Weapon','A1'))));
  const ms=definitions(convert(u).units[0]);
  assert.deepEqual(loadouts(ms),['Slayer Chain-Cannon, Energy Sword','Burst Cyclic Rifle, Hand Weapon','Burst Cyclic Rifle, Hand Weapon']);
  assert.deepEqual(ms.map(m=>m.originalCasterValue),[0,1,0]);
  for(const m of ms){assert.equal(m.originalToughValue,3);assert.match(m.ttsDescriptionOutput,/Ravage\(2\)/);assert.match(m.ttsDescriptionOutput,/Ambush/);}
  for(const m of ms.slice(1))assert.doesNotMatch(m.ttsDescriptionOutput,/Slayer Chain-Cannon/);
});
test('Knight Nemesis Walker separate arms and conditional engine/shield preserve innate caster and wounds',()=>{
  const n='Knight Nemesis Walker',w=name=>weapon(n,name),r=base+', Ambush, Caster(2), Fear(3), Tough(18)';
  const a=unit(n,r,model(named(n,1),w('Heavy Walker Slayer Hammer'),w('Heavy Walker Slayer Hammer'),w('Stomp')));
  const b=unit(n,r+', Teleport, Stealth',model(named(n,1),gear('Assault Slayer Volley-Gun + Walker Sword',w('Assault Slayer Volley-Gun'),w('Walker Sword')),w('Heavy Walker Fist'),w('Stomp'),selection('Teleport Engine','upgrade',rules('Teleport')),selection('Power Shield','upgrade',rules('Stealth'))));
  const [x,y]=convert(a,b).units.map(u=>definitions(u)[0]);
  assert.equal(x.loadoutCSV,'Heavy Walker Slayer Hammer, Heavy Walker Slayer Hammer, Stomp');
  assert.equal(y.loadoutCSV,'Assault Slayer Volley-Gun, Walker Sword, Heavy Walker Fist, Stomp');
  for(const m of [x,y]){assert.equal(m.originalToughValue,18);assert.equal(m.originalCasterValue,2);assert.match(m.ttsDescriptionOutput,/Ambush/);}
  assert.doesNotMatch(x.ttsDescriptionOutput,/Teleport|Stealth/);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Heavy Walker Slayer Hammer|Walker Slayer Hammer/);
  for(const rule of ['Teleport','Stealth','Caster(2)'])assert.equal(y.ttsDescriptionOutput.split(rule).length,2,rule);
});
test('Knight Veteran Master Brother caster level and shield toggle without losing bike or order rules',()=>{
  const n='Knight Veteran Master Brother',w=(name,a)=>weapon(n,name,a),r=base+', Hero, Versatile Expert';
  const a=unit(n,r+', Tough(3)',model(named(n,1),w('Flamer Pistol'),w('Hand Weapon','A3')));
  const b=unit(n,r+', Tough(6), Fast, Teleport, Armor(2), Caster(3)',model(named(n,1),w('Hand Weapon','A3'),w('Heavy Bike-Rifle'),selection('Combat Shield','upgrade',rules('Armor(2)')),selection('Master Archivist','upgrade',rules('Caster(3)',...spells))));
  const [x,y]=convert(a,b).units.map(u=>definitions(u)[0]);
  assert.equal(x.originalToughValue,3);assert.equal(x.originalCasterValue,0);
  assert.equal(y.originalToughValue,6);assert.equal(y.originalCasterValue,3);
  assert.equal(y.loadoutCSV,'Hand Weapon, Heavy Bike-Rifle');
  for(const rule of ['Caster(3)','Armor(2)','Fast','Teleport'])assert.equal(y.ttsDescriptionOutput.split(rule).length,2,rule);
  assert.doesNotMatch(x.ttsDescriptionOutput,/Caster\(|Armor\(2\)|Teleport|Fast/);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Flamer Pistol|Tough\(3\)/);
});
test('Knight Attack Vehicle cargo and armor options use exact transport capacity',()=>{
  const n='Knight Attack Vehicle',w=name=>weapon(n,name),r=base+', Fast, Tough(6)';
  const a=unit(n,r,model(named(n,1),w('Heavy Flamer'),w('Overrun')));
  const b=unit(n,r+', Transport(6), Strider, Armor(2)',model(named(n,1),w('Heavy Flamer'),w('Overrun'),selection('Cargo Space','upgrade',rules('Transport(6)')),selection('Dozer Blade','upgrade',rules('Strider')),selection('Extra Armor','upgrade',rules('Armor(2)'))));
  const [x,y]=convert(a,b).units.map(u=>definitions(u)[0]);
  for(const m of [x,y]){assert.equal(m.originalToughValue,6);assert.equal(m.originalCasterValue,0);}
  assert.doesNotMatch(x.ttsDescriptionOutput,/Transport\(|Strider|Armor\(2\)/);
  for(const rule of ['Transport(6)','Strider','Armor(2)'])assert.equal(y.ttsDescriptionOutput.split(rule).length,2,rule);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Transport\(X\)/);
});
