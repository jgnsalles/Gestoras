import pandas as pd, requests, json, sys, os, time
from concurrent.futures import ThreadPoolExecutor
W,O=sys.argv[1],sys.argv[2]
tks=sorted(pd.read_pickle(W+'/holdings.pkl').tk.unique())+['^BVSP']
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0'
def get(t):
    f=f'{O}/{t}.json'
    if os.path.exists(f): return t,'cached'
    sym=t if t.startswith('^') else t+'.SA'
    for i in range(4):
        r=S.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}',params=dict(period1=1325376000,period2=1704067200,interval='1d',events='div,splits'),timeout=30)
        if r.status_code==429: time.sleep(3*(i+1)); continue
        break
    open(f,'w').write(r.text); return t,r.status_code
with ThreadPoolExecutor(6) as ex:
    res=list(ex.map(get,tks))
from collections import Counter; print(Counter(x[1] for x in res))
