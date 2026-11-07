import json,shutil,os
from PIL import Image,ImageDraw,ImageFont
OUT='pwa/cfa-level1'
shutil.rmtree('pwa',ignore_errors=True); os.makedirs(OUT+'/lib')
shutil.copytree('site/pdf',OUT+'/pdf')
shutil.copy('npmtmp/package/build/pdf.min.js',OUT+'/lib/'); shutil.copy('npmtmp/package/build/pdf.worker.min.js',OUT+'/lib/')
d=json.load(open('structure.json'))
for m in d:
  for c in m['chapters']:
    for t in c['topics']: t.pop('kb',None)
tpl=open('template.html').read().replace('/*STRUCT*/',json.dumps(d,ensure_ascii=False,separators=(',',':')))
def rep(a,b):
  global tpl
  assert a in tpl, a[:60]; tpl=tpl.replace(a,b)
rep('É só me pedir no chat que eu ajusto o plano. Seu progresso fica salvo e eu consigo ler.','É só me pedir no chat que eu ajusto o plano (se quiser que eu veja seu progresso, me mande o arquivo de backup).')
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>','<script src="lib/pdf.min.js"></script>')
rep("getDocument({url:'pdf/'+id+'.pdf'})","getDocument({url:'pdf/'+id+'.pdf',disableRange:true,disableStream:true})")
rep('h+=`<p class="faint" style="font-size:12px;margin-top:30px">Pesos',
 'h+=deviceSection();\n  h+=`<p class="faint" style="font-size:12px;margin-top:30px">Pesos')
