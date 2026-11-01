import pandas as pd, re, json, glob, os, urllib.parse
F=pd.read_csv('out/fundos.csv')
def ids(g): return ' '.join(str(i) for i in F[F.gestora.str.contains(g,case=False)].id)
G=[ # gestora, match, arquivo, status
 ('Dynamo','Dynamo','https://www.dynamo.com.br/pt/cartas-dynamo','Arquivo completo desde 1993 no site.'),
 ('Squadra','Squadra','https://www.squadrainvest.com.br/cartas/','Cartas anuais (não há carta de 2014 e 2017 no arquivo).'),
 ('Oceana','Oceana','https://www.oceanainvestimentos.com.br/carta-de-gestao/','Cartas semestrais no site.'),
 ('Alaska','Alaska','https://www.alaska-asset.com.br/cartas/','Cartas trimestrais/semestrais e mensais (a partir de ago/2017).'),
 ('Atmos','Atmos','https://www.atmoscapital.com.br/cartas.php','Cartas semestrais numeradas.'),
 ('Guepardo','Guepardo','https://www.guepardoinvest.com.br/cartas-da-gestora/','Cartas trimestrais desde 2005.'),
 ('Bogari','Bogari','https://bogaricapital.com.br/biblioteca/cartas/','Cartas temáticas (sem data no título); não resumidas.'),
 ('SPX','Spx','https://www.spxcapital.com/fundos','Não publica cartas abertas; só relatórios mensais dos fundos.'),
 ('Apex','Apex','https://www.apexcapital.com.br/cartas','Página de cartas existe, mas as de 2014–2018 não estão acessíveis.'),
 ('Brasil Capital','Bc','https://brasilcapital.com/cartas-de-gestao/','Arquivo público só a partir de 2024.'),
 ('JGP','Jgp','https://www.jgp.com.br/comunicacoes/carta/','Arquivo público a partir de 2020.'),
 ('Bahia AM','Bahia','https://www.bahiaasset.com.br/carta-do-gestor/','Arquivo público só com cartas recentes.'),
 ('Constellation','Constellation','https://capitalaberto.com.br/empresas/2018/04/crise-boa-para-investir','Sem arquivo público; usamos reportagem da Capital Aberto sobre a carta de dez/2017.'),
 ('Moat','Moat','https://acionista.com.br/moat-capital-carta-aos-investidores-1t20/','Gestora começou em 2016; cartas públicas encontradas só a partir de 2020.'),
 ('Navi','Navi','https://www.empiricus.com.br/conteudo-extra/cartas-dos-gestores/navi-capital-carta-do-gestor-junho2021/','Gestora formada em 2017; cartas públicas encontradas só a partir de 2021.'),
 ('Núcleo','Nucleo','https://www.nucleocapital.com.br','Não encontramos cartas públicas.'),
 ('Tempo Capital','Tempo','https://www.tempocapital.com.br','Não encontramos cartas públicas.'),
 ('Velt','Velt','https://braziljournal.com/a-bolsa-ficou-pequena-por-isso-a-velt-vai-mudar-de-estrategia/','Site fora do ar; não encontramos cartas públicas.'),
 ('Una Capital (Mainá)','Una','https://www.unacapital.com.br','Não encontramos cartas públicas.'),
 ('Neo','Neo','','Site fora do ar; não encontramos cartas públicas.'),
 ('Equitas / Drys','Drys','','Não encontramos cartas públicas.'),
 ('STK','Stk','','Não encontramos cartas públicas.'),
 ('Perfin','Perfin','https://www.perfin.com.br','Não encontramos cartas públicas de 2014–2018.'),
 ('Indie','Indie','https://www.indiecapital.com.br','Não encontramos cartas públicas.'),
]
gest=pd.DataFrame([dict(gestora=g,fundos=ids(m),arquivo=a,status=s) for g,m,a,s in G])
L=[]
def add(g,data,tit,url): L.append(dict(gestora=g,data=data,carta=tit,url=url))
for f,(lab,ym) in {'2014/trimestre4':('4º tri 2014','2014-12'),'2015/trimestre1_2015':('1º tri 2015','2015-03'),'2015/trimestre2_2015':('2º tri 2015','2015-06'),'2015/trimestre3_2015':('3º tri 2015','2015-09'),'2015/trimestre4_2015':('4º tri 2015','2015-12'),'2016/semestre1_2016':('1º sem 2016','2016-06'),'2016/semestre2_2016':('2º sem 2016','2016-12'),'2017/semestre1_2017':('1º sem 2017','2017-06'),'2017/semestre2_2017':('2º sem 2017','2017-12'),'2018/semestre1_2018':('1º sem 2018','2018-06'),'2018/semestre2_2018':('2º sem 2018','2018-12')}.items():
    add('Alaska',ym,'Carta '+lab,f'https://www.alaska-asset.com.br/pdf/cartas/{f}.pdf')
