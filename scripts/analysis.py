import pandas as pd, numpy as np, json, sys
R,W,O=sys.argv[1],sys.argv[2],sys.argv[3]
ST=json.load(open(W+'/members.json'))
H=pd.read_pickle(W+'/holdings.pkl'); M=pd.read_pickle(W+'/masters.pkl'); Q=pd.read_pickle(W+'/quotas.pkl')
ret=pd.read_pickle(W+'/ret.pkl'); b3=pd.read_pickle(W+'/b3_monthly.pkl'); names=pd.read_pickle(W+'/names.pkl')
# termo tickers -> base
known=set(ret.columns)
H['tk']=[t[:-1] if t.endswith('T') and t[:-1] in known else t for t in H.tk]
H=H.groupby(['id','ym','master','tk'],as_index=False).agg(q=('q','sum'),v=('v','sum'),PL=('PL','first'))
H['w']=H.v/H.PL
months=sorted(H.ym.unique())
# Ibovespa
j=json.load(open(R+'/yahoo/^BVSP.json'))['chart']['result'][0]
ib=pd.Series(j['indicators']['quote'][0]['close'],index=pd.to_datetime(j['timestamp'],unit='s')).dropna()
ib=ib.groupby(ib.index.strftime('%Y-%m')).last(); ibr=ib.pct_change()
# split factor k: total-return ratio / raw price ratio
raw=b3.reindex(months).pct_change(fill_method=None)
K=((1+ret.reindex(months))/(1+raw.reindex(columns=ret.columns))); K=K.where((K-1).abs()>0.15,1.0).fillna(1.0)
q=Q.set_index(['CNPJ_FUNDO','ym']).VL_QUOTA
ser=[]; pos=[]
for s in ST:
    i=s['id']; m=M[M.id==i].set_index('ym'); h=H[H.id==i]
    hv=h.pivot_table(index='ym',columns='tk',values='w',aggfunc='sum').reindex(m.index)
    hq=h.pivot_table(index='ym',columns='tk',values='q',aggfunc='sum').reindex(m.index)
    hval=h.pivot_table(index='ym',columns='tk',values='v',aggfunc='sum').reindex(m.index)
    ms=list(m.index)
    for a,(t0,t1) in enumerate(zip([None]+ms[:-1],ms)):
        mt=m.loc[t1,'master']; PL=m.loc[t1,'PL']
        fr=np.nan; contrib=pd.Series(dtype=float)
        if t0 is not None and pd.Period(t1)-pd.Period(t0)==pd.offsets.MonthEnd(1) or (t0 is not None and (pd.Period(t1)-pd.Period(t0)).n==1):
            for f in (mt,m.loc[t0,'master']):
                if (f,t0) in q.index and (f,t1) in q.index: fr=q[(f,t1)]/q[(f,t0)]-1; break
            w0=hv.loc[t0].dropna(); r=ret.reindex(columns=w0.index).loc[t1] if t1 in ret.index else pd.Series(np.nan,index=w0.index)
            contrib=(w0*r.fillna(0))
        expl=contrib.sum() if len(contrib) else np.nan
        wt=hv.loc[t1].dropna()
        ser.append(dict(id=i,ym=t1,PL=PL,ret_fundo=fr,ret_ibov=ibr.get(t1,np.nan),exp_long=wt[wt>0].sum(),exp_short=wt[wt<0].sum(),n_acoes=int((wt>0.001).sum()),ret_acoes_contrib=expl,master=mt))
        tks=set(wt.index)|set(contrib.index)
        for tk in tks:
            w1=hv.loc[t1].get(tk,np.nan); q1=hq.loc[t1].get(tk,np.nan); v1=hval.loc[t1].get(tk,np.nan)
            q0=hq.loc[t0].get(tk,np.nan) if t0 is not None else np.nan
            k=K.loc[t1,tk] if (t1 in K.index and tk in K.columns) else 1.0
            dq=(0 if np.isnan(q1) else q1)-(0 if np.isnan(q0) else q0)*k
            px=v1/q1 if q1 and not np.isnan(q1) and q1!=0 else (hval.loc[t0].get(tk,np.nan)/q0*(1+ret.loc[t1,tk]) if (t0 is not None and q0 and t1 in ret.index and tk in ret.columns and not np.isnan(ret.loc[t1,tk])) else np.nan)
            tv=dq*px if not np.isnan(px) else np.nan
            if t0 is None or m.loc[t0,'master']!=mt: tv=np.nan
            pos.append((i,t1,tk,w1,contrib.get(tk,np.nan),tv/PL if PL else np.nan,v1))
S=pd.DataFrame(ser)
P=pd.DataFrame(pos,columns=['id','ym','tk','peso','contrib','trade_pct_pl','valor'])
P=P[(P.peso.abs()>=0.0005)|(P.contrib.abs()>=0.00005)|(P.trade_pct_pl.abs()>=0.0005)]
S.to_pickle(W+'/serie.pkl'); P.to_pickle(W+'/pos.pkl')
print(len(S),len(P))
chk=S[(S.ym>='2014-01')&(S.ym<='2018-12')].dropna(subset=['ret_fundo'])
print('corr fundo vs contrib',chk[['ret_fundo','ret_acoes_contrib']].corr().iloc[0,1], 'mean resid',(chk.ret_fundo-chk.ret_acoes_contrib).mean())
print(chk.groupby('id').apply(lambda d: pd.Series({'fund':(1+d.ret_fundo).prod()-1,'contrib':d.ret_acoes_contrib.sum(),'ibov':(1+d.ret_ibov).prod()-1,'corr':d.ret_fundo.corr(d.ret_acoes_contrib)})).round(2).to_string())
