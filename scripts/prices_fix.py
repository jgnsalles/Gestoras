import pandas as pd, numpy as np, json, sys
W=sys.argv[1]
ret=pd.read_pickle(W+'/ret.pkl'); src=pd.read_pickle(W+'/retsrc.pkl')
succ={k:v for k,v in json.load(open(W+'/succ.json')).items() if v[1]>=0.97 and k!=v[0]}
dy=pd.read_pickle(W+'/divyield_monthly.pkl')
def ym(f):
    j=json.load(open(f))['chart']['result'][0]; ts=pd.to_datetime(j['timestamp'],unit='s')
    a=pd.Series(j['indicators']['adjclose'][0]['adjclose'],index=ts).dropna(); return a.groupby(a.index.strftime('%Y-%m')).last().pct_change()
nS=nD=0
for old,(new,c,n) in succ.items():
    if old not in ret: continue
    y=ym(f'raw/yahoo2/{new}.json').reindex(ret.index)
    m=(src[old]=='B')&y.notna()&ret[old].notna()
    ret.loc[m,old]=y[m]; src.loc[m,old]='S'; nS+=int(m.sum())
for t in dy.columns:
    if t not in ret: continue
    d=dy[t].reindex(ret.index).fillna(0)
    m=(src[t]=='B')&ret[t].notna()&(d>0)
    ret.loc[m,t]=(1+ret.loc[m,t])*(1+d[m])-1; src.loc[m,t]='BD'; nD+=int(m.sum())
ret.to_pickle(W+'/ret.pkl'); src.to_pickle(W+'/retsrc.pkl')
print('meses via sucessor',nS,'meses com dividendos somados',nD)
