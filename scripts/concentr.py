import pandas as pd, numpy as np, sys
W,O=sys.argv[1],sys.argv[2]
P=pd.read_pickle(W+'/pos.pkl'); F=pd.read_csv(O+'/fundos.csv')
P=P[(P.ym>='2014-01')&(P.ym<='2018-12')&(P.peso>0)]
def per_month(g):
    w=g.peso.values; s=w/w.sum()
    return pd.Series({'n1':(w>=0.01).sum(),'n3':(w>=0.03).sum(),'top1':w.max(),'top1s':s.max(),'top5s':np.sort(s)[-5:].sum(),'effN':1/(s**2).sum(),'exp':w.sum()})
m=P.groupby(['id','ym']).apply(per_month)
r=m.groupby('id').agg(n1=('n1','mean'),n3=('n3','mean'),top1=('top1','mean'),top1max=('top1','max'),top1s=('top1s','mean'),top5s=('top5s','mean'),effN=('effN','mean'),meses_top1_30=('top1s',lambda x:(x>0.3).mean()))
r=F.set_index('id')[['fundo','gestora']].join(r).round(2)
r.to_csv(W+'/concentr.csv'); pd.set_option('display.width',250)
print(r.sort_values('effN').to_string())
