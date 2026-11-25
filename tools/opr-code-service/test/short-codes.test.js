import test from 'node:test';
import assert from 'node:assert/strict';
import { zipSync, strToU8 } from 'fflate';
import { convertRosz } from '../src/roster.js';
import worker from '../src/index.js';

const namespace='http://www.battlescribe.net/schema/rosterSchema';
function roster(){
  const equipment=(name,kind='Ranged Weapon')=>'<selection name="'+name+'" type="upgrade"><profiles><profile name="'+name+'" typeName="'+kind+'"><characteristics><characteristic name="Range">18&quot;</characteristic><characteristic name="Attacks">A1</characteristic><characteristic name="Special Rules">AP(1)</characteristic></characteristics></profile></profiles></selection>';
  const models='<selection name="Four Battle Brothers — fixed equipment" type="model" number="4"><selections>'+equipment('Heavy Rifle')+'</selections></selection>'+
    '<selection name="Fifth Battle Brother — customisable weapon" type="model" number="1"><selections>'+equipment('Sniper Rifle')+'</selections></selection>';
  const xml='<?xml version="1.0" encoding="utf-8"?><roster xmlns="'+namespace+'" name="Sample"><forces><force><selections><selection id="u1" name="Battle Brothers" type="unit"><profiles><profile typeName="Unit"><characteristics><characteristic name="Quality">3+</characteristic><characteristic name="Defense">3+</characteristic><characteristic name="Special Rules">Battleborn, Fearless</characteristic></characteristics></profile></profiles><selections>'+models+'</selections></selection></selections></force></forces></roster>';
  return zipSync({'Sample.ros':strToU8(xml)});
}
function mockEnv(){
  const map=new Map();
  return {ARMIES:{
    async put(k,v,options){assert.equal(options.expirationTtl,600);map.set(k,v)},
    async get(k){return map.get(k)??null}
  },ASSETS:{fetch:async()=>new Response('ok')}};
}
test('model quantities and specialist loadouts survive .rosz import',()=>{
  const x=convertRosz(roster());
  assert.equal(x.units.length,1);
  assert.equal(x.units[0].modelDefinitions.length,5);
  assert.equal(x.units[0].modelDefinitions.filter(m=>m.loadoutCSV==='Heavy Rifle').length,4);
  assert.equal(x.units[0].modelDefinitions.filter(m=>m.loadoutCSV==='Sniper Rifle').length,1);
  assert.ok(x.units[0].modelDefinitions[0].ttsDescriptionOutput.includes('[FFE477]'));
});
test('fresh code resolves and expired code is rejected',async()=>{
  const env=mockEnv();
  const upload=await worker.fetch(new Request('https://example.test/api/upload',{method:'POST',body:roster()}),env);
  assert.equal(upload.status,200);
  const result=await upload.json();
  assert.match(result.code,/^OPR-[A-HJ-NP-Z2-9]{9}$/);
  assert.equal(result.expiresInSeconds,600);
  const url='https://example.test/api/army?code='+result.code;
  const fetched=await worker.fetch(new Request(url),env);
  assert.equal(fetched.status,200);
  const data=await fetched.json();
  assert.equal(data.listJson.units[0].modelDefinitions.length,5);
  const stored=JSON.parse(await env.ARMIES.get(result.code));
  stored.expiresAt=Date.now()-1;
  await env.ARMIES.put(result.code,JSON.stringify(stored),{expirationTtl:600});
  const expired=await worker.fetch(new Request(url),env);
  assert.equal(expired.status,404);
});
test('every upload gets a different code',async()=>{
  const env=mockEnv();
  const post=()=>worker.fetch(new Request('https://example.test/api/upload',{method:'POST',body:roster()}),env);
  const a=await (await post()).json(),b=await (await post()).json();
  assert.notEqual(a.code,b.code);
});