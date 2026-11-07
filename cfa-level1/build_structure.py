import re,json,sys
MODS={
1:("Quantitative Methods","Métodos Quantitativos",["Taxas & Retornos","Valor do Dinheiro no Tempo","Probabilidade & Estatística","Distribuição e Forma","Estatística Aplicada"]),
2:("Economics","Economia",["Microeconomia","Macroeconomia & Ciclos Econômicos","Geopolítica & Comércio Global"]),
3:("Corporate Issuers","Emissores Corporativos",["Estruturas Empresariais & Governança Corporativa","Gestão Financeira de Curto e Longo Prazo","Decisões de Investimentos e Modelos de Negócio"]),
4:("Financial Statement Analysis","Análise de Demonstrações Financeiras",["Introdução à Análise das Demonstrações Financeiras","Análise da Demonstração de Resultado","Análise de Balanços","Análise de Fluxos de Caixa","Análise de Estoques","Análise de Ativos de Longo Prazo","Passivos de Longo Prazo e Equity","Análise de Impostos","Qualidade dos Relatórios Financeiros","Técnicas de Análise Financeira","Introdução à Modelagem de Demonstrações Financeiras"]),
5:("Equity Investments","Renda Variável",["Estrutura do Mercado Financeiro","Conceitos de Renda Variável","Índices do Mercado Financeiro","Análise Setorial & Empresarial","Avaliação de Ações"]),
6:("Fixed Income","Renda Fixa",["Renda Fixa: Conceitos & Produtos","Precificação & Retornos na Renda Fixa","Riscos na Renda Fixa – Parte I","Riscos na Renda Fixa – Parte II"]),
7:("Derivatives","Derivativos",["Introdução aos Derivativos","Compromissos Firmes: Termo, Futuro & Swap","Reivindicações Contingentes","Paridades & Precificação de Opções"]),
8:("Alternative Investments","Investimentos Alternativos",["Principais Conceitos","Categorias de Ativos","Análise de Performance & Digital Assets"]),
9:("Portfolio Management","Gestão de Portfólios",["Risco, Retorno e Dominância","Teoria Moderna de Carteiras","Gestão de Performance & Gestão de Risco","Construção de Portfolios","Finanças Comportamentais"]),
10:("Ethical and Professional Standards","Ética e Padrões Profissionais",["Princípios Éticos do CFA","Processos Éticos do CFA (Standards)"]),
}
CH={1:[4,23,52,76,102],2:[4,47,68],3:[4,28,48],4:[4,19,51,70,90,101,112,130,138,151,177],5:[4,22,32,47,71],6:[4,27,43,58],7:[4,16,26,40],8:[4,14,40],9:[4,15,35,57,75],10:[4,13]}
# manual topic breakpoints (page -> name) override header-based grouping inside these ranges
OVR={
 (1,'merge'):{"Médias Simples (Aritmética)":"Média Simples (Aritmética)","CMPC Custo Médio Ponderado de":"CMPC Custo Médio Ponderado de Capital","Lei dos Grandes Números e Teorema Central do Limite":"Estimação e Inferência","Relação TIR x VPL":"TIR Taxa Interna de Retorno","Relação VPL x TMA":"TIR Taxa Interna de Retorno","Testes Paramétricos e Não Paramétricos":"Testes Paramétricos e Não Paramétricos","Testes Paramétricos":"Testes Paramétricos e Não Paramétricos","Testes Não Paramétricos":"Testes Paramétricos e Não Paramétricos","Média Ponderada":"Médias: Ponderada, Geométrica e Harmônica","Média Geométrica":"Médias: Ponderada, Geométrica e Harmônica","Média Harmônica":"Médias: Ponderada, Geométrica e Harmônica","Tipos de Médias":"Médias: Ponderada, Geométrica e Harmônica","Retorno do Período de Retenção":"HPR, TMA e WACC","Taxa Mínima de Atratividade":"HPR, TMA e WACC","CMPC Custo Médio Ponderado de Capital":"HPR, TMA e WACC","Taxa de Retorno Ponderada pelo Tempo":"TWRR & MWRR","Taxa de Retorno Ponderada pelo Dinheiro":"TWRR & MWRR","Diagrama em Árvore":"Probabilidade, Árvores e Bayes","Probabilidade":"Probabilidade, Árvores e Bayes","Fórmula de Bayes":"Probabilidade, Árvores e Bayes","Modelo de Árvore Binomial":"Probabilidade, Árvores e Bayes","Estatística":"Medidas de Posição Central","Matemática Financeira":"Juros Simples","Regimes de Capitalização: Juros Simples":"Juros Simples","Regimes de Capitalização: Juros Compostos":"Juros Compostos","Regimes de Capitalização: Juros Contínuo":"Juros Contínuos e Perpetuidade","Perpetuidade com crescimento constante":"Juros Contínuos e Perpetuidade","VPL Valor Presente Líquido":"VPL & TIR","TIR Taxa Interna de Retorno":"VPL & TIR","TIRM Taxa Interna de Retorno Modificada":"TIRM (MIRR)"},
}
BREAK={
 2:{5:"Oferta e Demanda",15:"Elasticidade",24:"Receita, Lucro e Custos",31:"Economias de Escala",33:"Estruturas de Mercado",45:"Concentração de Mercado",48:"PIB",50:"Inflação",52:"Política Monetária",56:"Política Fiscal",59:"Ciclos Econômicos",63:"Curva de Juros (ETTJ) e Curva de Phillips",69:"Geopolítica e Cooperação",71:"Globalização e Organizações Internacionais",73:"Comportamento dos Países e Instrumentos",75:"Riscos Geopolíticos",77:"Comércio Internacional: Tarifas, Cotas e Blocos",82:"Câmbio: Cotações e PPP",88:"Câmbio: Balança, Restrições e Forwards"},
 4:{52:"Estrutura do Balanço",55:"Ativos e Passivos Circulantes",58:"Impostos Diferidos e PL",60:"Intangíveis e Goodwill",63:"Instrumentos Financeiros",66:"Passivos de Longo Prazo e Fiscais Diferidos",69:"Índices do Balanço",
    71:"Ligação entre Demonstrativos",77:"Métodos Direto e Indireto",80:"Investimento, Financiamento e IFRS x US GAAP",83:"Análises Avançadas e FCF",88:"Índices de Fluxo de Caixa",
    91:"Valoração de Estoques",94:"Inflação, Deflação e Write-Downs",99:"Índices e Divulgação",
    102:"Ativos não Circulantes",105:"Ativos Intangíveis",107:"Impairment e Derecognition",109:"Apresentação e Divulgação",
    113:"Leases: Conceitos",116:"Lessee Accounting (IFRS e US GAAP)",121:"Lessor Accounting",123:"Planos de Compensação",128:"Apresentação e Divulgação",
    131:"Lucro Contábil x Renda Tributável",134:"DTA x DTL e IR Corporativo",
    139:"Qualidade: Conceitos e Espectro",141:"Contabilidade Viesada e Earnings Management",144:"Disciplina e Detecção de Problemas",147:"Impactos nas Demonstrações e Sinais de Alerta",
    152:"Processo e Ferramentas de Análise",155:"Análise por Índices e Common-Size",161:"Gráficos e Regressão",163:"Índices de Atividade",166:"Índices de Liquidez",168:"Índices de Solvência",171:"Índices de Rentabilidade",174:"DuPont e Índices Setoriais",
    178:"Construção do Modelo e Receitas",181:"Projeção de Custos e Despesas",183:"Lucro por Segmento e Imposto",185:"Demonstrações Pro Forma",187:"Capex, Capital de Giro e FCF",190:"Inputs de Valuation",191:"Finanças Comportamentais nas Projeções",194:"Inflação, Deflação e Receita Normalizada"},
 3:{29:"Ciclo Operacional e de Caixa",33:"Fontes e Custo de Liquidez",35:"Gestão de Liquidez e Capital de Giro",38:"Estrutura de Capital: Determinantes",42:"Modigliani-Miller",46:"Estrutura Ótima e Pecking Order",49:"Tipos de Investimento de Capital",52:"Alocação de Capital e Ferramentas",55:"Princípios, Armadilhas e Vieses",57:"Opções Reais",59:"Modelos de Negócio: Oferta e Precificação",64:"Proposta e Cadeia de Valor",66:"Modelos Convencionais e Plataformas"},
 5:{31:"Fontes de Retorno",72:"Conceitos de Valuation",76:"Modelos de Múltiplos",82:"Modelos de Valor Presente (FCFF e DDM)",87:"Asset-based Valuation"},
 6:{5:"Conceitos de Renda Fixa",12:"Títulos Governamentais",16:"Títulos Privados",20:"Securitização",28:"Precificação e YTM",30:"Full Price, Flat Price e Accrued Interest",32:"Relações de Preço e Matrix Pricing",34:"Fixed-Rate Notes: Yields e Spreads",38:"Floating-Rate Notes e Money Market",41:"Forward Rates e WAC",43:"Risco de Mercado",47:"Risco de Crédito",54:"Riscos Legais, Operacionais e de Liquidez",59:"Fontes de Retorno e Duration",64:"Limitações da Duration e Horizonte",66:"Duration Baseada em Yield",72:"Convexidade",78:"Medidas Baseadas na Curva"},
 8:{5:"Conceito e Real Assets",7:"Métodos de Investimento",10:"Estruturas e Mecanismos (Hurdle, HWM, Waterfall)",14:"Private Equity",20:"Private Debt",23:"Real Estate",28:"Infraestrutura",31:"Land e Commodities",35:"Hedge Funds",41:"Mensuração de Desempenho (DPI, TVPI)",45:"Precificação e Fee Arrangements",47:"Exercícios",49:"Ativos Digitais e DLT",53:"Tipos de Ativos Digitais",59:"Riscos e Diversificação"},
 9:{5:"Princípio da Dominância",7:"Risco Total e Sistêmico",10:"Outros Riscos (Crédito, Legal, Modelo, Operacional)",16:"Utilidade e Tolerância ao Risco",20:"Fronteira Eficiente de Markowitz",25:"CAL / CML",27:"SML",30:"Modelos Multifatoriais (Fama-French, Carhart, APT)",34:"Mercado Eficiente (EMH)",36:"Medidas de Performance",42:"Framework de Gestão de Risco",48:"Orçamento e Métricas de Risco (VaR, CVaR)",53:"Modificação de Risco",58:"Gestão de Portfolios: Overview",61:"Asset Management e Fundos",65:"IPS: Objetivos e Restrições",69:"Construção da Carteira e SAA",73:"Princípios de Construção e ESG",76:"Heurísticas e Vieses",78:"Vieses Cognitivos",82:"Vieses Emocionais",86:"Tabelas Resumo"},
 10:{5:"Ética e Confiança na Profissão",9:"Código de Ética e GIPS",14:"Guidance e Programa de Conduta",16:"Tabela dos Padrões",17:"I – Profissionalismo",22:"II – Integridade dos Mercados",25:"III – Deveres com Clientes",30:"IV – Deveres com Empregadores",34:"V – Análise e Recomendações",37:"VI – Conflitos de Interesse",41:"VII – Responsabilidades como Membro/Candidato"},
}
MERGE7={"Classificação das Opções":"Valor do Prêmio e Moneyness","Valor do Prêmio da Opção":"Valor do Prêmio e Moneyness","Paridade Put-Call Empresarial":"Paridade Put-Call","Variáveis e o relação do impacto nas opções":"Fatores e Gregas","Variáveis Gregas":"Fatores e Gregas","Derivativos":"O que são Derivativos","Principais Estratégias nos Derivativos":"Estratégias: Alavancagem, Hedge e Arbitragem","Compromissos Firmes":"Contrato a Termo","Replicação":"Paridade Put-Call","Modelo de Árvore Binomial":"Árvore Binomial"}
MERGE5={"Global Registered Shares (GRS)":"Depositary Receipts","Instruções de Validade e Compensação":"Ordens e Instruções de Negociação","Renda Variável":"Ações","Retorno dos Investidores":"Ações","Gestão de Índices: Rebalancear e Reconstruir":"Construção de Índices","Cálculos de Valor e Retornos de Índices":"Cálculos de Índices","Análise da Empresa: Passado e Presente":"Modelo de Negócio e Receita","Determinando o Modelo de Negócio":"Modelo de Negócio e Receita","Análise de Receita":"Modelo de Negócio e Receita","Investimentos de capital e Estrutura de capital":"Investimentos e Estrutura de Capital","Análise de empresas: Forecast":"Forecasting","Sistema Financeiro":"Sistema e Mercado Financeiro","Mercado Financeiro":"Sistema e Mercado Financeiro"}
MERGE4={"Escopo da Análise das Demonstrações":"Framework e Escopo da Análise","Framework":"Framework e Escopo da Análise","Fontes Regulamentadas de Informação":"Fontes de Informação","Outras Fontes de Informação":"Fontes de Informação","Mudanças em Estimativas Contábeis":"Mudanças Contábeis, Escopo e Câmbio","Mudanças no Escopo e em Taxas de Câmbio":"Mudanças Contábeis, Escopo e Câmbio","Análise Vertical e Horizontal":"Análise Vertical/Horizontal e Índices","Análise Vertical":"Análise Vertical/Horizontal e Índices","Índices do Income Statement":"Análise Vertical/Horizontal e Índices","Reconhecimento de Despesa":"Reconhecimento de Receita e Despesa","Reconhecimento de Receita":"Reconhecimento de Receita e Despesa"}
MERGE3={"Abertura de Capital":"IPO, SPAC e Fechamento de Capital","Fechamento de Capital":"IPO, SPAC e Fechamento de Capital","Formas de Captação de Recursos":"Captação e Direitos de Acionistas x Credores","Direitos dos Acionistas x Credores":"Captação e Direitos de Acionistas x Credores"}
MERGE10={}
MERGE={1:OVR[(1,'merge')],3:MERGE3,4:MERGE4,5:MERGE5,7:MERGE7}
def pages(m):
    t=open(f'txt/m{m}.txt').read().split('\f')
    out={}
    for i,p in enumerate(t):
        lines=[l.strip() for l in p.splitlines() if l.strip()]
        lines=[l for l in lines if l!='CFA – Level 1' and not re.fullmatch(r'\d+',l)]
        if not lines: continue
        h=re.split(r'\s{3,}',lines[0])[0].strip()
        s=re.split(r'\s{3,}',lines[1])[0].strip() if len(lines)>1 else ''
        if s.startswith('Neste modelo') or s.startswith('Dessa forma') or s.startswith('Se as taxas') or s=='Capita' or s=='CFA Level 1' or s=='INÍCIO' or s=='PRÍNCIPIO': s=''
        out[i+1]=(h,s)
    return out,len(t)
