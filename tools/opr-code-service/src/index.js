import { convertRosz } from './roster.js';

const TTL=600;
const alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const headers={'content-type':'application/json; charset=utf-8','cache-control':'no-store','access-control-allow-origin':'*'};
const respond=(x,status=200)=>new Response(JSON.stringify(x),{status,headers});
function newCode(){
  const chars=[];
  while(chars.length<9){
    for(const b of crypto.getRandomValues(new Uint8Array(12))){
      if(b>=224)continue;
      chars.push(alphabet[b%alphabet.length]);
      if(chars.length===9)break;
    }
  }
  return 'OPR-'+chars.join('');
}
export default {async fetch(request,env){
  const url=new URL(request.url);
  if(request.method==='GET'&&url.pathname==='/')return env.ASSETS.fetch(request);
  if(!env.ARMIES)return respond({error:'KV namespace ARMIES is not configured'},503);
  if(request.method==='POST'&&url.pathname==='/api/upload'){
    if(Number(request.headers.get('content-length')||0)>1048576)return respond({error:'Maximum file size 1MB'},413);
    const bytes=new Uint8Array(await request.arrayBuffer());
    if(bytes.length>1048576)return respond({error:'Maximum file size 1MB'},413);
    let listJson;
    try{listJson=convertRosz(bytes)}catch(e){return respond({error:String(e.message||e)},400)}
    const code=newCode(),expiresAt=Date.now()+TTL*1000;
    await env.ARMIES.put(code,JSON.stringify({listId:code,listJson,expiresAt}),{expirationTtl:TTL});
    return respond({code,expiresInSeconds:TTL,expiresAt,units:listJson.units.length,models:listJson.units.reduce((n,u)=>n+u.modelDefinitions.length,0)});
  }
  if(request.method==='GET'&&url.pathname==='/api/army'){
    const code=(url.searchParams.get('code')||'').toUpperCase().trim();
    if(!/^OPR-[A-HJ-NP-Z2-9]{9}$/.test(code))return respond({error:'Invalid army code'},400);
    const text=await env.ARMIES.get(code);
    if(!text)return respond({error:'Code not found or expired: upload again for a new code'},404);
    const data=JSON.parse(text);
    if(Date.now()>=data.expiresAt)return respond({error:'Code expired: upload again for a new code'},404);
    return respond({listId:data.listId,listJson:data.listJson});
  }
  return respond({error:'Not found'},404);
}};