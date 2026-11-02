import requests, json, os, sys, time
O=sys.argv[1]; tks=sys.argv[2].split(',')
S=requests.Session(); S.headers['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
ok=[]
for t in tks:
    f=f'{O}/{t}.json'
    if os.path.exists(f) and '"timestamp"' in open(f).read(): ok.append(t); continue
    for i in range(3):
        r=S.get(f'https://query2.finance.yahoo.com/v8/finance/chart/{t}.SA',params=dict(period1=1325376000,period2=1735689600,interval='1d',events='div,splits'),timeout=30)
        if r.status_code==429: time.sleep(5*(i+1)); continue
        break
    open(f,'w').write(r.text)
    if '"timestamp"' in r.text: ok.append(t)
    time.sleep(0.4)
print('OK',len(ok),','.join(ok))