extra = r'''
/* ---------- app instalado: offline + backup ---------- */
const IS_PWA = true;
if('serviceWorker' in navigator){ navigator.serviceWorker.register('sw.js').catch(()=>{}); }
try{ navigator.storage && navigator.storage.persist && navigator.storage.persist(); }catch(e){}
function offlineCount(){ return +(lsGet('cfa-l1-offline')||0); }
function deviceSection(){
  const n=offlineCount(), all=TOPICS.length;
  return `<h2>Este aparelho</h2>
  <div class="callout"><div class="ci">📱</div><div>Seu progresso fica salvo neste aparelho. Faça um backup de vez em quando (por exemplo, todo domingo) e guarde no app Arquivos ou no seu e-mail.</div></div>
  <div class="list">
    <div class="li"><div class="lt"><div>Apostilas offline</div><small id="offTxt">${n>=all?'Todos os '+all+' recortes estão salvos no aparelho':(n?n+' de '+all+' recortes salvos':'Baixe uma vez (≈65 MB) e estude sem internet')}</small></div><button class="btn" id="offBtn">${n>=all?'Atualizar':'Baixar tudo'}</button></div>
    <div class="li"><div class="lt"><div>Fazer backup</div><small>Gera um arquivo com seus checks, dificuldades e anotações</small></div><button class="btn" id="expBtn">Exportar</button></div>
    <div class="li"><div class="lt"><div>Restaurar backup</div><small>Escolha um arquivo .json exportado antes</small></div><label class="btn" for="impFile">Importar</label><input type="file" id="impFile" accept=".json,application/json" hidden></div>
  </div>`;
}
document.addEventListener('click',async e=>{
  if(e.target.id==='offBtn'){
    const b=e.target, txt=document.getElementById('offTxt'); b.disabled=true;
    let ok=0; const ids=TOPICS.map(t=>t.id);
    const cache = 'caches' in window ? await caches.open('cfa-pdf-v1') : null;
    for(let i=0;i<ids.length;i+=6){
      await Promise.all(ids.slice(i,i+6).map(async id=>{ try{ const url='pdf/'+id+'.pdf'; const r=await fetch(url,{cache:'reload'}); if(r.ok){ if(cache) await cache.put(url,r.clone()); ok++; } }catch(err){} }));
      txt.textContent='Baixando… '+ok+' de '+ids.length;
    }
    lsSet('cfa-l1-offline',ok); txt.textContent= ok===ids.length ? 'Todos os '+ok+' recortes estão salvos no aparelho' : ok+' de '+ids.length+' salvos. Tente de novo com internet.';
    b.disabled=false; b.textContent= ok===ids.length?'Atualizar':'Tentar de novo';
  }
  if(e.target.id==='expBtn'){
    const blob=new Blob([JSON.stringify(S,null,1)],{type:'application/json'});
    const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='cfa-l1-backup-'+isoDate(new Date())+'.json';
    document.body.appendChild(a); a.click(); setTimeout(()=>{URL.revokeObjectURL(a.href); a.remove();},4000);
  }
});
document.addEventListener('change',e=>{
  if(e.target.id!=='impFile' || !e.target.files[0]) return;
  const fr=new FileReader(); fr.onload=()=>{ try{ const o=JSON.parse(fr.result); if(!o||typeof o.t!=='object') throw 0; S=Object.assign({t:{},pace:5,start:S.start,upd:0},o); save(); render(); refreshSide(); alertBox('Backup restaurado: '+Object.keys(S.t).length+' assuntos com marcações.'); }catch(err){ alertBox('Esse arquivo não parece um backup deste app.'); } };
  fr.readAsText(e.target.files[0]);
});
function alertBox(msg){ const t=document.getElementById('tip'); t.textContent=msg; t.style.left='16px'; t.style.top='60px'; t.hidden=false; setTimeout(()=>t.hidden=true,3500); }
'''
rep('refreshSide(); render();\n</script>', extra+'\nrefreshSide(); render();\n</script>')
head_end=tpl.index('</style>')+len('</style>')
head='''<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="CFA L1">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#191919" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" href="icon-192.png">
<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}label.btn{cursor:pointer}</style>
'''
html=head+tpl[:head_end].replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')+'\n</head><body>'+tpl[head_end:]+'\n</body></html>'
open(OUT+'/index.html','w').write(html)
json.dump({"name":"CFA Level 1","short_name":"CFA L1","start_url":"./","scope":"./","display":"standalone","background_color":"#ffffff","theme_color":"#ffffff","lang":"pt-BR",
 "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]},open(OUT+'/manifest.webmanifest','w'),ensure_ascii=False,indent=1)
open(OUT+'/sw.js','w').write('''const SHELL='cfa-shell-v1', PDF='cfa-pdf-v1';
const FILES=['./','index.html','manifest.webmanifest','lib/pdf.min.js','lib/pdf.worker.min.js','icon-192.png','icon-512.png','apple-touch-icon.png'];
self.addEventListener('install',e=>{ e.waitUntil(caches.open(SHELL).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())); });
self.addEventListener('activate',e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==SHELL&&k!==PDF).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); });
self.addEventListener('fetch',e=>{
  const req=e.request; if(req.method!=='GET') return;
  const url=new URL(req.url); if(url.origin!==location.origin) return;
  if(url.pathname.includes('/pdf/')){
    // recortes: do aparelho primeiro; baixa e guarda se ainda não tiver
    e.respondWith(caches.open(PDF).then(async c=>{ const hit=await c.match(url.pathname.slice(url.pathname.indexOf('pdf/'))) || await c.match(req,{ignoreSearch:true}); if(hit) return hit;
      const r=await fetch(req); if(r.ok) c.put(req,r.clone()); return r; }));
    return;
  }
  // app: tenta a versão nova; sem internet, usa a salva
  e.respondWith(fetch(req).then(r=>{ if(r.ok){ const cp=r.clone(); caches.open(SHELL).then(c=>c.put(req,cp)); } return r; })
    .catch(()=>caches.match(req,{ignoreSearch:true}).then(r=>r||caches.match('index.html'))));
});
''')
# icons
def icon(sz,fn):
  im=Image.new('RGB',(sz,sz),'#37352f'); dr=ImageDraw.Draw(im)
  # ledger grid like the app cover
  step=sz//12
  for x in range(0,sz,step): dr.line([(x,0),(x,sz)],fill='#403e38',width=max(1,sz//256))
  for y in range(0,sz,step): dr.line([(0,y),(sz,y)],fill='#403e38',width=max(1,sz//256))
  # compounding curve
  pts=[(i/40*sz, sz*0.86 - (1.075**i)*sz*0.04) for i in range(41)]
  dr.line(pts,fill='#8a8576',width=max(2,sz//80))
  fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(sz*0.36))
  fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(sz*0.13))
  dr.text((sz/2,sz*0.30),'CFA',font=fs,fill='#c9c4b6',anchor='mm')
  dr.text((sz/2,sz*0.55),'L1',font=fb,fill='#ffffff',anchor='mm')
  im.save(OUT+'/'+fn)
icon(180,'apple-touch-icon.png'); icon(192,'icon-192.png'); icon(512,'icon-512.png')
print('ok')
