import pandas as pd, numpy as np, json, glob, zipfile, sys, os
R,W=sys.argv[1],sys.argv[2]
H=pd.read_pickle(W+'/holdings.pkl'); tks=set(H.tk)
rows=[]
for z in sorted(glob.glob(R+'/b3/COTAHIST_A*.ZIP')):
    zf=zipfile.ZipFile(z)
    for n in zf.namelist():
        for line in zf.open(n):
            if line[:2]!=b'01' or line[24:27]!=b'010': continue
            tk=line[12:24].decode('latin1').strip()
            if tk not in tks: continue
            rows.append((tk,line[2:10].decode(),int(line[108:121])/100,int(line[210:217]),int(line[170:188])/100))
b=pd.DataFrame(rows,columns=['tk','dt','close','fatcot','vol'])
b['close']=b.close/b.fatcot; b['ym']=b.dt.str[:4]+'-'+b.dt.str[4:6]
b3=b.sort_values('dt').groupby(['tk','ym']).tail(1).set_index(['tk','ym']).close.unstack(0)
b3.to_pickle(W+'/b3_monthly.pkl')
# yahoo adjusted month-end
yh={}; ysplit={}
for f in glob.glob(R+'/yahoo/*.json'):
    t=os.path.basename(f)[:-5]
    try: j=json.load(open(f))['chart']['result'][0]
    except Exception: continue
    if 'timestamp' not in j: continue
    ts=pd.to_datetime(j['timestamp'],unit='s')
    adj=j['indicators'].get('adjclose',[{}])[0].get('adjclose')
    if not adj: continue
    s=pd.Series(adj,index=ts).dropna()
    s=s.groupby(s.index.strftime('%Y-%m')).last(); yh[t]=s
yh=pd.DataFrame(yh).sort_index(); yh.to_pickle(W+'/yahoo_monthly.pkl')
# returns
months=sorted(set(b3.index)|set(yh.index))
b3=b3.reindex(months); yr=yh.reindex(months).pct_change(fill_method=None)
br=b3.pct_change(fill_method=None)
# quantity ratio across funds, for split detection
q=H[H.sign>0].groupby(['tk','ym','id']).q.sum().unstack('id')
qr={}
for tk,g in q.groupby(level=0):
    g=g.droplevel(0).reindex(months)
    qr[tk]=(g/g.shift(1)).median(axis=1)
qr=pd.DataFrame(qr)
ret=pd.DataFrame(index=months,columns=sorted(tks),dtype=float); src=pd.DataFrame('',index=months,columns=sorted(tks))
for t in tks:
    r=br[t] if t in br else pd.Series(np.nan,index=months)
    if t in qr:
        k=qr[t].reindex(months)
        pr=1+r
        split=(k.round(2).sub(1).abs()>0.3)&((pr*k-1).abs()<0.25)&((r.abs()>0.3))
        r=r.where(~split,pr*k-1)
    use_y=t in yr and yr[t].notna()
    if t in yr:
        ret[t]=yr[t].where(yr[t].notna(),r); src[t]=np.where(yr[t].notna(),'Y',np.where(r.notna(),'B',''))
    else:
        ret[t]=r; src[t]=np.where(r.notna(),'B','')
ret=ret.clip(-0.9,3)
ret.to_pickle(W+'/ret.pkl'); src.to_pickle(W+'/retsrc.pkl')
ib=yh['^BVSP'] if '^BVSP' in yh else None
print(b3.shape, yh.shape, ret.notna().sum().sum())
