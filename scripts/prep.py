import pandas as pd, glob, sys
R=sys.argv[1]; O=sys.argv[2]
# PL at last report of Dec 2014 / Dec 2018 (+ check existence mid-period via dec months)
out=[]
for y in (2014,2018):
    d=pd.read_csv(f'{R}/inf_diario_fi_{y}/inf_diario_fi_{y}12.csv',sep=';',dtype={'CNPJ_FUNDO':str})
    d=d.sort_values('DT_COMPTC').groupby('CNPJ_FUNDO').tail(1)
    d['ANO']=y; out.append(d[['CNPJ_FUNDO','ANO','DT_COMPTC','VL_PATRIM_LIQ','NR_COTST']])
pd.concat(out).to_pickle(f'{O}/pl.pkl')
for y in (2014,2018):
    for b in ('BLC_2','BLC_1','BLC_4','BLC_7','BLC_8','PL'):
        f=f'{R}/cda_{y}/cda_fi_{b}_{y}.csv'
        it=pd.read_csv(f,sep=';',encoding='latin1',dtype=str,chunksize=500000)
        df=pd.concat(c[c.DT_COMPTC.str.startswith(f'{y}-12')] for c in it)
        df.to_pickle(f'{O}/cda_{b}_{y}.pkl'); print(y,b,len(df))
