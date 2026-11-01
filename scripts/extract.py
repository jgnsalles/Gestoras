import pandas as pd, json, sys, zipfile, io, glob, os
R,W=sys.argv[1],sys.argv[2]
ST=json.load(open(W+'/members.json'))
M=set(c for s in ST for c in s['members'])
REN={'CNPJ_FUNDO_CLASSE':'CNPJ_FUNDO','CNPJ_FUNDO_CLASSE_COTA':'CNPJ_FUNDO_COTA','TP_FUNDO_CLASSE':'TP_FUNDO'}
def read(z,key):
    zf=zipfile.ZipFile(z); names=[n for n in zf.namelist() if key in n]
    out=[]
    for n in names:
        for c in pd.read_csv(zf.open(n),sep=';',encoding='latin1',dtype=str,chunksize=400000):
            out.append(c.rename(columns=REN))
    return pd.concat(out) if out else pd.DataFrame()
zips=sorted(glob.glob(R+'/cda_fi_20*.zip'))
pos,pls,cot=[],[],[]
for z in zips:
    b2=read(z,'BLC_2'); b2=b2[b2.CNPJ_FUNDO_COTA.notna()]
    b2['v']=pd.to_numeric(b2.VL_MERC_POS_FINAL,errors='coerce')
    # grow member set with funds held by members (masters), 3 levels
    for _ in range(3):
        new=set(b2[b2.CNPJ_FUNDO.isin(M)].CNPJ_FUNDO_COTA)-M
        M|=new
    keep=b2[b2.CNPJ_FUNDO.isin(M)][['CNPJ_FUNDO','DT_COMPTC','CNPJ_FUNDO_COTA','v']]; cot.append(keep)
    b4=read(z,'BLC_4'); b4=b4[b4.CNPJ_FUNDO.isin(M)]
    pos.append(b4[['CNPJ_FUNDO','DT_COMPTC','TP_APLIC','TP_ATIVO','CD_ATIVO','DS_ATIVO','CD_ISIN','QT_POS_FINAL','VL_MERC_POS_FINAL','QT_AQUIS_NEGOC','VL_AQUIS_NEGOC','QT_VENDA_NEGOC','VL_VENDA_NEGOC']])
    pl=read(z,'_PL_'); pls.append(pl[pl.CNPJ_FUNDO.isin(M)][['CNPJ_FUNDO','DT_COMPTC','VL_PATRIM_LIQ']])
    print(os.path.basename(z),len(M),len(pos[-1]),flush=True)
pd.concat(pos).to_pickle(W+'/hist_pos.pkl'); pd.concat(pls).to_pickle(W+'/hist_pl.pkl'); pd.concat(cot).to_pickle(W+'/hist_cot.pkl')
json.dump(sorted(M),open(W+'/allfunds.json','w'))
