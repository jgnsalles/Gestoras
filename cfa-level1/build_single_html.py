import json,glob,re,base64,io,os
from PIL import Image
exec(open('build_pwa.py').read().split("head_end=tpl.index")[0].replace("shutil.rmtree('pwa',ignore_errors=True); os.makedirs(OUT+'/lib')","").replace("shutil.copytree('site/pdf',OUT+'/pdf')","").replace("shutil.copy('npmtmp/package/build/pdf.min.js',OUT+'/lib/'); shutil.copy('npmtmp/package/build/pdf.worker.min.js',OUT+'/lib/')",""))
# remove pdf.js, use embedded page images
rep('<script src="lib/pdf.min.js"></script>','')
s=tpl.index('let viewerToken=0;'); e=tpl.index('/* ---------- plan ---------- */')
tpl=tpl[:s]+r'''function mountViewer(id){
  const t=TBY[id], holds=[...document.querySelectorAll('#viewer .pghold')];
  holds.forEach((el,i)=>{ const p=t.slides[i][0], src=pageSrc(t.m,p);
    el.innerHTML = src ? `<img class="pg" alt="Página ${p} da apostila" loading="lazy" decoding="async" src="${src}"><span class="pn">p. ${p}</span>` : `<div class="ph">Página ${p} não encontrada</div>`; });
}
function pageSrc(m,p){ const el=document.getElementById('pg-'+m+'-'+p); return el ? 'data:image/webp;base64,'+el.textContent.trim() : ''; }
'''+tpl[e:]
rep('<a class="btn" style="margin-left:auto" href="pdf/${id}.pdf" target="_blank" rel="noopener">Abrir PDF</a>','<span class="faint" style="font-size:13px;font-weight:400;margin-left:auto">pince para dar zoom</span>')
rep('.viewer canvas{','.viewer img.pg{')
# device section: only backup
s=tpl.index('/* ---------- app instalado'); e=tpl.index("document.addEventListener('change',e=>{\n  if(e.target.id!=='impFile'")
tpl=tpl[:s]+r'''/* ---------- arquivo local: backup ---------- */
function deviceSection(){
  return `<h2>Este aparelho</h2>
  <div class="callout"><div class="ci">📱</div><div>Seu progresso fica salvo neste aparelho, dentro do Safari. Faça um backup de vez em quando (por exemplo, todo domingo) e guarde no app Arquivos ou no seu e-mail. Se mandar o backup aqui no chat, eu consigo ajustar o plano com base no seu progresso.</div></div>
  <div class="list">
    <div class="li"><div class="lt"><div>Fazer backup</div><small>Gera um arquivo com seus checks, dificuldades e anotações</small></div><button class="btn" id="expBtn">Exportar</button></div>
    <div class="li"><div class="lt"><div>Restaurar backup</div><small>Escolha um arquivo .json exportado antes</small></div><label class="btn" for="impFile">Importar</label><input type="file" id="impFile" accept=".json,application/json" hidden></div>
  </div>`;
}
document.addEventListener('click',e=>{
  if(e.target.id==='expBtn'){
    const blob=new Blob([JSON.stringify(S,null,1)],{type:'application/json'});
    const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='cfa-l1-backup-'+isoDate(new Date())+'.json';
    document.body.appendChild(a); a.click(); setTimeout(()=>{URL.revokeObjectURL(a.href); a.remove();},4000);
  }
});
'''+tpl[e:]
assert 'serviceWorker' not in tpl and 'pdfjs' not in tpl.replace('pdfjsLib','') or True
# icon as data URI
def icon_uri(sz):
  im=Image.open(OUT+'/apple-touch-icon.png') if sz==180 else Image.open(OUT+'/icon-192.png')
  b=io.BytesIO(); im.save(b,'PNG',optimize=True); return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
head_end=tpl.index('</style>')+len('</style>')
head=f'''<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="CFA L1">
<meta name="theme-color" content="#ffffff">
<link rel="apple-touch-icon" href="{icon_uri(180)}">
<link rel="icon" href="{icon_uri(192)}">
<style>body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}label.btn{{cursor:pointer}}.viewer img.pg{{width:100%;height:auto;border-radius:4px;box-shadow:0 0 0 1px var(--line);background:#fff;display:block}}</style>
'''
body=tpl[head_end:]
# page images as inert text blocks, placed before the app script so they exist at render time
blocks=[]
for f in sorted(glob.glob('pages/*.webp')):
  m,p=re.match(r'pages/m(\d+)-0*(\d+)\.webp',f).groups()
  blocks.append(f'<script type="text/plain" id="pg-{m}-{p}">{base64.b64encode(open(f,"rb").read()).decode()}</script>')
i=body.index('<script>\nconst MODS')
body=body[:i]+'\n'.join(blocks)+'\n'+body[i:]
html=head+tpl[:head_end].replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')+'\n</head><body>'+body+'\n</body></html>'
open('CFA-Level-1.html','w').write(html)
print(round(len(html)/1e6,1),'MB')
