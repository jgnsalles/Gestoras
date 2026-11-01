import pandas as pd, glob, zipfile, sys
R,W=sys.argv[1],sys.argv[2]
tks=set(pd.read_pickle(W+'/holdings.pkl').tk); tks|={t[:-1] for t in tks if t.endswith('T')}
nm={}
for z in sorted(glob.glob(R+'/b3/COTAHIST_A*.ZIP')):
    zf=zipfile.ZipFile(z)
    for n in zf.namelist():
        for line in zf.open(n):
            if line[:2]!=b'01' or line[24:27]!=b'010': continue
            tk=line[12:24].decode('latin1').strip()
            if tk in tks: nm[tk]=line[27:39].decode('latin1').strip()
pd.Series(nm).to_pickle(W+'/names.pkl'); print(len(nm))
