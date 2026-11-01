import pandas as pd, json, re, sys
W=sys.argv[1]
S=pd.read_pickle(W+'/strat.pkl'); P=pd.read_pickle(W+'/pairs.pkl')
import importlib.util
EXC=r'ITA[UÚ]|OPPORTUNITY|\bXP\b|BRADESCO|BRAM|SANTANDER|AZ QUEST|BTG|SAFRA|\bBB\b|CAIXA|VERDE|RPS|ARX|PAC[IÍ]FICO|VINCI|GENIAL|PLURAL'
x=P[(P.rk14<=50)|(P.rk18<=50)].copy()
x=x[~(x.gestor_18.fillna('')+' '+x.nome_18.fillna('')+' '+x.nome_14.fillna('')).str.upper().str.contains(EXC,regex=True)].sort_values('rk18')
out=[]
for i,(_,r) in enumerate(x.iterrows()):
    mem=set(S[2014].loc[r.r14,'members'])|set(S[2018].loc[r.r18,'members'])
    out.append(dict(id=i+1,r14=r.r14,r18=r.r18,nome=r.nome_18,gestor=r.gestor_18,rk14=int(r.rk14),rk18=int(r.rk18),members=sorted(mem)))
json.dump(out,open(W+'/members.json','w'),ensure_ascii=False,indent=0)
print(len(out), sum(len(o['members']) for o in out))
