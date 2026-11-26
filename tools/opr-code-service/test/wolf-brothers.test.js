import test from 'node:test';
import assert from 'node:assert/strict';
import { zipSync, strToU8 } from 'fflate';
import { convertRosz } from '../src/roster.js';

// Synthetic selected-roster fixtures based on Wolf Brothers v3.6.0.
// These exercise nested squad loadouts, not the actual New Recruit exporter.
const sel = (name, type, contents='', quantity=1) =>
  '<selection name="'+name+'" type="'+type+'" number="'+quantity+'">'+contents+'</selection>';
const list = (...items) => '<selections>'+items.join('')+'</selections>';
const profile = (name,type,stats) => '<profiles><profile name="'+name+'" typeName="'+type+'"><characteristics>'+
  Object.entries(stats).map(([k,v])=>'<characteristic name="'+k+'">'+v+'</characteristic>').join('')+
  '</characteristics></profile></profiles>';
const weapon = (name,type,range,attacks,rules) => sel(name,'upgrade',profile(name,type,{'Range':range,'Attacks':attacks,'Special Rules':rules}));
const melee=(name,attacks,rules)=>weapon(name,'Melee Weapon','-',attacks,rules);
const ranged=(name,range,attacks,rules)=>weapon(name,'Ranged Weapon',range,attacks,rules);
const unit=(name,rules,...gear)=>sel(name,'unit',profile(name,'Unit',{'Quality':'3+','Defense':'4+','Special Rules':rules})+list(...gear));
const model=(name,...gear)=>sel(name,'model',list(...gear));
const convert=(...units)=>convertRosz(zipSync({'Wolf.ros':strToU8('<roster xmlns="http://www.battlescribe.net/schema/rosterSchema" name="Wolf smoke test"><forces><force>'+list(...units)+'</force></forces></roster>')}));
const wolfRules='Fast, Fearless, Tough(3), Wolfborn';
const backpack=()=>ranged('Backpack-GL','9&quot;','A1','AP(1), Assault');
const claws=()=>melee('Energy Were-Claws','A3','Rending');
const hammer=()=>melee('Energy Hammer','A1','AP(1), Blast(3)');
const squad=(name,...models)=>sel(name,'upgrade',list(...models));
test('Wolf Brothers nested squad replacement preserves all three separate models and selected gear',()=>{
  const baseline=unit('Werewolf Brothers',wolfRules,squad('Energy Were-Claws',...Array.from({length:3},(_,i)=>model('Werewolf Brothers — Model '+(i+1),claws()))));
  const upgraded=unit('Werewolf Brothers',wolfRules+', Armor(3), Regeneration',squad('Energy Hammers + Combat Shields + Backpack-GLs',...Array.from({length:3},(_,i)=>model('Werewolf Brothers — Model '+(i+1),hammer(),backpack()))));
  const [a,b]=convert(baseline,upgraded).units;
  assert.equal(a.modelDefinitions.length,3);
  assert.equal(b.modelDefinitions.length,3);
  for(const m of a.modelDefinitions){
    assert.equal(m.loadoutCSV,'Energy Were-Claws');
    assert.equal(m.originalToughValue,3);
    assert.doesNotMatch(m.ttsDescriptionOutput,/Armor\(3\)|Regeneration|Backpack-GL/);
  }
  for(const m of b.modelDefinitions){
    assert.equal(m.loadoutCSV,'Energy Hammer, Backpack-GL');
    assert.equal(m.originalToughValue,3);
    assert.match(m.ttsDescriptionOutput,/Armor\(3\)/);
    assert.match(m.ttsDescriptionOutput,/Regeneration/);
    assert.doesNotMatch(m.ttsDescriptionOutput,/Energy Were-Claws/);
  }
});
test('Wolf Battle Brothers nested specialist and sergeant upgrades stay on their own models',()=>{
  const rifle=()=>ranged('Heavy Rifle','18&quot;','A1','AP(1)');
  const strike=()=>melee('Strike','A1','-');
  const special=model('Wolf Battle Brothers — Model 1',ranged('Fusion Rifle','12&quot;','A1','AP(4), Deadly(3)'),strike());
  const sergeant=model('Wolf Battle Brothers — Model 2',squad('Sergeant loadout',ranged('Sgt. Arc-Charger Pistol','9&quot;','A1','Rending, Assault'),melee('Energy Sword','A1','Rending')));
  const rest=Array.from({length:3},(_,i)=>model('Wolf Battle Brothers — Model '+(i+3),rifle(),strike()));
  const result=convert(unit('Wolf Battle Brothers','Fearless, Wolfborn',special,sergeant,...rest)).units[0].modelDefinitions;
  assert.equal(result.length,5);
  assert.equal(result[0].loadoutCSV,'Fusion Rifle, Strike');
  assert.equal(result[1].loadoutCSV,'Sgt. Arc-Charger Pistol, Energy Sword');
  assert.equal(result.filter(m=>m.loadoutCSV==='Heavy Rifle, Strike').length,3);
  assert.ok(result.every(m=>m.originalToughValue===0));
});
test('Wolf Combat Walker keeps Tough(12) and only selected arm profiles',()=>{
  const stomp=melee('Stomp','A4','AP(1)');
  const fists=()=>melee('Walker Combat Fist','A4','AP(2)');
  const base='Fear(2), Fearless, Tough(12), Wolfborn';
  const a=unit('Wolf Combat Walker',base,model('Wolf Combat Walker — Model 1',stomp,squad('Two Walker Combat Fists',fists(),fists())));
  const b=unit('Wolf Combat Walker',base+', Fortified',model('Wolf Combat Walker — Model 1',stomp,squad('Walker Axe + Combat Shield',melee('Walker Axe','A6','Shred'))));
  const [x,y]=convert(a,b).units.map(u=>u.modelDefinitions[0]);
  assert.equal(x.originalToughValue,12);
  assert.equal(y.originalToughValue,12);
  assert.equal(x.loadoutCSV,'Stomp, Walker Combat Fist, Walker Combat Fist');
  assert.equal(y.loadoutCSV,'Stomp, Walker Axe');
  assert.match(y.ttsDescriptionOutput,/Fortified/);
  assert.doesNotMatch(y.ttsDescriptionOutput,/Walker Combat Fist/);
});
