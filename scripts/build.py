import pandas as pd, numpy as np, sys, re
R,W=sys.argv[1],sys.argv[2]
rd=lambda f: pd.read_csv(f,sep=';',encoding='latin1',dtype=str)
def at(df,ini,fim,date):
    m=(df[ini].fillna('0000')<=date)&((df[fim].isna())|(df[fim]>=date))
    return df[m].sort_values(ini).groupby('CNPJ_FUNDO').tail(1).set_index('CNPJ_FUNDO')
H=f'{R}/cad_fi_hist/cad_fi_hist_'
cls=rd(H+'classe.csv'); ges=rd(H+'gestor.csv'); exc=rd(H+'exclusivo.csv'); nom=rd(H+'denom_social.csv')
cad=rd(f'{R}/cad_fi.csv').drop_duplicates('CNPJ_FUNDO').set_index('CNPJ_FUNDO')
pl=pd.read_pickle(f'{W}/pl.pkl')
EQ_LONG=['Ações','Ações e outros TVM cedidos em empréstimo','Compras a termo a receber','Certificado ou recibo de depósito de valores mobiliários']
SHORT=['Obrigações por ações e outros TVM recebidos em empréstimo','Vendas a termo a receber']
res={}
for y in (2014,2018):
    D=f'{y}-12-31'
    P=pl[pl.ANO==y].set_index('CNPJ_FUNDO')
    cpl=pd.read_pickle(f'{W}/cda_PL_{y}.pkl').drop_duplicates('CNPJ_FUNDO',keep='last').set_index('CNPJ_FUNDO')
    plv=pd.to_numeric(cpl.VL_PATRIM_LIQ,errors='coerce')
    a=pd.concat([pd.read_pickle(f'{W}/cda_{b}_{y}.pkl') for b in ('BLC_4','BLC_8')])
    a['v']=pd.to_numeric(a.VL_MERC_POS_FINAL,errors='coerce').fillna(0)
    eq=a[a.TP_APLIC.isin(EQ_LONG)].groupby('CNPJ_FUNDO').v.sum()
    sh=a[a.TP_APLIC.isin(SHORT)].groupby('CNPJ_FUNDO').v.sum()
    indfut=a[a.TP_ATIVO.str.contains('Ibovespa|IBrX',na=False)&a.TP_APLIC.str.contains('vendidas',na=False)].groupby('CNPJ_FUNDO').size()
    ex7=pd.read_pickle(f'{W}/cda_BLC_7_{y}.pkl'); ex7['v']=pd.to_numeric(ex7.VL_MERC_POS_FINAL,errors='coerce').fillna(0)
    ext=ex7.groupby('CNPJ_FUNDO').v.sum()
    c=pd.read_pickle(f'{W}/cda_BLC_2_{y}.pkl'); c['v']=pd.to_numeric(c.VL_MERC_POS_FINAL,errors='coerce').fillna(0)
    c=c[c.v>0]
    etf=c[c.TP_ATIVO=='Fundos de Índice'].groupby('CNPJ_FUNDO').v.sum()
    c=c[c.CNPJ_FUNDO_COTA.notna()&(c.TP_ATIVO!='Fundos de Índice')]
    cot=c.groupby(['CNPJ_FUNDO','CNPJ_FUNDO_COTA']).v.sum().reset_index()
    cot['w']=cot.v/cot.CNPJ_FUNDO.map(plv)
    funds=plv.index
    def sh_(s): return (s.reindex(funds).fillna(0)/plv).clip(-5,5).fillna(0)
    d_eq=sh_(eq)+sh_(etf); d_sh=sh_(sh); d_ex=sh_(ext)
    L_eq,L_sh,L_ex=d_eq.copy(),d_sh.copy(),d_ex.copy()
    for _ in range(6):  # look-through recursion
        for src,dst,base in ((L_eq,'e',d_eq),(L_sh,'s',d_sh),(L_ex,'x',d_ex)):
            pass
        t=cot.assign(e=cot.CNPJ_FUNDO_COTA.map(L_eq).fillna(0)*cot.w, s=cot.CNPJ_FUNDO_COTA.map(L_sh).fillna(0)*cot.w, x=cot.CNPJ_FUNDO_COTA.map(L_ex).fillna(0)*cot.w).groupby('CNPJ_FUNDO')[['e','s','x']].sum()
        L_eq=d_eq.add(t.e,fill_value=0); L_sh=d_sh.add(t.s,fill_value=0); L_ex=d_ex.add(t.x,fill_value=0)
    fundw=cot.groupby('CNPJ_FUNDO').w.sum()
    top=cot.sort_values('w').groupby('CNPJ_FUNDO').tail(1).set_index('CNPJ_FUNDO')
    parent={f:r.CNPJ_FUNDO_COTA for f,r in top.iterrows() if r.w>=0.7}
    def root(f):
        seen=set()
        while f in parent and f not in seen: seen.add(f); f=parent[f]
        return f
    df=pd.DataFrame(index=funds.union(P.index))
    df['PL']=P.VL_PATRIM_LIQ.reindex(df.index).fillna(plv.reindex(df.index))
    df['COTST']=P.NR_COTST.reindex(df.index)
    df['eq']=L_eq.reindex(df.index); df['short']=L_sh.reindex(df.index); df['ext']=L_ex.reindex(df.index)
    df['indfut']=indfut.reindex(df.index).fillna(0)
    df['fundw']=fundw.reindex(df.index).fillna(0)
    df['root']=[root(f) for f in df.index]
    df['classe']=at(cls,'DT_INI_CLASSE','DT_FIM_CLASSE',D).CLASSE.reindex(df.index)
    g=at(ges,'DT_INI_GESTOR','DT_FIM_GESTOR',D); df['gestor']=g.GESTOR.reindex(df.index)
    df['excl']=at(exc,'DT_INI_ST_EXCLUSIVO','DT_FIM_ST_EXCLUSIVO',D).FUNDO_EXCLUSIVO.reindex(df.index)
    n=at(nom,'DT_INI_DENOM_SOCIAL','DT_FIM_DENOM_SOCIAL',D).DENOM_SOCIAL
    df['nome']=n.reindex(df.index).fillna(cad.DENOM_SOCIAL.reindex(df.index))
    df['classe']=df.classe.fillna(cad.CLASSE.reindex(df.index))
    df['ANO']=y
    res[y]=df
    print(y,len(df),df.PL.notna().sum())
pd.concat(res).to_pickle(f'{W}/funds.pkl')
