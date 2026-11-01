import pandas as pd, json, sys, zipfile, glob, os
R,W=sys.argv[1],sys.argv[2]
M=set(json.load(open(W+'/allfunds.json')))
REN={'CNPJ_FUNDO_CLASSE':'CNPJ_FUNDO','TP_FUNDO_CLASSE':'TP_FUNDO'}
out=[]
srcs=sorted(glob.glob(R+'/inf_diario_fi_20*.zip'))+sorted(glob.glob(R+'/inf_diario_fi_201[48]/*.csv'))
for z in srcs:
    if z.endswith('.zip') and (('_2014' in z) or ('_2018' in z)): continue
    files=[(zipfile.ZipFile(z),n) for n in zipfile.ZipFile(z).namelist()] if z.endswith('.zip') else [(None,z)]
    for zf,n in files:
        f=zf.open(n) if zf else open(n,'rb')
        d=pd.read_csv(f,sep=';',dtype=str).rename(columns=REN)
        if 'ID_SUBCLASSE' in d: d=d[d.ID_SUBCLASSE.isna()]
        d=d[d.CNPJ_FUNDO.isin(M)][['CNPJ_FUNDO','DT_COMPTC','VL_QUOTA','VL_PATRIM_LIQ']]
        out.append(d)
q=pd.concat(out); q['VL_QUOTA']=pd.to_numeric(q.VL_QUOTA,errors='coerce'); q['VL_PATRIM_LIQ']=pd.to_numeric(q.VL_PATRIM_LIQ,errors='coerce')
q['ym']=q.DT_COMPTC.str[:7]
q=q.sort_values('DT_COMPTC').groupby(['CNPJ_FUNDO','ym']).tail(1)
q.to_pickle(W+'/quotas.pkl'); print(len(q), q.ym.min(), q.ym.max())
