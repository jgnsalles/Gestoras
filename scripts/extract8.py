import pandas as pd, json, sys, glob, os
sys.path.insert(0,os.path.dirname(__file__))
R,W=sys.argv[1],sys.argv[2]
M=set(json.load(open(W+'/allfunds.json')))
import zipfile
REN={'CNPJ_FUNDO_CLASSE':'CNPJ_FUNDO','TP_FUNDO_CLASSE':'TP_FUNDO'}
out=[]
for z in sorted(glob.glob(R+'/cda_fi_20*.zip')):
    zf=zipfile.ZipFile(z)
    for n in [n for n in zf.namelist() if 'BLC_8' in n]:
        for c in pd.read_csv(zf.open(n),sep=';',encoding='latin1',dtype=str,chunksize=400000,quoting=3,on_bad_lines='skip'):
            c=c.rename(columns=REN); c=c[c.CNPJ_FUNDO.isin(M)]
            out.append(c[['CNPJ_FUNDO','DT_COMPTC','TP_APLIC','TP_ATIVO','DS_ATIVO','QT_POS_FINAL','VL_MERC_POS_FINAL','QT_AQUIS_NEGOC','VL_AQUIS_NEGOC','QT_VENDA_NEGOC','VL_VENDA_NEGOC']])
    print(os.path.basename(z),flush=True)
d=pd.concat(out); d['CD_ATIVO']=d.DS_ATIVO.str.upper().str.extract(r'\b([A-Z]{4}\d{1,2}[A-Z]?)\b',expand=False); d['CD_ISIN']=None
d.to_pickle(W+'/hist_pos8.pkl'); print(len(d), d[d.TP_APLIC.str.startswith('Ações',na=False)].CD_ATIVO.isna().mean())