s=open('web/arch_www_oceanainvestimentos_com_br_carta-de-gestao_.html',encoding='utf8',errors='ignore').read()
for u in sorted(set(re.findall(r'href="(http[^"]*Oceana-Investimentos-20(?:1[4-8])S[12][^"]*\.pdf)"',s))):
    y,h=re.search(r'(201[4-8])S([12])',u).groups(); add('Oceana',f'{y}-{"06" if h=="1" else "12"}',f'Carta {h}º semestre {y}',urllib.parse.quote(u.replace('http://','https://'),safe=':/%'))
for f,(lab,ym) in {'carta-2013':('Carta anual 2013 (inclui Equatorial)','2013-12'),'carta-2015':('Carta anual 2015','2015-12'),'carta-2016':('Carta anual 2016','2016-12'),'carta-2018':('Carta anual 2018','2018-12')}.items():
    add('Squadra',ym,lab,f'https://www.squadrainvest.com.br/wp-content/uploads/2022/09/{f}.pdf')
MES={'Mar':'03','Jun':'06','Set':'09','Dez':'12','Mai':'05'}
for f in sorted(glob.glob('cartas/guepardo_*.pdf')):
    n=os.path.basename(f)[9:-4]; m=re.search(r'-(Mar|Jun|Set|Dez|Mai)(\d\d)$',n); ym=f'20{m.group(2)}-{MES[m.group(1)]}'
    add('Guepardo',ym,f'Carta nº {n.split("-")[0]} ({m.group(1).lower()}/{m.group(2)})',f'https://www.guepardoinvest.com.br/Carta-{n}.pdf')
for n,(lab,ym) in {'11':('1º sem 2014','2014-06'),'12':('2º sem 2014','2014-12'),'13':('1º sem 2015','2015-06'),'14':('2º sem 2015','2015-12'),'15':('1º sem 2016','2016-06'),'16':('2º sem 2016','2016-12'),'17':('1º sem 2017','2017-06'),'18':('2º sem 2017','2017-12'),'19':('1º sem 2018','2018-06'),'20':('2º sem 2018','2018-12')}.items():
    add('Atmos',ym,f'Carta Atmos nº {n} ({lab})',f'https://www.atmoscapital.com.br/documentos/cartas/Carta-Atmos-{n}.pdf')
for f in sorted(glob.glob('web/dynapi_*.json')):
    try: d=json.load(open(f))
    except Exception: continue
    if not isinstance(d,list): continue
    for p in d:
        if not isinstance(p,dict): continue
        t=re.sub('<[^>]+>','',p['title']['rendered']).replace('&#8211;','–'); m=re.match(r'Carta (\d+)',t)
        if m and 82<=int(m.group(1))<=99:
            pdf=re.findall(r'https?://[^"\']+\.pdf',p['content']['rendered'])
            txt=open(f'cartas/dynamo_{int(m.group(1)):03d}.txt',errors='ignore').read() if os.path.exists(f'cartas/dynamo_{int(m.group(1)):03d}.txt') else ''
            dm=re.search(r'Rio de Janeiro,? \d{1,2} de ([a-zç]+) de (20\d\d)',re.sub(r'\s+',' ',txt))
            mm={'janeiro':'01','fevereiro':'02','março':'03','abril':'04','maio':'05','junho':'06','julho':'07','agosto':'08','setembro':'09','outubro':'10','novembro':'11','dezembro':'12'}
            ym=f'{dm.group(2)}-{mm.get(dm.group(1),"01")}' if dm else ''
            add('Dynamo',ym,t,pdf[0] if pdf else p['link'])
add('Constellation','2017-12','Reportagem sobre a carta de dez/2017 (Capital Aberto)','https://capitalaberto.com.br/empresas/2018/04/crise-boa-para-investir')
for n,t in [('20','Privatizações'),('23','Elétricas'),('16','Nióbio'),('29','Discurso x Prática')]:
    pass
