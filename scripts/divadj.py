import pandas as pd, numpy as np, json, re, glob, zipfile, os, sys
R,W=sys.argv[1],sys.argv[2]
need=open(W+'/need_div.txt').read().split()
# daily closes for needed tickers
if not os.path.exists(W+'/b3_daily_need.pkl'):
    rows=[]; ns=set(need)
    for z in sorted(glob.glob(R+'/b3/COTAHIST_A*.ZIP')):
        zf=zipfile.ZipFile(z)
        for n in zf.namelist():
            for line in zf.open(n):
                if line[:2]!=b'01' or line[24:27]!=b'010': continue
                tk=line[12:24].decode('latin1').strip()
                if tk in ns: rows.append((tk,line[2:10].decode(),int(line[108:121])/100/int(line[210:217])))
    pd.DataFrame(rows,columns=['tk','dt','close']).to_pickle(W+'/b3_daily_need.pkl')
D=pd.read_pickle(W+'/b3_daily_need.pkl'); D['dt']=pd.to_datetime(D.dt,format='%Y%m%d')
# dividends
divs=[]
for t in need:
    f=f'{R}/fund/{t}.html'
    if not os.path.exists(f): continue
    s=open(f,encoding='latin1').read()
    for d,v,tp,q in re.findall(r'<td>(\d\d/\d\d/\d{4})</td>\s*<td>([\d.,]+)</td>\s*<td>([^<]+)</td>\s*<td>[^<]*</td>\s*<td>(\d+)</td>',s):
        divs.append((t,pd.to_datetime(d,format='%d/%m/%Y'),float(v.replace('.','').replace(',','.'))/int(q),tp.strip()))
dv=pd.DataFrame(divs,columns=['tk','dt','val','tipo'])
dv=dv[(dv.dt>='2011-12-01')&(dv.dt<='2023-12-31')]
# price on data-com (last close on or before)
out=[]
for t,g in dv.groupby('tk'):
    px=D[D.tk==t].sort_values('dt')
    if px.empty: continue
    m=pd.merge_asof(g.sort_values('dt'),px[['dt','close']],on='dt',direction='backward')
    m['y']=m.val/m.close; out.append(m)
dv=pd.concat(out); dv=dv[dv.y.between(0,0.25)]
dv['ym']=dv.dt.dt.strftime('%Y-%m')
dy=dv.groupby(['ym','tk']).y.sum().unstack()
dy.to_pickle(W+'/divyield_monthly.pkl')
print('tickers com proventos',dy.shape[1],'média anual de DY',round(float(dy.sum().mean()/12),4))
