import pandas as pd, numpy as np, sys
W=sys.argv[1]
F=pd.read_pickle(W+'/funds.pkl'); S=pd.read_pickle(W+'/strat.pkl')
IDX=r'INDEX|[ÍI]NDICE|IBOVESPA|IBRX|IBX|\bETF\b|PASSIV|PETROBRAS|\bVALE\b|FGTS|MONO|S&P|ISHARES|INDEXADO|SMALL CAP INDEX'
LS=r'LONG SHORT|LONG AND SHORT|LONG-SHORT|L/S|EQUITY HEDGE|MARKET NEUTRAL'
LB=r'LONG BIAS|LONG-BIAS'
E={}
for y in (2014,2018):
    s=S[y].copy(); f=F.loc[y]
    names=lambda m: ' | '.join(f.reindex(list(m)).nome.dropna().str.upper())
    s['allnames']=s.members.apply(names)
    s['net']=s['eq']-s['short']
    # investors excluding feeders inside the strategy
    nfeed=s.n-1
    s['cot']=s.cotst-nfeed
    s['idx']=s.allnames.str.contains(IDX,regex=True)
    s['ls']=s.allnames.str.contains(LS,regex=True)
    s['lb']=s.allnames.str.contains(LB,regex=True)
    s['tipo']=pd.Series(np.where(s.acoes,'Ações',np.where(s.classe_root=='Multimercado','Multimercado','X')),index=s.index)
    ok=s.tipo.isin(['Ações','Multimercado'])&~s.idx&~s.ls&(s.fundw<0.5)&(s.ext<0.4)&(s.PL>0)
    ok&=(s.tipo=='Ações')|s.lb|(s.net>=0.6)
    ok&=s.net>=0.3
    s['ok']=ok
    E[y]=s
# link across years by member overlap
a,b=E[2014],E[2018]
m14={c:r for r,mm in a.members.items() for c in mm}
f18=F.loc[2018].PL
pairs={}
for r18,mm in b.members.items():
    for c in mm:
        if c in m14:
            k=(m14[c],r18); pairs[k]=pairs.get(k,0)+(f18.get(c,0) or 0)+1
P=pd.DataFrame([(k[0],k[1],v+(1e13 if k[0]==k[1] else 0)) for k,v in pairs.items()],columns=['r14','r18','w'])
P=P.merge(a[['PL','ok','nome','gestor','tipo','net','short','cot']].add_suffix('_14'),left_on='r14',right_index=True)
P=P.merge(b[['PL','ok','nome','gestor','tipo','net','short','cot']].add_suffix('_18'),left_on='r18',right_index=True)
P=P[P.ok_14&P.ok_18&(P[['cot_14','cot_18']].max(axis=1)>=100)&((P.net_14>=0.5)|(P.net_18>=0.5))]
# if many-to-one, keep biggest pairing
P=P.sort_values('w',ascending=False)
used14,used18,keep=set(),set(),[]
for i,r in P.iterrows():
    if r.r14 in used14 or r.r18 in used18: continue
    used14.add(r.r14); used18.add(r.r18); keep.append(i)
P=P.loc[keep]
P['rk14']=P.PL_14.rank(ascending=False).astype(int); P['rk18']=P.PL_18.rank(ascending=False).astype(int)
# also rank vs whole eligible universe (incl. funds that did not survive)
P.to_pickle(W+'/pairs.pkl'); pd.to_pickle(E,W+'/elig.pkl')
T=P[(P.rk14<=30)|(P.rk18<=30)].copy()
pd.set_option('display.width',300); pd.set_option('display.max_colwidth',60)
T['PL14']=(T.PL_14/1e6).round(0); T['PL18']=(T.PL_18/1e6).round(0)
print(len(T)); print(T.sort_values('PL_18',ascending=False)[['nome_18','gestor_18','tipo_18','PL14','PL18','rk14','rk18','net_14','net_18','short_18','cot_18']].round(2).to_string())
print('\nTop30 2014 elegíveis que NÃO sobreviveram:'); x=a[a.ok&(a.cot>=100)&~a.index.isin(P.r14)].sort_values('PL',ascending=False).head(15); print(x[['nome','gestor','PL']].to_string())
print('\nTop30 2018 elegíveis sem histórico 2014:'); x=b[b.ok&(b.cot>=100)&~b.index.isin(P.r18)].sort_values('PL',ascending=False).head(15); print(x[['nome','gestor','PL']].to_string())