bog=open('web/bog.html',encoding='utf8',errors='ignore').read()
for u in sorted(set(re.findall(r'href="(http://bogaricapital\.com\.br/wp-content/uploads/201[5-9]/\d\d/Carta-Bogari-\d+-[^"]+\.pdf)"',bog))):
    if '%C3' in u: continue
    n=re.search(r'Carta-Bogari-(\d+)-([^"]+)\.pdf',u); add('Bogari','',f'Carta nº {int(n.group(1))} – {n.group(2).replace("-"," ")}',urllib.parse.quote(u.replace('http://','https://'),safe=':/%'))
L=pd.DataFrame(L).drop_duplicates('url')
# --- teses ---
T=[]
def th(g,carta,url,base,tk,pos,visao,acao,janela='depois',nota=''):
    T.append(dict(gestora=g,carta=carta,url=url,base=base,tk=tk,posicao=pos,visao=visao,acao=acao,janela=janela,nota=nota))
sq='https://www.squadrainvest.com.br/wp-content/uploads/2022/09/'
th('Squadra','Carta anual 2013',sq+'carta-2013.pdf','2013-12','EQTL3','comprada','Equatorial é a maior posição desde 2012: executivos com cultura de dono, metas cobradas, e capacidade de fazer turnaround de distribuidoras ruins (Celpa, comprada em 2012). Setor visto como previsível e pouco correlacionado ao ciclo.','Maior posição dos fundos; mais de 15% do capital da empresa; aproveitou a queda antes do aumento de capital (R$ 16) para montar posição.')
th('Squadra','Carta anual 2015',sq+'carta-2015.pdf','2015-12','VVAR11','comprada','Mea culpa: “erramos em quase tudo” em Via Varejo (negócio, gestão, controlador, ciclo e tamanho da posição), que chegou a ser a 2ª maior posição.','Perda com Via Varejo anulou o ganho com Equatorial em 2015.','antes')
th('Squadra','Carta anual 2016',sq+'carta-2016.pdf','2015-12','BRML3','comprada','BR Malls a valuation de crise (níveis só vistos em 2008); única grande de shoppings sem controlador, o que exigiu atuação em governança (contra mudança na poison pill).','Aumentou bastante a posição no 2º semestre de 2015 e indicou conselheiros.')
th('Squadra','Carta anual 2016',sq+'carta-2016.pdf','2016-12','COGN3','vendida','Posição vendida no setor de educação (Kroton): margens e retornos excepcionalmente altos, sustentados por FIES e regulação, vistos como insustentáveis.','Short em educação ganhou relevância no portfólio vendido do Long-Biased.')
th('Squadra','Carta anual 2018',sq+'carta-2018.pdf','2018-03','ELPL3','comprada','Eletropaulo: depois do acordo com a Eletrobras, a Squadra apostou numa disputa pelo controle quando a Energisa lançou OPA a R$ 19,38.','Comprou cerca de 5% dos fundos a preço médio de ~R$ 20 esperando um leilão entre interessados.',nota='A disputa aconteceu: a Enel venceu com oferta de R$ 45,22 por ação em junho de 2018.')
th('Squadra','Carta anual 2018',sq+'carta-2018.pdf','2018-06','CESP6','comprada','Estatais em processo de “desestatização”; CESP como caso de privatização com indicação de conselheiros pela Squadra.','Posição em CESP com participação no conselho; boa parte do ganho veio após o leilão de outubro de 2018.')
at='https://www.atmoscapital.com.br/documentos/cartas/Carta-Atmos-'
th('Atmos','Carta nº 13 (1º sem 2015)',at+'13.pdf','2015-06','BBDC4','comprada','Bancos privados: com bancos públicos sobrealavancados e estrangeiros saindo (HSBC, Santander menos agressivo), “um oligopólio educado parece renascer”.','Bradesco e Itaúsa entre as maiores posições do fundo.')
th('Atmos','Carta nº 14 (2º sem 2015)',at+'14.pdf','2015-12','BRML3','cautela','Shoppings: lojistas fechando lojas e renegociando aluguel; “aluguéis parecem contratos bastante frágeis” na recessão.','Cautela com o setor; fundo com baixa exposição a ações entre 2009 e 2016 por visão negativa do ciclo.')
th('Atmos','Carta nº 18 (2º sem 2017)',at+'18.pdf','2017-12','PETR4','comprada','Pela primeira vez em muito tempo as estatais tomam decisões racionais: Petrobras mudou a política de preços, vendeu ativos e cortou custos; Eletrobras e BB também.','Aumentou a alocação em ações e entrou em estatais (Petrobras, Eletrobras, Banco do Brasil).')
th('Atmos','Carta nº 18 (2º sem 2017)',at+'18.pdf','2017-12','ELET3','comprada','Eletrobras vendendo subsidiárias, com programa de demissões e discussão de capitalização (privatização).','Posição em Eletrobras junto com Petrobras e BB.')
th('Atmos','Carta nº 20 (2º sem 2018)',at+'20.pdf','2018-12','CIEL3','saída','Cielo, por anos posição importante e lucrativa, “iniciou um processo de destruição de valor acelerado” com a competição em adquirência.','Saiu da posição.')
ak='https://www.alaska-asset.com.br/pdf/cartas/'
th('Alaska','Carta 1º tri 2015',ak+'2015/trimestre1_2015.pdf','2015-03','UGPA3','comprada','Investir é investir em pessoas: Ultrapar como exemplo de alinhamento de longo prazo entre controle e gestão (programa de ações de Pery Igel).','Ultrapar entre as posições; carteira concentrada em empresas de gestão forte.')
th('Alaska','Carta 2º sem 2017',ak+'2017/semestre2_2017.pdf','2017-12','MGLU3','comprada','Magazine Luiza: cultura e propósito de Luiza Trajano e do time como vantagem (“lidar com as necessidades do consumidor de classe média”, não só vender geladeira).','Maior posição e maior contribuição do fundo em 2016–2017; manteve mesmo após a forte alta.')
th('Alaska','Carta 1º sem 2017',ak+'2017/semestre1_2017.pdf','2017-05','BOVA11','mercado','Dia do áudio de Joesley (18/05/2017): queda vista como ruído, não fundamento, e “grande oportunidade de compra”.','Manteve as posições e comprou na queda.')
oc='https://www.oceanainvestimentos.com.br/mmweb/wp-content/uploads/'
oL=L[L.gestora=='Oceana'].set_index('data').url
th('Oceana','Carta 2º semestre 2014',oL['2014-12'],'2014-12','EQTL3','comprada','Equatorial: TIR real estimada de 12% num setor defensivo, boa governança e gestão eficiente.','Uma das posições mais atrativas do portfólio.')
th('Oceana','Carta 2º semestre 2014',oL['2014-12'],'2014-12','BVMF3','comprada','BM&FBovespa a P/L de 13–14x (11x sem a participação na CME), TIR real de 13–14%; risco de autuação fiscal do ágio dimensionado.','Posição relevante.')
th('Oceana','Carta 1º semestre 2015',oL['2015-06'],'2015-06','CIEL3','reduziu','Cielo de alta qualidade e protegida da competição, mas a alta do semestre reduziu a margem de segurança.','Reduziu parte da posição.')
th('Oceana','Carta 2º semestre 2015',oL['2015-12'],'2015-12','COGN3','comprada','Crédito restrito pune os alavancados e favorece empresas sólidas e desalavancadas que podem consolidar seus setores (Kroton e Equatorial).','Manteve Kroton e Equatorial como posições centrais.')
th('Oceana','Carta 1º semestre 2016',oL['2016-06'],'2016-06','GFSA3','comprada','Gafisa a 24% do valor patrimonial, com Tenda (baixa renda) e participação em Alphaville valendo mais que a empresa inteira.','Posição de valor em incorporação.')
th('Oceana','Carta 2º semestre 2016',oL['2016-12'],'2016-12','IGTA3','comprada','Shoppings dominantes (Iguatemi, Multiplan) vendem por m² muito acima de BR Malls e Aliansce na crise; lojistas mais saudáveis.','Iguatemi como tese principal do setor.')
th('Oceana','Carta 1º semestre 2017',oL['2017-06'],'2017-06','UGPA3','reduziu','Ultrapar: trabalho de campo indicou recuperação de market share da Ipiranga contra os postos bandeira branca.','Ganhou com a alta e reduziu a posição pela menor margem de segurança.')
th('Oceana','Carta 1º semestre 2017',oL['2017-06'],'2017-06','BBSE3','comprada','BB Seguridade descontada porque o mercado focou no efeito da queda da Selic no resultado de curto prazo.','Comprou a preço atrativo e teve ganho relevante.')
th('Oceana','Carta 1º semestre 2018',oL['2018-06'],'2018-06','SEER3','comprada','Ser Educacional: menores custos do setor, marcas fortes no Nordeste e caixa confortável para ganhar com a consolidação do ensino superior.','Investimento em Ser Educacional detalhado na carta.')
gp=lambda n:L[(L.gestora=='Guepardo')&L.carta.str.contains(f'nº {n} ')].url.iloc[0]
th('Guepardo','Carta nº 70 (dez/14)',gp(70),'2014-12','BRFS3','comprada','BRF: a equipe que assumiu em 2013 vinha gerando valor “de forma recorrente trimestre após trimestre”.','Maior posição dos fundos.')
th('Guepardo','Carta nº 70 (dez/14)',gp(70),'2014-12','TPIS3','saída','Triunfo: muito valor nos negócios individuais, mas a alocação de capital e a alavancagem decepcionaram; reconhecido como erro.','Terminou o desinvestimento no 4º trimestre de 2014.')
th('Guepardo','Carta nº 70 (dez/14)',gp(70),'2014-12','JSLG3','comprada','JSL: resultado acima do esperado; mercado interpretou mal o guidance de 2014.','Manteve como posição relevante.')
th('Guepardo','Carta nº 79 (dez/16)',gp(79),'2016-12','GGBR4','saída','Gerdau: recuperou as perdas de 2014–2015 em 2016, mas o retorno ficou abaixo da renda fixa; cenário mudou em relação à tese.','Desinvestimento total de Gerdau e Metalúrgica Gerdau.')
th('Guepardo','Carta nº 79 (dez/16)',gp(79),'2016-12','BRFS3','comprada','BRF: espera de melhora de resultados no 2º semestre de 2017.','Aproveitou a queda das ações para aumentar a posição.')
th('Guepardo','Carta nº 83 (dez/17)',gp(83),'2017-12','RAIL3','comprada','Rumo sob a Cosan: ganhos de eficiência (6% menos combustível por t·km), novos contratos (Fibria) e alavancagem operacional.','Posição em Rumo e Cosan Logística.')
th('Guepardo','Carta nº 88 (dez/18)',gp(88),'2018-12','VULC3','comprada','Vulcabras com a operação da Under Armour no Brasil e menos concorrência de importados.','Posição em Vulcabras (+40,6% no 4º tri de 2018).')
dy=lambda n:L[(L.gestora=='Dynamo')&L.carta.str.startswith(f'Carta {n} ')].url.iloc[0]
th('Dynamo','Carta 83/84 – Renner',dy(83),'2014-12','LREN3','comprada','Renner, investida desde 1994: após queda de mais de 30% desde maio/2013, volta a ser posição de destaque; modelo de “estilo de vida”, crédito próprio e crescimento sem perder rentabilidade.','Aumentou a posição até virar uma das maiores do Cougar.')
th('Dynamo','Carta 91/92 – BVMF',dy(91),'2016-12','B3SA3','comprada','BM&FBovespa (acionista desde 2011): infraestrutura de mercado dominante, ganhos com integração da clearing e fusão com a Cetip; competição e regulação vistas como mais benignas que o mercado temia.','Uma das maiores posições do fundo.')
th('Constellation','Carta dez/2017 (via Capital Aberto)','https://capitalaberto.com.br/empresas/2018/04/crise-boa-para-investir','2017-12','FLRY3','comprada','Empresas saíram mais eficientes da crise; projeção de PIB +2,7% e lucro das investidas +26% em 2018. Destaques de 2017: Fleury, CVC, B3 e Raia Drogasil.','Manteve as posições em Fleury, CVC, B3 e Raia.')
th('Constellation','Carta dez/2017 (via Capital Aberto)','https://capitalaberto.com.br/empresas/2018/04/crise-boa-para-investir','2017-12','CVCB3','comprada','CVC como uma das principais posições e destaque de 2017, apostando na recuperação do consumo.','Manteve a posição.')
T=pd.DataFrame(T); T.insert(0,'id',range(1,len(T)+1))
gest.to_csv('out/cartas_gestoras.csv',index=False); L.to_csv('out/cartas_links.csv',index=False); T.to_csv('out/cartas_teses.csv',index=False)
print(len(gest),len(L),len(T)); print(L.groupby('gestora').size()); print(gest[['gestora','fundos']].to_string())
