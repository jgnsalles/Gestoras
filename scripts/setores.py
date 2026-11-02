import openpyxl, glob, pandas as pd, json, re
f=glob.glob('web/setor/*.xlsx')[0]; ws=openpyxl.load_workbook(f,read_only=True).active
setor=sub=seg=None; M={}
for r in ws.iter_rows(min_row=9,values_only=True):
    a,b,c,d=r[:4]
    if a and str(a).strip() and not str(a).startswith('(') : setor=str(a).strip()
    if b and str(b).strip(): sub=str(b).strip()
    if c and not d: seg=str(c).strip()
    if d and str(d).strip() and len(str(d).strip())==4: M[str(d).strip()]=(setor,sub,seg)
MAN={'CTIP':('Financeiro','Serviços Financeiros Diversos','Serviços Financeiros Diversos'),'BVMF':('Financeiro','Serviços Financeiros Diversos','Serviços Financeiros Diversos'),
'KROT':('Consumo Cíclico','Diversos','Serviços Educacionais'),'ESTC':('Consumo Cíclico','Diversos','Serviços Educacionais'),'SEDU':('Consumo Cíclico','Diversos','Serviços Educacionais'),'ABRE':('Consumo Cíclico','Diversos','Serviços Educacionais'),'AEDU':('Consumo Cíclico','Diversos','Serviços Educacionais'),
'FIBR':('Materiais Básicos','Madeira e Papel','Papel e Celulose'),'HGTX':('Consumo Cíclico','Tecidos, Vestuário e Calçados','Vestuário'),'RLOG':('Bens Industriais','Transporte','Transporte Ferroviário'),'RUMO':('Bens Industriais','Transporte','Transporte Ferroviário'),'ALLL':('Bens Industriais','Transporte','Transporte Ferroviário'),
'SMLS':('Consumo Cíclico','Diversos','Programas de Fidelização'),'LAME':('Consumo Cíclico','Comércio','Produtos Diversos'),'BTOW':('Consumo Cíclico','Comércio','Produtos Diversos'),'GNDI':('Saúde','Serv.Méd.Hospit..Análises e Diagnósticos','Serv.Méd.Hospit..Análises e Diagnósticos'),
'SULA':('Financeiro','Previdência e Seguros','Seguradoras'),'CESP':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'ELPL':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'TPIS':('Bens Industriais','Transporte','Exploração de Rodovias'),
'MAGG':('Materiais Básicos','Mineração','Minerais Não Metálicos'),'SSBR':('Financeiro','Exploração de Imóveis','Exploração de Imóveis'),'BRML':('Financeiro','Exploração de Imóveis','Exploração de Imóveis'),'ALSC':('Financeiro','Exploração de Imóveis','Exploração de Imóveis'),'IGTA':('Financeiro','Exploração de Imóveis','Exploração de Imóveis'),'BRPR':('Financeiro','Exploração de Imóveis','Exploração de Imóveis'),
'DTEX':('Materiais Básicos','Madeira e Papel','Madeira'),'TIMP':('Comunicações','Telecomunicações','Telecomunicações'),'QGEP':('Petróleo, Gás e Biocombustíveis','Petróleo, Gás e Biocombustíveis','Exploração, Refino e Distribuição'),'BRDT':('Petróleo, Gás e Biocombustíveis','Petróleo, Gás e Biocombustíveis','Exploração, Refino e Distribuição'),
'CIEL':('Financeiro','Serviços Financeiros Diversos','Serviços Financeiros Diversos'),'VVAR':('Consumo Cíclico','Comércio','Eletrodomésticos'),'NATU':('Consumo não Cíclico','Produtos de Uso Pessoal e de Limpeza','Produtos de Uso Pessoal'),'BEMA':('Tecnologia da Informação','Computadores e Equipamentos','Computadores e Equipamentos'),
'LLIS':('Consumo Cíclico','Comércio','Tecidos, Vestuário e Calçados'),'CZLT':('Petróleo, Gás e Biocombustíveis','Petróleo, Gás e Biocombustíveis','Exploração, Refino e Distribuição'),'DAGB':('Consumo Cíclico','Comércio','Produtos Diversos'),'BBRK':('Financeiro','Exploração de Imóveis','Intermediação Imobiliária'),
'ELET':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'PCAR':('Consumo não Cíclico','Comércio e Distribuição','Alimentos'),'BRFS':('Consumo não Cíclico','Alimentos Processados','Carnes e Derivados'),'EMBR':('Bens Industriais','Material de Transporte','Material Aeronáutico e de Defesa'),
'CCRO':('Bens Industriais','Transporte','Exploração de Rodovias'),'ARZZ':('Consumo Cíclico','Tecidos, Vestuário e Calçados','Calçados'),'TRPL':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'SUZB':('Materiais Básicos','Madeira e Papel','Papel e Celulose'),'VALE':('Materiais Básicos','Mineração','Minerais Metálicos'),
'ENBR':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'JBSS':('Consumo não Cíclico','Alimentos Processados','Carnes e Derivados'),'GUAR':('Consumo Cíclico','Comércio','Tecidos, Vestuário e Calçados'),'BBTG':('Financeiro','Intermediários Financeiros','Bancos'),'SANB':('Financeiro','Intermediários Financeiros','Bancos'),
'LINX':('Tecnologia da Informação','Programas e Serviços','Programas e Serviços'),'SNSL':('Tecnologia da Informação','Programas e Serviços','Programas e Serviços'),'ARTR':('Bens Industriais','Transporte','Exploração de Rodovias'),'PARC':('Financeiro','Previdência e Seguros','Corretoras de Seguros'),'CELP':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'CRUZ':('Consumo não Cíclico','Fumo','Cigarros e Fumo'),'TEMP':('Saúde','Serv.Méd.Hospit..Análises e Diagnósticos','Serv.Méd.Hospit..Análises e Diagnósticos'),'BIDI':('Financeiro','Intermediários Financeiros','Bancos'),'TIET':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'SMLE':('Consumo Cíclico','Diversos','Programas de Fidelização'),'CTAX':('Bens Industriais','Serviços','Serviços Diversos'),'MPLU':('Consumo Cíclico','Diversos','Programas de Fidelização'),'GETI':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'TBLE':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'LCAM':('Consumo Cíclico','Diversos','Aluguel de carros'),'IMCH':('Consumo Cíclico','Hoteis e Restaurantes','Restaurante e Similares'),'BPHA':('Saúde','Comércio e Distribuição','Medicamentos e Outros Produtos'),'OMGE':('Utilidade Pública','Energia Elétrica','Energia Elétrica'),'MLFT':('Consumo não Cíclico','Comércio e Distribuição','Alimentos'),'TERM':('Bens Industriais','Construção e Engenharia','Construção Pesada'),'CCPR':('Consumo não Cíclico','Agropecuária','Agricultura'),'EBTP':('Comunicações','Telecomunicações','Telecomunicações'),'VAGR':('Consumo não Cíclico','Agropecuária','Agricultura'),'BOVA':('ETF de índice','ETF de índice','ETF'),'BOVV':('ETF de índice','ETF de índice','ETF'),'SMAL':('ETF de índice','ETF de índice','ETF'),'PIBB':('ETF de índice','ETF de índice','ETF'),'BRAX':('ETF de índice','ETF de índice','ETF'),'ECOO':('ETF de índice','ETF de índice','ETF'),'DIVO':('ETF de índice','ETF de índice','ETF')}
for k,v in MAN.items(): M.setdefault(k,v)
REP=json.load(open('work/rep.json'))
P=pd.concat([pd.read_csv('out/posicoes_1.csv'),pd.read_csv('out/posicoes_2.csv')])
tks=sorted(P.tk.unique()); out=[]
for t in tks:
    s=M.get(t[:4]) or M.get(t[:4].replace('3','')) 
    out.append(dict(tk=t,setor=(s[0] if s else 'Outros/não classificado'),subsetor=(s[1] if s else '')))
O=pd.DataFrame(out)
w=P[(P.ym>='2014-01')&(P.ym<='2018-12')&(P.peso>0)].groupby('tk').peso.sum()
O['w']=O.tk.map(w).fillna(0)
print('peso sem setor',round(O[O.setor.str.startswith('Outros')].w.sum()/O.w.sum(),4))
print(O[O.setor.str.startswith('Outros')].sort_values('w',ascending=False).head(25)[['tk','w']].to_string())
print(O.groupby('setor').w.sum().sort_values(ascending=False).round(1).to_string())
nm=pd.read_csv('out/acoes.csv').set_index('tk').empresa
A=pd.DataFrame({'tk':tks,'empresa':[nm.get(t,'') for t in tks]}).merge(O[['tk','setor','subsetor']],on='tk')
A.to_csv('out/acoes.csv',index=False)