data=[]
for m,(en,pt,chn) in MODS.items():
    P,n=pages(m); npages=max(P)
    chs=CH[m]; mod={"id":m,"en":en,"pt":pt,"pdfPages":npages,"chapters":[]}
    for ci,start in enumerate(chs):
        end=(chs[ci+1]-1) if ci+1<len(chs) else npages
        topics=[]; cur=None
        for p in range(start,end+1):
            h,s=P.get(p,('',''))
            if p==start:
                continue
            name=None
            if m in BREAK and p in BREAK[m]: name=BREAK[m][p]
            elif m in BREAK and any(k<=p for k in BREAK[m] if start<k<=end) and m in (2,3,4,5,6,8,9,10) and not (m==3 and p<29) and not (m==9 and False):
                name=None  # continue current
            else:
                hh=h
                for _ in range(4): hh=MERGE.get(m,{}).get(hh,hh)
                name=hh if (cur is None or hh!=cur['name']) else None
            if name and (cur is None or name!=cur['name']):
                cur={"name":name,"start":p,"end":p,"slides":[]}; topics.append(cur)
            cur['end']=p
            sub=s or h
            cur['slides'].append([p,sub])
        # include chapter opener in first topic
        if topics: topics[0]['start']=start; topics[0]['slides'].insert(0,[start,"Abertura do capítulo"])
        mod["chapters"].append({"name":chn[ci],"start":start,"end":end,"topics":topics})
    data.append(mod)
# M10 standards: split standards I..VII as topics
for ch in data[9]['chapters'][1:]:
    pass
json.dump(data,open('structure.json','w'),ensure_ascii=False,indent=1)
for mod in data:
    print(f"M{mod['id']} {mod['en']}")
    for c in mod['chapters']:
        print(f"  [{c['start']}-{c['end']}] {c['name']}")
        for t in c['topics']: print(f"      {t['start']}-{t['end']} {t['name']}")
