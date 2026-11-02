import pandas as pd, numpy as np, json, os
b3=pd.read_pickle('work/b3_monthly.pkl')
def ym(f):
    j=json.load(open(f))['chart']['result'][0]; ts=pd.to_datetime(j['timestamp'],unit='s')
    a=pd.Series(j['indicators']['adjclose'][0]['adjclose'],index=ts).dropna(); return a.groupby(a.index.strftime('%Y-%m')).last()
P={'BRFS3':'MBRF3','BVMF3':'B3SA3','JSLG3':'SIMH3','KROT3':'COGN3','IGTA3':'IGTI11','ALSC3':'ALOS3','PCAR4':'PCAR3','LAME4':'AMER3','LAME3':'AMER3','VIVT4':'VIVT3','VALE5':'VALE3','SUZB5':'SUZB3','ELET3':'AXIA3','ELET6':'AXIA3','ESTC3':'YDUQ3','EMBR3':'EMBJ3','DTEX3':'DXCO3','VVAR3':'BHIA3','TRPL4':'ISAE4','CCRO3':'MOTV3','BRDT3':'VBBR3','QGEP3':'BRAV3','TIMP3':'TIMS3','ARZZ3':'AZZA3','NTCO3':'NATU3','RAIL3':'RAIL3','RUMO3':'RAIL3','HAPV3':'HAPV3','QUAL3':'QUAL3','MULT3':'MULT3','TOTS3':'TOTS3','JSLG3x':'JSLG3'}
res={}
for old,new in P.items():
    o=old.rstrip('x'); f=f'raw/yahoo2/{new}.json'
    if o not in b3 or not os.path.exists(f): continue
    y=ym(f).pct_change(); r=b3[o].pct_change(fill_method=None)
    d=pd.concat([r,y],axis=1,keys=['b3','y']).dropna(); d=d[(d.b3.abs()<0.4)]
    d=d[(d.index>='2012-01')&(d.index<='2019-12')]
    if len(d)<12: print(old,new,'poucos',len(d)); continue
    c=d.b3.corr(d.y); md=(d.y-d.b3).median()
    print(f'{old:7}->{new:7} n={len(d):3} corr={c:.3f} medDiff={md*100:.2f}%  meses {d.index.min()}..{d.index.max()}')
    res[old.rstrip('x')]=(new,round(c,3),len(d))
json.dump(res,open('work/succ.json','w'))
