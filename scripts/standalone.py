import re, sys, os
S, OUT = sys.argv[1], sys.argv[2]
page = open(S+'/out/index.html').read().replace('<meta name="dash-one-writer">\n','')
style = re.search(r'<style>(.*?)</style>', page, re.S).group(1)
script = re.search(r'<script>(.*?)</script>', page, re.S).group(1)
body = re.sub(r'<style>.*?</style>|<script>.*?</script>', '', page, flags=re.S).strip()
d3 = open(S+'/lib/d3.min.js').read()
ids = ['fundos','serie_mensal','posicoes_1','posicoes_2','precos','acoes','ibov','cartas_gestoras','cartas_links','cartas_teses']
data = '\n'.join(f'<script type="text/csv" id="csv-{i}">\n{open(S+"/out/"+i+".csv").read()}</script>' for i in ids)
tokens = '''
:root{
  --color-bg:#f6f7f9; --color-panel:#ffffff; --color-fg:#17202b; --color-fg-muted:#5b6675; --color-border-line:#e1e5eb;
  --color-ok:#1f8a4c; --color-bad:#c4372f;
  --cds-chart-muted:#a9b2bf; --cds-chart-grid:#edf0f4; --cds-chart-axis:#b8c0cc; --cds-chart-reference:#8c96a3;
  --cds-surface-popover:#ffffff; --cds-border:#d5dbe3; --cds-shadow-popover:0 6px 20px rgba(20,30,45,.14); --cds-text-secondary:#5b6675;
  --font-anthropic-sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-anthropic-serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --cds-font-size-caption:.78rem; --cds-font-size-body:.95rem; --cds-font-size-heading:1.08rem; --cds-font-size-title:1.75rem; --cds-font-weight-medium:600;
  --cds-gap-xs:4px; --cds-gap-sm:8px; --cds-gap-md:14px; --cds-gap-lg:22px;
  --cds-pad-xs:4px; --cds-pad-sm:8px; --cds-pad-md:14px; --cds-pad-lg:18px; --cds-radius:8px; --cds-dur-slow:.3s;
  color-scheme: light;
}
@media (prefers-color-scheme: dark){ :root{
  --color-bg:#10151c; --color-panel:#171e27; --color-fg:#e8edf3; --color-fg-muted:#9aa6b5; --color-border-line:#2a3441;
  --color-ok:#4cc27e; --color-bad:#f0736a;
  --cds-chart-muted:#5d6878; --cds-chart-grid:#222b36; --cds-chart-axis:#3c4757; --cds-chart-reference:#6f7a8a;
  --cds-surface-popover:#1d2530; --cds-border:#334050; --cds-shadow-popover:0 6px 20px rgba(0,0,0,.45); --cds-text-secondary:#9aa6b5;
  color-scheme: dark; } }
html,body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:15px}
#dash-root{max-width:1280px;margin:0 auto;padding-block:24px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
'''
shim = '''
window.dash = (() => {
  const data = {}; ['%s'].forEach((id) => { data[id] = d3.csvParse(document.getElementById('csv-' + id).textContent.trim()); });
  const DEF = { fundo: '1', inicio: '2013-12', fim: '2018-12', acao: null, pg: 'resumo', aba: 'perf', emp: 'ano', anoEmp: null, graf: 'stack', gestora: null };
  let P = { ...DEF }; const draws = new Map(); const hooks = [];
  const runOne = (name) => { const fn = draws.get(name); if (!fn) return; document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => { try { fn(el); } catch (e) { console.error(name, e); } }); };
  const runAll = () => { hooks.forEach((f) => { try { f(); } catch (e) { console.error(e); } }); for (const n of draws.keys()) runOne(n); };
  let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(runAll, 150); });
  return {
    data: (id) => ({ status: 'ok', data: data[id] || [] }),
    params: () => ({ ...P }),
    setParams: (o) => { P = { ...P, ...o }; runAll(); },
    resetParams: () => { P = { ...DEF }; runAll(); },
    draw: (name, fn) => { if (fn) draws.set(name, fn); else runOne(name); },
    onData: (f) => { hooks.push(f); }, refresh: () => {}, setLink: () => {},
    colors: ['#2f6fd0', '#d9822b', '#2a9d8f', '#c4467a', '#7a5cc4', '#8a9a2b', '#b5523b', '#4a90a4'],
    _run: runAll,
  };
})();
''' % "','".join(ids)
html = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Navegando Dilma 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=Source+Serif+4:wght@400&display=swap">
<style>{tokens}{style}</style></head>
<body><div id="dash-root">
{body}
</div>
{data}
<script>{d3}</script>
<script>{shim}</script>
<script>{script}</script>
<script>dash._run();</script>
</body></html>'''
open(OUT,'w').write(html); print(os.path.getsize(OUT)//1024,'KB')
