import pandas as pd, numpy as np, sys, re
W,OUT=sys.argv[1],sys.argv[2]
P=pd.read_pickle(W+'/pairs.pkl'); E=pd.read_pickle(W+'/elig.pkl')
T=P[(P.rk14<=30)|(P.rk18<=30)].copy()
b=E[2018]; a=E[2014]
T['lb']=T.r18.map(b.lb)|T.r14.map(a.lb)
T['short_14']=T.r14.map(a.short)
T['estilo']=np.where((T.tipo_18=='Multimercado')|T.lb|(T[['short_14','short_18']].max(axis=1)>0.1)|(T[['net_14','net_18']].min(axis=1)<0.65),'Long bias','Long only')
def short_name(n):
    n=re.sub(r'(-\s*)?FUNDO DE INVESTIMENTO(S)?( EM| DE)?( A[CÇ][OÕ]ES| MULTIMERCADO)?|BDR N[IÍ]VEL\s+I|INVESTIMENTO NO EXTERIOR|AÇÕES INSTITUCIONAL','',str(n))
    n=re.sub(r'\s*-\s*$','',re.sub(r'\s+',' ',n)).strip(' -'); return n.title().replace('Ações','Ações') or n
T['Fundo']=T.nome_18.apply(short_name)
T['Gestora']=T.gestor_18.str.replace(r'\s*(-\s*)?(GEST(Ã|A)O|GESTORA|ADMINISTRA|INVESTIMENTOS LTDA|ASSET MANAGEMENT|CAPITAL LTDA|LTDA|S\.A\.|S/A).*$','',regex=True).str.title()
notes={}
for i,r in T.iterrows():
    n=[]
    if r.PL_14<50e6: n.append('Pequeno em 2014, cresceu muito até 2018')
    if r.PL_18<0.5*r.PL_14: n.append('Encolheu bastante até 2018')
    if 'PREVID' in str(r.nome_18).upper() or 'FLEXPREV' in str(r.nome_18).upper(): n.append('Fundo de previdência')
    if max(r.short_14,r.short_18)>0.4: n.append('Muita posição vendida (aluguel); perfil mais long-short')
    if r.r14!=r.r18: n.append('Mudou de estrutura/CNPJ master no período')
    notes[i]='; '.join(n)
T['Obs']=pd.Series(notes)
T=T.sort_values(['rk18'])
out=pd.DataFrame({'Rank 2014':T.rk14,'Rank 2018':T.rk18,'Fundo / estratégia':T.Fundo,'Gestora':T.Gestora,'Estilo':T.estilo,
 'Classe CVM':T.tipo_18,'PL dez/2014 (R$ mi)':(T.PL_14/1e6).round(0),'PL dez/2018 (R$ mi)':(T.PL_18/1e6).round(0),
 'Variação PL':(T.PL_18/T.PL_14-1),'Expos. líquida ações 2014':T.net_14.round(2),'Expos. líquida ações 2018':T.net_18.round(2),
 'Top 30 em':np.where((T.rk14<=30)&(T.rk18<=30),'2014 e 2018',np.where(T.rk14<=30,'Só 2014','Só 2018')),
 'CNPJ master 2014':T.r14,'CNPJ master 2018':T.r18,'Nome CVM 2018':T.nome_18,'Observações':T.Obs})
# non survivors / newcomers
fa=a[a.ok&(a.cot>=100)&~a.index.isin(P.r14)&a.nome.notna()].sort_values('PL',ascending=False).head(15)
fb=b[b.ok&(b.cot>=100)&~b.index.isin(P.r18)&b.nome.notna()].sort_values('PL',ascending=False).head(15)
fora=pd.concat([pd.DataFrame({'Motivo':'Grande em 2014, mas não chegou a 2018','Fundo':fa.nome,'Gestora':fa.gestor,'PL (R$ mi)':(fa.PL/1e6).round(0),'Ano':2014}),
                pd.DataFrame({'Motivo':'Grande em 2018, mas não existia em 2014','Fundo':fb.nome,'Gestora':fb.gestor,'PL (R$ mi)':(fb.PL/1e6).round(0),'Ano':2018})]).reset_index().rename(columns={'root':'CNPJ'})
met=pd.DataFrame({'Metodologia':[
'Fonte: CVM Dados Abertos — Informe Diário (PL do último dia útil de dez/2014 e dez/2018), Composição de Carteira (CDA de dez/2014 e dez/2018) e Cadastro histórico de fundos.',
'Estrutura master/feeder consolidada: um fundo que tem 70% ou mais do PL em cotas de outro fundo é tratado como feeder; o PL da estratégia é o PL do master final (evita dupla contagem).',
'Universo: estratégias com fundo classe CVM "Ações", ou "Multimercado" com exposição líquida a ações ≥ 60% ou "Long Bias" no nome.',
'Exposição a ações calculada com look-through nas cotas de fundos: ações à vista + emprestadas + termo comprado, menos ações tomadas em aluguel (vendidas). Futuros de índice não entram (CVM não informa o nocional).',
'Excluídos: fundos de índice/ETF/passivos, FMP-FGTS, fundos de uma ação só (Petrobras, Vale), long-short/equity hedge/market neutral (pelo nome), fundos de fundos (≥50% em cotas de terceiros), fundos com ≥40% no exterior, estruturas com menos de 100 cotistas nos dois anos (veículos exclusivos/família/fundação).',
'"Atravessou o período": a estratégia existe em dez/2014 e em dez/2018 (mesmo CNPJ ou feeders em comum). Exige exposição líquida ≥ 50% em pelo menos um dos anos.',
'Ranking: posição por PL entre as estratégias sobreviventes em cada ano. A lista é a união do Top 30 de 2014 com o Top 30 de 2018.',
'Estilo "Long bias": multimercado, "Long Bias" no nome, posição vendida > 10% do PL, ou exposição líquida < 65% em algum ano. Os demais são "Long only".']})
with pd.ExcelWriter(OUT,engine='openpyxl') as x:
    out.to_excel(x,sheet_name='Ranking',index=False); fora.to_excel(x,sheet_name='Fora da lista',index=False); met.to_excel(x,sheet_name='Metodologia',index=False)
    ws=x.sheets['Ranking']
    for col,wd in zip('ABCDEFGHIJKLMNOP',[9,9,42,28,11,13,12,12,11,11,11,12,20,20,60,50]): ws.column_dimensions[col].width=wd
    for c in ws['I'][1:]: c.number_format='0%'
    ws.freeze_panes='C2'
    x.sheets['Fora da lista'].column_dimensions['B'].width=40; x.sheets['Fora da lista'].column_dimensions['C'].width=70; x.sheets['Fora da lista'].column_dimensions['D'].width=50
    x.sheets['Metodologia'].column_dimensions['A'].width=160
pd.set_option('display.width',250)
print(out[['Rank 2014','Rank 2018','Fundo / estratégia','Gestora','Estilo','PL dez/2014 (R$ mi)','PL dez/2018 (R$ mi)','Observações']].to_string(index=False))
