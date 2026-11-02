import pandas as pd, zipfile, glob, json, sys
R,W=sys.argv[1],sys.argv[2]
C={'08.912.569/0001-35':('GAP Ações','GAP Asset (Trek)'),'16.498.954/0001-06':('Pollux Ações','Empiricus Asset'),'19.821.896/0001-06':('Skopos Participações','Skopos'),
'11.046.170/0001-23':('Gávea Estratégia Ações','Gávea Investimentos'),'18.846.554/0001-70':('Vertra','Multiplica Capital'),'07.549.186/0001-81':('Long Brasil Ações','Una Capital'),
'11.361.553/0001-96':('BRZ Valor','BRZ Investimentos'),'07.914.910/0001-29':('Polo Latitude 84','Polo Capital'),'13.089.215/0001-72':('3G Brasil Ações','3G Capital')}
out=[]
src=[z for z in sorted(glob.glob(R+'/inf_diario_fi_201[3-9].zip')) if '2014' not in z and '2018' not in z]+sorted(glob.glob(R+'/inf_diario_fi_201[48]/*.csv'))
for z in src:
    files=[(zipfile.ZipFile(z),n) for n in zipfile.ZipFile(z).namelist()] if z.endswith('.zip') else [(None,z)]
    for zf,n in files:
        d=pd.read_csv(zf.open(n) if zf else n,sep=';',dtype=str)
        d=d[d.CNPJ_FUNDO.isin(C)]; out.append(d[['CNPJ_FUNDO','DT_COMPTC','VL_QUOTA','VL_PATRIM_LIQ']])
q=pd.concat(out); q['ym']=q.DT_COMPTC.str[:7]; q=q.sort_values('DT_COMPTC').groupby(['CNPJ_FUNDO','ym']).tail(1)
q[['q','pl']]=q[['VL_QUOTA','VL_PATRIM_LIQ']].astype(float)
ib=pd.read_csv('out/ibov.csv').set_index('ym').pontos
gh=pd.read_csv(R+'/cad_fi_hist/cad_fi_hist_gestor.csv',sep=';',encoding='latin1',dtype=str)
rows=[]
for c,(nm,g) in C.items():
    x=q[q.CNPJ_FUNDO==c].set_index('ym').sort_index(); x=x[x.pl>1e6]
    if x.empty: continue
    h=gh[gh.CNPJ_FUNDO==c].sort_values('DT_INI_GESTOR')
    h14=h[(h.DT_INI_GESTOR<='2014-12-31')&((h.DT_FIM_GESTOR.isna())|(h.DT_FIM_GESTOR>='2014-12-31'))]
    fim_g=h14.DT_FIM_GESTOR.iloc[-1] if len(h14) and isinstance(h14.DT_FIM_GESTOR.iloc[-1],str) else None
    novo=h[h.DT_INI_GESTOR>(fim_g or '9999')].GESTOR.iloc[0] if fim_g and (h.DT_INI_GESTOR>fim_g).any() else ''
    last=x.index[-1]; evento='Encerrado'
    if fim_g and fim_g[:7]<last: last=fim_g[:7]; evento='Gestão transferida para '+str(novo).title()
    first='2013-12'; xx=x.loc[first:last]
    r=xx.q.iloc[-1]/xx.q.iloc[0]-1; ri=ib.get(last)/ib.get(first)-1
    rows.append(dict(cnpj=c,fundo=nm,gestora=g,pl_2014_mi=round(x.pl.get('2014-12',float('nan'))/1e6),pl_max_mi=round(x.loc[:last].pl.max()/1e6),ultimo_mes=last,evento=evento,ret_fundo=round(r,4),ret_ibov=round(ri,4)))
    print(nm,last,evento,round(r,3),round(ri,3))
pd.DataFrame(rows).sort_values('pl_2014_mi',ascending=False).to_csv('out/encerrados.csv',index=False)
q.to_pickle(W+'/closed_q.pkl')
