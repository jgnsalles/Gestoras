import pandas as pd, numpy as np, sys
W=sys.argv[1]
F=pd.read_pickle(W+'/funds.pkl')
EXN=r'INDEX|[ÍI]NDICE|IBOVESPA|IBRX|IBX|\bETF\b|PASSIV|EXTERIOR|BDR|GLOBAL|PETROBRAS|\bVALE\b|FGTS|MONO|S&P|ISHARES|SMALL CAP ATIVO INDEX|INDEXADO'
out={}
for y in (2014,2018):
    f=F.loc[y].copy()
    f['m_open']=(f.excl!='S')
    g=f.groupby('root')
    s=pd.DataFrame({'n':g.size(),'open':g.m_open.any(),'acoes':g.classe.apply(lambda x:(x=='Ações').any()),
        'excl_name':g.nome.apply(lambda x:x.fillna('').str.upper().str.contains(EXN,regex=True).any()),
        'members':g.apply(lambda x:set(x.index)),'cotst':g.COTST.sum()})
    r=f.reindex(s.index)
    s['PL']=r.PL; s['eq']=r['eq']; s['short']=r.short; s['ext']=r.ext; s['indfut']=r.indfut; s['fundw']=r.fundw
    s['gestor']=r.gestor; s['classe_root']=r.classe; s['nome_root']=r.nome
    # display name: biggest open member that's not root, else root
    def disp(x):
        x=x[x.excl!='S'] if (x.excl!='S').any() else x
        return x.sort_values('PL').nome.iloc[-1]
    s['nome']=g.apply(disp)
    out[y]=s
pd.to_pickle(out,W+'/strat.pkl')
