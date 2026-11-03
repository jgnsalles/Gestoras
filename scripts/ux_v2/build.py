"""Gera output/navegando_dilma_2_v2.html a partir de output/navegando_dilma_2.html.

Acrescenta a aba Ciclo, o mapa de calor do Resumo, as bolhas de Empresas, a linha do
tempo das Cartas e tabelas em cartões no celular. Os dados embutidos não mudam.
Uso: python3 scripts/ux_v2/build.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'output', 'navegando_dilma_2.html')
OUT = os.path.join(ROOT, 'output', 'navegando_dilma_2_v2.html')

s = open(SRC, encoding='utf-8').read()
css = open(os.path.join(HERE, 'ux.css'), encoding='utf-8').read()
js = open(os.path.join(HERE, 'ux.js'), encoding='utf-8').read()
gross = open(os.path.join(ROOT, 'output', 'dashboard', 'captacao_bruta.csv'), encoding='utf-8').read()

CICLO = '''<section class="rx-page" id="pg-ciclo" data-pg="ciclo">
    <article class="rx-card" id="cy-card">
      <h2>O ciclo, mês a mês</h2>
      <div class="rx-legend" data-draw="cy-legend"></div>
      <div class="rx-chips-b" data-draw="cy-gran"></div>
      <div class="rx-chart" data-draw="cy-main" data-source="serie_mensal precos acoes ibov"></div>
      <p class="rx-note">Fundos: média simples da cota dos 30 masters. Setores: mediana do retorno das ações do setor no trimestre menos o Ibovespa. Universo: ações que algum dos 30 fundos teve com ≥0,5% do PL. Captação e resgate: soma diária do Informe Diário da CVM no master de cada fundo.</p>
    </article>
    <article class="rx-card" id="cy-fases">
      <h2>Melhores e piores por fase</h2>
      <p class="rx-note">Retorno total com dividendos. Só entram ações com preço em todos os meses da fase. Toque numa ação para ver o gráfico dela.</p>
      <div data-draw="cy-phases" data-source="precos acoes"></div>
    </article>
    <article class="rx-card" id="cy-acao-card">
      <h2 data-draw="cy-acao-t">—</h2>
      <div class="rx-legend" data-draw="cy-acao-lg"></div>
      <div class="rx-chart" data-draw="cy-acao" data-source="precos posicoes_1 posicoes_2"></div>
      <div class="rx-split" data-draw="cy-acao-k"></div>
    </article>
  </section>

  '''

HEAT = '''<article class="rx-card" id="resumo-heat">
      <h2>Fundos × ano</h2>
      <p class="rx-note">Cor: diferença para o Ibovespa (verde bateu, vermelho perdeu). Número: retorno do fundo. Ordenado pelo total. Toque no nome para abrir o fundo.</p>
      <div class="rx-chart" data-draw="hm-sum" data-source="fundos serie_mensal ibov"></div>
    </article>
    '''

BUB = '''<article class="rx-card" id="empresas-bolhas">
      <h2>O que todos tinham × o que rendeu</h2>
      <p class="rx-note">Cada bolha é uma empresa. Direita: mais peso nos fundos. Acima da linha: bateu o Ibovespa no ano. Tamanho: nº de fundos com ≥1% do PL em algum mês do ano. Toque para ver no Ciclo.</p>
      <div class="rx-chips-b" data-draw="bub-anos" data-source="serie_mensal"></div>
      <div class="rx-chart" data-draw="emp-bub" data-source="posicoes_1 posicoes_2 precos acoes"></div>
    </article>
    '''

CT = '''<article class="rx-card" id="cartas-tempo">
      <h2>Teses no tempo</h2>
      <p class="rx-note">Cada ponto é uma tese das cartas: data da carta × resultado contra o Ibovespa em 2 anos (ou 1). Faixa cinza: ±5 p.p.</p>
      <div class="rx-legend" data-draw="ct-legend"></div>
      <div class="rx-chart" data-draw="ct-time" data-source="cartas_teses precos ibov"></div>
      <div id="ct-det" data-draw="ct-det"></div>
    </article>
    '''

REPL = [
    ('<title>Navegando Dilma 2</title>', '<title>Navegando Dilma 2 v2</title>', 1),
    ('</style></head>', css + '</style></head>', 1),
    ("pg: 'resumo'", "pg: 'ciclo'", 2),
    ('<button type="button" role="tab" class="rx-tab" data-pg="resumo" aria-selected="true">Resumo</button>',
     '<button type="button" role="tab" class="rx-tab" data-pg="ciclo" aria-selected="true">Ciclo</button>\n      '
     '<button type="button" role="tab" class="rx-tab" data-pg="resumo" aria-selected="false">Resumo</button>', 1),
    ('<section class="rx-page" id="pg-resumo" data-pg="resumo">',
     CICLO + '<section class="rx-page" id="pg-resumo" data-pg="resumo" hidden>\n    ' + HEAT, 1),
    ('<div class="rx-tablebox rx-sumbox" data-draw="tb-sum" data-source="fundos serie_mensal ibov"></div>',
     '<details class="rx-more"><summary>Ver tabela</summary><div class="rx-tablebox rx-sumbox" data-draw="tb-sum" data-source="fundos serie_mensal ibov"></div></details>', 1),
    ('<article class="rx-card" id="resumo-tabela">\n      <div class="rx-cardhead">\n        <h2>Resumo dos 30 fundos</h2>',
     '<article class="rx-card" id="resumo-tabela">\n      <div class="rx-cardhead">\n        <h2>Tabela dos 30 fundos</h2>', 1),
    ('<article class="rx-card" id="empresas-card">', BUB + '<article class="rx-card" id="empresas-card">', 1),
    ('<article class="rx-card" id="cartas-gestoras">', CT + '<article class="rx-card" id="cartas-gestoras">', 1),
    ('<script type="text/csv" id="csv-encerrados">', '<script type="text/csv" id="csv-captacao_bruta">\n' + gross + '</script>\n<script type="text/csv" id="csv-encerrados">', 1),
    ('<script>dash._run();</script>', '<script>\n' + js + '\n</script>\n<script>dash._run();</script>', 1),
]
for old, new, n in REPL:
    c = s.count(old)
    assert c == n, (old[:60], c)
    s = s.replace(old, new)
open(OUT, 'w', encoding='utf-8').write(s)
print(OUT, os.path.getsize(OUT) // 1024, 'KB')
