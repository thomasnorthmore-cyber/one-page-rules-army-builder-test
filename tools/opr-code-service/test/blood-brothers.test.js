import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { zipSync, strToU8 } from 'fflate';
import { convertRosz } from '../src/roster.js';

// Synthetic selected-roster XML. Weapon stats come from the independently
// extracted Blood Brothers source fixture, not from the converter.
const source=JSON.parse(readFileSync(new URL('../../../reference/blood-brothers-weapon-profiles.json',import.meta.url),'utf8')).units;
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
const convert=(...units)=>convertRosz(zipSync({'Blood.ros':strToU8('<roster xmlns="http://www.battlescribe.net/schema/rosterSchema" name="Blood smoke test"><forces><force>'+selections(...units)+'</force></forces></roster>')}));
const definitions=u=>u.modelDefinitions;
const base='Bloodborn, Fearless';
const named=(u,i)=>u+' — Model '+i;
const loadouts=(models)=>models.map(m=>m.loadoutCSV);
test('Blood Death Brothers squad replacements preserve five individual models, regeneration and mobility',()=>{
  const n='Blood Death Brothers', w=name=>weapon(n,name);
  const original=unit(n,base+', Regeneration',gear('Heavy Rifles + Strikes',...Array.from({length:5},(_,i)=>model(named(n,i+1),w('Heavy Rifle'),w('Strike')))));
  const replacement=unit(n,base+', Regeneration, Ambush, Flying',gear('Heavy Pistols + Hand Weapons',model(named(n,1),w('Plasma Pistol'),w('Hand Weapon')),...Array.from({length:4},(_,i)=>model(named(n,i+2),w('Heavy Pistol'),w('Hand Weapon')))));
  const [a,b]=convert(original,replacement).units.map(definitions);
  assert.equal(a.length,5); assert.equal(b.length,5);
  assert.deepEqual(loadouts(a),Array(5).fill('Heavy Rifle, Strike'));
  assert.deepEqual(loadouts(b),['Plasma Pistol, Hand Weapon',...Array(4).fill('Heavy Pistol, Hand Weapon')]);
  for(const m of a){assert.match(m.ttsDescriptionOutput,/Regeneration/);assert.doesNotMatch(m.ttsDescriptionOutput,/Ambush|Flying/);}
  for(const m of b){assert.match(m.ttsDescriptionOutput,/Regeneration/);assert.match(m.ttsDescriptionOutput,/Ambush/);assert.match(m.ttsDescriptionOutput,/Flying/);assert.doesNotMatch(m.ttsDescriptionOutput,/Heavy Rifle|Strike/);}
});
test('Blood Guard Brothers one Burst Fusion Pistol and individual lance replacements stay on their own models',()=>{
  const n='Blood Guard Brothers',w=name=>weapon(n,name);
  const u=unit(n,base+', Flying, Ambush',model(named(n,1),w('Burst Fusion Pistol'),w('Energy Sword')),model(named(n,2),w('Plasma Pistol'),w('Energy Lance')),...Array.from({length:3},(_,i)=>model(named(n,i+3),w('Heavy Pistol'),w('Energy Lance'))));
  const ms=definitions(convert(u).units[0]);
  assert.equal(ms.length,5);
  assert.deepEqual(loadouts(ms),['Burst Fusion Pistol, Energy Sword','Plasma Pistol, Energy Lance',...Array(3).fill('Heavy Pistol, Energy Lance')]);
  assert.match(ms[0].ttsDescriptionOutput,/AP\(4\), Deadly\(3\), Assault/);
  for(const m of ms.slice(1))assert.doesNotMatch(m.ttsDescriptionOutput,/Burst Fusion Pistol/);
});
test('Blood Veteran Assault Brothers shield replacement removes Armor(2) without removing flight',()=>{
  const n='Blood Veteran Assault Brothers',w=name=>weapon(n,name);
  const shield=unit(n,base+', Versatile Expert, Armor(2), Flying',gear('Hand Weapons + Combat Shields',...Array.from({length:3},(_,i)=>model(named(n,i+1),w('Hand Weapon'),selection('Combat Shield','upgrade',rules('Armor(2)'))))));
  const claws=unit(n,base+', Versatile Expert, Ambush, Flying',gear('Dual Energy Claws',...Array.from({length:3},(_,i)=>model(named(n,i+1),w('Dual Energy Claws')))));
  const [a,b]=convert(shield,claws).units.map(definitions);
  assert.equal(a.length,3);assert.equal(b.length,3);
  for(const m of a){assert.equal(m.loadoutCSV,'Hand Weapon');assert.equal(m.ttsDescriptionOutput.match(/Armor\(2\)/g)?.length,1);assert.match(m.ttsDescriptionOutput,/Flying/);}
  for(const m of b){assert.equal(m.loadoutCSV,'Dual Energy Claws');assert.match(m.ttsDescriptionOutput,/Flying/);assert.match(m.ttsDescriptionOutput,/Ambush/);assert.doesNotMatch(m.ttsDescriptionOutput,/Armor\(2\)|Hand Weapon/);}
});
test('Blood Veteran Battle Brothers rifle attachments only appear on the selected rifle model',()=>{
  const n='Blood Veteran Battle Brothers',w=name=>weapon(n,name);
  const u=unit(n,base+', Versatile Expert',model(named(n,1),gear('Burst Battle Rifle',w('Burst Battle Rifle'),w('Flamer-Mod'),w('Fusion-Mod')),w('Strike')),model(named(n,2),w('Plasma Rifle'),w('Strike')),model(named(n,3),w('Flamer'),w('Strike')));
  const ms=definitions(convert(u).units[0]);
  assert.deepEqual(loadouts(ms),['Burst Battle Rifle, Flamer-Mod, Fusion-Mod, Strike','Plasma Rifle, Strike','Flamer, Strike']);
  assert.match(ms[0].ttsDescriptionOutput,/AP\(4\), Deadly\(3\), Limited/);
  for(const m of ms.slice(1))assert.doesNotMatch(m.ttsDescriptionOutput,/Flamer-Mod|Fusion-Mod|Burst Battle Rifle/);
});
test('Blood Combat Walker pilot changes retain Tough(12) and selected arms',()=>{
  const n='Blood Combat Walker',w=name=>weapon(n,name),r=base+', Fear(2), Tough(12)';
  const a=unit(n,r,model(named(n,1),w('Stomp'),w('Walker Combat Fist'),w('Walker Combat Fist')));
  const b=unit(n,r+', Regeneration',model(named(n,1),w('Stomp'),w('Walker Claw'),gear('Fusion Rifle + Light Walker Fist',w('Fusion Rifle'),w('Light Walker Fist')),selection('Death Pilot','upgrade',rules('Regeneration'))));
  const c=unit(n,r+', Caster(2)',model(named(n,1),w('Stomp'),w('Walker Combat Fist'),w('Walker Combat Fist'),selection('Archivist','upgrade',rules('Caster(2)'))));
  const [x,y,z]=convert(a,b,c).units.map(u=>definitions(u)[0]);
  for(const m of [x,y,z])assert.equal(m.originalToughValue,12);
  assert.equal(x.loadoutCSV,'Stomp, Walker Combat Fist, Walker Combat Fist');
  assert.equal(y.loadoutCSV,'Stomp, Walker Claw, Fusion Rifle, Light Walker Fist');
  assert.equal(y.ttsDescriptionOutput.match(/Regeneration/g)?.length,1);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Walker Combat Fist|Caster\(2\)/);
  assert.doesNotMatch(x.ttsDescriptionOutput,/Regeneration|Caster\(2\)/);
  assert.match(z.ttsDescriptionOutput,/Caster\(2\)/);
  assert.doesNotMatch(z.ttsDescriptionOutput,/Regeneration/);
});
test('Blood Attack Vehicle cargo, dozer and armor rules reflect exact selected options',()=>{
  const n='Blood Attack Vehicle',w=name=>weapon(n,name),r=base+', Fast, Tough(6)';
  const a=unit(n,r,model(named(n,1),w('Heavy Flamer'),w('Overrun')));
  const b=unit(n,r+', Transport(6), Strider, Armor(2)',model(named(n,1),w('Heavy Flamer'),w('Overrun'),selection('Cargo Space','upgrade',rules('Transport(6)')),selection('Dozer Blade','upgrade',rules('Strider')),selection('Extra Armor','upgrade',rules('Armor(2)'))));
  const [x,y]=convert(a,b).units.map(u=>definitions(u)[0]);
  assert.equal(x.originalToughValue,6);assert.equal(y.originalToughValue,6);
  assert.doesNotMatch(x.ttsDescriptionOutput,/Transport\(|Strider|Armor\(2\)/);
  for(const value of ['Transport(6)','Strider','Armor(2)'])assert.equal(y.ttsDescriptionOutput.split(value).length,2,value);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Transport\(X\)/);
});
