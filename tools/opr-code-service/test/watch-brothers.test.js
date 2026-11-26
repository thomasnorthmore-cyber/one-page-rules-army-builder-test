import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { zipSync, strToU8 } from 'fflate';
import { convertRosz } from '../src/roster.js';

// Synthetic selected-roster XML. Weapon stats come from the independently
// extracted Watch Brothers source fixture, not from the converter.
const source=JSON.parse(readFileSync(new URL('../../../reference/watch-brothers-weapon-profiles.json',import.meta.url),'utf8')).units;
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
const convert=(...units)=>convertRosz(zipSync({'Watch.ros':strToU8('<roster xmlns="http://www.battlescribe.net/schema/rosterSchema" name="Watch smoke test"><forces><force>'+selections(...units)+'</force></forces></roster>')}));
const definitions=u=>u.modelDefinitions;
const base='Watchborn, Fearless';
const named=(u,i)=>u+' — Model '+i;
const loadouts=(models)=>models.map(m=>m.loadoutCSV);
const spells=['Watch Dome (1)','Psychic Terror (1)','Watch Sight (2)','Lightning Fog (2)','Blessed Ammo (3)','Watch Trauma (3)'];
test('Watch Battle Brothers independent rifle attachments and melee replacements',()=>{
  const n='Watch Battle Brothers',w=name=>weapon(n,name);
  const u=unit(n,base+', Armor(2)',model(named(n,1),gear('Burst Heavy Rifle',w('Burst Heavy Rifle'),w('Fusion-Mod')),w('Strike')),model(named(n,2),gear('Heavy Machinegun',w('Heavy Machinegun'),w('Flamer-Mod')),w('Strike')),model(named(n,3),w('Plasma Pistol'),w('Energy Sword')));
  const ms=definitions(convert(u).units[0]);
  assert.equal(ms.length,3);
  assert.deepEqual(loadouts(ms),['Burst Heavy Rifle, Fusion-Mod, Strike','Heavy Machinegun, Flamer-Mod, Strike','Plasma Pistol, Energy Sword']);
  assert.match(ms[0].ttsDescriptionOutput,/AP\(4\), Deadly\(3\), Limited/);
  assert.match(ms[1].ttsDescriptionOutput,/Blast\(3\), Limited, Reliable/);
  assert.doesNotMatch(ms[0].ttsDescriptionOutput,/Flamer-Mod|Heavy Machinegun/);
  assert.doesNotMatch(ms[1].ttsDescriptionOutput,/Fusion-Mod|Burst Heavy Rifle/);
  assert.doesNotMatch(ms[2].ttsDescriptionOutput,/Flamer-Mod|Fusion-Mod|Strike/);
  for(const m of ms)assert.match(m.ttsDescriptionOutput,/Armor\(2\)/);
});
test('Watch Vanguard shield and Aerial Drop apply to all three models without losing Flying',()=>{
  const n='Watch Vanguard',w=name=>weapon(n,name),r=base+', Flying';
  const a=unit(n,r, ...Array.from({length:3},(_,i)=>model(named(n,i+1),w('Flamer Pistol'),w('Hand Weapon'))));
  const b=unit(n,r+', Armor(2), Ambush',model(named(n,1),w('Dual Energy Claws')),model(named(n,2),w('Great Energy Hammer')),model(named(n,3),w('Fusion Pistol'),w('Energy Fist')));
  const [x,y]=convert(a,b).units.map(definitions);
  assert.deepEqual(loadouts(x),Array(3).fill('Flamer Pistol, Hand Weapon'));
  assert.deepEqual(loadouts(y),['Dual Energy Claws','Great Energy Hammer','Fusion Pistol, Energy Fist']);
  for(const m of x){assert.match(m.ttsDescriptionOutput,/Flying/);assert.doesNotMatch(m.ttsDescriptionOutput,/Armor\(2\)|Ambush/);}
  for(const m of y){assert.match(m.ttsDescriptionOutput,/Flying/);assert.match(m.ttsDescriptionOutput,/Armor\(2\)/);assert.match(m.ttsDescriptionOutput,/Ambush/);assert.doesNotMatch(m.ttsDescriptionOutput,/Flamer Pistol|Hand Weapon/);}
});
test('Watch Destroyers switch squad shields to mixed burst rifles and missile rack',()=>{
  const n='Watch Destroyers',w=(name,a)=>weapon(n,name,a),r=base+', Tough(3)';
  const a=unit(n,r+', Armor(2)',gear('Hand Weapons + Combat Shields',...Array.from({length:3},(_,i)=>model(named(n,i+1),w('Hand Weapon','A3'),selection('Combat Shield','upgrade',rules('Armor(2)'))))));
  const b=unit(n,r+', Ambush',gear('Burst Cyclic Rifles + Hand Weapons',model(named(n,1),gear('Missile Rack + Burst Cyclic Rifle',w('Missile Rack'),w('Burst Cyclic Rifle')),w('Energy Sword')),model(named(n,2),w('Burst Cyclic Rifle'),w('Hand Weapon','A1')),model(named(n,3),w('Burst Cyclic Rifle'),w('Hand Weapon','A1'))));
  const [x,y]=convert(a,b).units.map(definitions);
  assert.deepEqual(loadouts(x),Array(3).fill('Hand Weapon'));
  assert.deepEqual(loadouts(y),['Missile Rack, Burst Cyclic Rifle, Energy Sword','Burst Cyclic Rifle, Hand Weapon','Burst Cyclic Rifle, Hand Weapon']);
  for(const m of [...x,...y])assert.equal(m.originalToughValue,3);
  for(const m of x)assert.equal(m.ttsDescriptionOutput.split('Armor(2)').length,2);
  for(const m of y){assert.match(m.ttsDescriptionOutput,/Ambush/);assert.doesNotMatch(m.ttsDescriptionOutput,/Armor\(2\)/);}
  for(const m of y.slice(1))assert.doesNotMatch(m.ttsDescriptionOutput,/Missile Rack/);
});
test('Watch Brother Bikers preserve both bike weapon and individual specialist or sergeant weapons',()=>{
  const n='Watch Brother Bikers',w=name=>weapon(n,name);
  const u=unit(n,base+', Fast, Tough(3)',gear('Assault Heavy Bike-Rifles + Heavy Rifles + Strikes',model(named(n,1),w('Assault Heavy Bike-Rifle'),w('Fusion Rifle'),w('Strike')),model(named(n,2),w('Assault Heavy Bike-Rifle'),gear('Sergeant loadout',w('Plasma Pistol'),w('Energy Sword'))),model(named(n,3),w('Assault Heavy Bike-Rifle'),w('Heavy Rifle'),w('Strike'))));
  const ms=definitions(convert(u).units[0]);
  assert.deepEqual(loadouts(ms),['Assault Heavy Bike-Rifle, Fusion Rifle, Strike','Assault Heavy Bike-Rifle, Plasma Pistol, Energy Sword','Assault Heavy Bike-Rifle, Heavy Rifle, Strike']);
  for(const m of ms){assert.equal(m.originalToughValue,3);assert.match(m.ttsDescriptionOutput,/Fast/);}
  assert.doesNotMatch(ms[1].ttsDescriptionOutput,/Fusion Rifle|Strike/);
  assert.doesNotMatch(ms[2].ttsDescriptionOutput,/Plasma Pistol|Energy Sword/);
});
test('Watch Master Brother selects caster or Enhanced Watchborn Aura without granting a fixed AP bonus',()=>{
  const n='Watch Master Brother',w=(name,a)=>weapon(n,name,a),r=base+', Hero';
  const a=unit(n,r+', Tough(3)',model(named(n,1),w('Flamer'),w('Hand Weapon','A1')));
  const b=unit(n,r+', Fast, Tough(6), Armor(2), Caster(3)',model(named(n,1),w('Burst Heavy Rifle'),w('Hand Weapon','A1'),w('Heavy Bike-Rifle'),selection('Combat Shield','upgrade',rules('Armor(2)')),selection('Master Archivist','upgrade',rules('Caster(3)',...spells))));
  const c=unit(n,r+', Tough(3), Enhanced Watchborn Aura',model(named(n,1),w('Flamer'),w('Hand Weapon','A1'),selection('Death-Munitions Keeper','upgrade',rules('Enhanced Watchborn Aura'))));
  const [x,y,z]=convert(a,b,c).units.map(u=>definitions(u)[0]);
  assert.deepEqual([x.originalCasterValue,y.originalCasterValue,z.originalCasterValue],[0,3,0]);
  assert.deepEqual([x.originalToughValue,y.originalToughValue,z.originalToughValue],[3,6,3]);
  for(const s of spells)assert.ok(y.ttsDescriptionOutput.includes(s));
  assert.match(y.ttsDescriptionOutput,/Armor\(2\)/);assert.doesNotMatch(y.ttsDescriptionOutput,/Enhanced Watchborn Aura/);
  assert.equal(z.ttsDescriptionOutput.split('Enhanced Watchborn Aura').length,2);
  assert.doesNotMatch(z.ttsDescriptionOutput,/AP\(|Caster\(|Armor\(2\)/);
  assert.doesNotMatch(x.ttsDescriptionOutput,/Caster\(|Enhanced Watchborn Aura|Armor\(2\)/);
});
test('Watch Attack Vehicle keeps Unstoppable Mark as an ability and exact transport capacity',()=>{
  const n='Watch Attack Vehicle',w=name=>weapon(n,name),r=base+', Fast, Tough(6)';
  const a=unit(n,r,model(named(n,1),w('Heavy Flamer'),w('Overrun')));
  const b=unit(n,r+', Transport(6), Strider, Armor(2), Unstoppable Mark',model(named(n,1),w('Heavy Flamer'),w('Overrun'),selection('Cargo Space','upgrade',rules('Transport(6)')),selection('Dozer Blade','upgrade',rules('Strider')),selection('Extra Armor','upgrade',rules('Armor(2)')),selection('Targeting Array','upgrade',rules('Unstoppable Mark'))));
  const [x,y]=convert(a,b).units.map(u=>definitions(u)[0]);
  assert.equal(y.originalToughValue,6);
  assert.doesNotMatch(x.ttsDescriptionOutput,/Transport\(|Strider|Armor\(2\)|Unstoppable Mark/);
  for(const rule of ['Transport(6)','Strider','Armor(2)','Unstoppable Mark'])assert.equal(y.ttsDescriptionOutput.split(rule).length,2,rule);
  assert.doesNotMatch(y.ttsDescriptionOutput.split('Abilities')[0],/Unstoppable/);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Transport\(X\)/);
});
test('Watch Deathstar Gunship Cluster Bombs are movement-triggered, not ordinary melee or ranged weapons',()=>{
  const n='Watch Deathstar Gunship',w=name=>weapon(n,name),r=base+', Aircraft, Tough(9)';
  const guns=()=>[w('Strafing Gatling Cannons'),w('Strafing Rocket Volley-Pod')];
  const a=unit(n,r,model(named(n,1),...guns(),w('Strafing Linked Heavy Rifle-Arrays')));
  const b=unit(n,r,model(named(n,1),...guns(),w('Cluster Bombs')));
  const c=unit(n,r+', Transport(11)',model(named(n,1),...guns(),selection('Cargo Space','upgrade',rules('Transport(11)'))));
  const [x,y,z]=convert(a,b,c).units.map(u=>definitions(u)[0]);
  for(const m of [x,y,z])assert.equal(m.originalToughValue,9);
  assert.match(x.ttsDescriptionOutput,/Strafing Linked Heavy Rifle-Arrays/);
  assert.equal(y.loadoutCSV,'Strafing Gatling Cannons, Strafing Rocket Volley-Pod, Cluster Bombs');
  assert.match(y.ttsDescriptionOutput,/Crossing Strike weapons[\s\S]*Cluster Bombs[\s\S]*A3  AP\(1\), Crossing Strike, Surge/);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Melee weapons|Strafing Linked Heavy Rifle-Arrays|Transport\(/);
  assert.equal(z.loadoutCSV,'Strafing Gatling Cannons, Strafing Rocket Volley-Pod');
  assert.match(z.ttsDescriptionOutput,/Transport\(11\)/);
  assert.doesNotMatch(z.ttsDescriptionOutput,/Cluster Bombs|Strafing Linked Heavy Rifle-Arrays/);
});
test('Crossing Strike uses shooting grants instead of melee grants even on a no-range legacy profile',()=>{
  // Synthetic isolated converter semantics test, not a legal Watch Brothers upgrade combination.
  const n='Watch Deathstar Gunship';
  const a=unit(n,base+', Aircraft, Tough(9)',model(named(n,1),weapon(n,'Cluster Bombs'),selection('Test shooting grant','upgrade',rules('Shred when Shooting')),selection('Test melee grant','upgrade',rules('Rending in Melee'))));
  const m=definitions(convert(a).units[0])[0];
  const weaponText=m.ttsDescriptionOutput.split('Abilities')[0];
  assert.match(weaponText,/AP\(1\), Crossing Strike, Surge, Shred/);
  assert.doesNotMatch(weaponText,/Rending/);
});
