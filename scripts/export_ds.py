import pandas as pd, numpy as np, json, sys, re
W,O=sys.argv[1],sys.argv[2]
ST=json.load(open(W+'/members.json'))
# 2º filtro: fora fundos com alguma posição acima de 50% do PL em algum mês de 2014-2018
C=pd.read_csv(W+'/concentr.csv',index_col='id'); EXCL=set(C[C.top1max>0.50].index)
# 3º filtro: no máximo 2 fundos por gestora (sai JGP Equity Multimercado e Oceana Valor)
EXCL|={14,18}
print('excluidos',sorted(EXCL)); ST=[s for s in ST if s['id'] not in EXCL]; S=pd.read_pickle(W+'/serie.pkl'); P=pd.read_pickle(W+'/pos.pkl'); S=S[~S.id.isin(EXCL)]; P=P[~P.id.isin(EXCL)]
ret=pd.read_pickle(W+'/ret.pkl'); b3=pd.read_pickle(W+'/b3_monthly.pkl'); names=pd.read_pickle(W+'/names.pkl')
PAIRS=pd.read_pickle(W+'/pairs.pkl').set_index('r18')
def sn(n):
    n=re.sub(r'(-\s*)?FUNDO DE INVESTIMENTO(S)? EM COTAS DE FUNDOS DE INVESTIMENTO( EM| DE)?( A[CÇ][OÕ]ES)?|(-\s*)?FUNDO DE INVESTIMENTO(S)?( EM| DE)?( A[CÇ][OÕ]ES| MULTIMERCADO)?|BDR N[IÍ]VEL\s+I|INVESTIMENTO NO EXTERIOR','',str(n))
    return re.sub(r'\s+',' ',n).strip(' -').title().replace('Jgp','JGP').replace('Spx','SPX').replace('Am ','AM ').replace('Stk','STK')
F=[]
for s in ST:
    nm='Neo Future' if s['r18']=='29.994.412/0001-76' else sn(s['nome'])
    if s['r18']=='09.271.730/0001-00': nm='JGP Equity (Multimercado)'
    if s['r18']=='13.136.966/0001-00': nm='JGP Equity Explorer (Ações)'
    g=re.sub(r'\s*(-\s*)?(GEST(Ã|A)O|GESTORA|ADMINISTRA|INVESTIMENTOS|ASSET MANAGEMENT|CAPITAL LTDA|LTDA|S\.A\.|S/A|PARTNERS).*$','',str(s['gestor'])).title()
    p=PAIRS.loc[s['r18']]
    F.append(dict(id=s['id'],fundo=nm,gestora=g,rank_2014=s['rk14'],rank_2018=s['rk18'],pl_2014_mi=round(p.PL_14/1e6),pl_2018_mi=round(p.PL_18/1e6),cnpj_master_2018=s['r18']))
pd.DataFrame(F).to_csv(O+'/fundos.csv',index=False)
S2=S.copy(); S2['PL_mi']=(S2.PL/1e6).round(1)
for c in ['ret_fundo','ret_ibov','exp_long','exp_short','ret_acoes_contrib']: S2[c]=S2[c].round(5)
S2=S2.sort_values(['id','ym'])
prevPL=S2.groupby('id').PL.shift(1); prevM=S2.groupby('id').master.shift(1)
S2['fluxo_mi']=((S2.PL-prevPL*(1+S2.ret_fundo))/1e6).where((S2.master==prevM)&S2.ret_fundo.notna()).round(1)
S2[['id','ym','PL_mi','ret_fundo','ret_ibov','exp_long','exp_short','n_acoes','ret_acoes_contrib','fluxo_mi']].to_csv(O+'/serie_mensal.csv',index=False)
# --- agrupa ON/PN/units e tickers renomeados por empresa ---
ALIAS={'KROT':'COGN','BVMF':'B3SA','RUMO':'RAIL','ESTC':'YDUQ','VVAR':'VIIA','NATU':'NTCO','ABRE':'SEDU','GOAU':'GOAU'}
root=lambda t: ALIAS.get(t[:4],t[:4]) if re.match(r'^[A-Z][A-Z0-9]{3}\d{1,2}$',t) else t
Pall=pd.read_pickle(W+'/pos.pkl')
held=Pall.assign(a=Pall.peso.abs()).groupby('tk').a.sum()
rep={}
for t in held.index:
    r0=root(t); 
    if r0 not in rep or held[t]>held[rep[r0]]: rep[r0]=t
REP={t:rep[root(t)] for t in held.index}
json.dump(REP,open(W+'/rep.json','w'))
P=P.assign(tk=P.tk.map(REP).fillna(P.tk))
P=P.groupby(['id','ym','tk'],as_index=False).agg(peso=('peso','sum'),contrib=('contrib',lambda x: x.sum(min_count=1)),trade_pct_pl=('trade_pct_pl',lambda x: x.sum(min_count=1)))
P2=P[['id','ym','tk']].copy(); P2['peso']=P.peso.round(5); P2['contrib']=P.contrib.round(6); P2['compra_venda_pct_pl']=P.trade_pct_pl.round(5)
P2[P2.id<=17].to_csv(O+'/posicoes_1.csv',index=False); P2[P2.id>17].to_csv(O+'/posicoes_2.csv',index=False)
months=sorted(S.ym.unique()); tks=sorted(P.tk.unique())
# retorno da empresa: média dos tickers ponderada pelo peso agregado nos fundos no mês anterior
W_t=Pall.assign(a=Pall.peso.abs()).groupby(['ym','tk']).a.sum().unstack().reindex(months).shift(1)
r=pd.DataFrame(index=months,columns=tks,dtype=float)
for rp in tks:
    members=[t for t,v in REP.items() if v==rp and t in ret.columns] or ([rp] if rp in ret.columns else [])
    if not members: continue
    R_=ret.reindex(index=months,columns=members); w=W_t.reindex(columns=members).fillna(0).where(R_.notna(),0)
    w=w.where(w.sum(axis=1)>0, R_.notna().astype(float))
    r[rp]=(R_.fillna(0)*w).sum(axis=1)/w.sum(axis=1).replace(0,np.nan)
idx=(1+r.fillna(0)).cumprod()*100
idx=idx.where(r.notna())
pr=b3.reindex(index=months,columns=tks)
L=pd.DataFrame({'ret_total':r.stack(future_stack=True).round(5),'indice_ret_total':idx.stack(future_stack=True).round(2),'preco_b3':pr.stack(future_stack=True).round(2)}).dropna(how='all').reset_index()
L.columns=['ym','tk','ret_total','indice_ret_total','preco_b3']; L.to_csv(O+'/precos.csv',index=False)
pd.DataFrame({'tk':tks,'empresa':[names.get(t,names.get(t[:-1],'')) for t in tks]}).to_csv(O+'/acoes.csv',index=False)
import os; [print(f, os.path.getsize(O+'/'+f)//1024,'KB') for f in sorted(os.listdir(O))]
