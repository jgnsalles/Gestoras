"""Captação e resgate brutos mensais do master de cada fundo (Informe Diário da CVM).

Fonte: https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/HIST/inf_diario_fi_AAAA.zip
(cache em RAW, padrão /home/user/raw_cvm). Para cada fundo e mês, o master é o CNPJ cujo
PL de fim de mês e variação da cota batem com serie_mensal.csv (que já segue a troca de master).
Saída: output/dashboard/captacao_bruta.csv  (id, ym, cnpj, capt_mi, resg_mi)
Uso: python3 scripts/ux_v2/captacao.py [RAW]
"""
import io, os, sys, zipfile
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = sys.argv[1] if len(sys.argv) > 1 else '/home/user/raw_cvm'
DS = os.path.join(ROOT, 'output', 'dashboard')

parts = []
for y in range(2013, 2019):
    z = zipfile.ZipFile(os.path.join(RAW, f'inf_{y}.zip'))
    for n in sorted(z.namelist()):
        d = pd.read_csv(io.BytesIO(z.read(n)), sep=';', usecols=['CNPJ_FUNDO', 'DT_COMPTC', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA'], dtype={'CNPJ_FUNDO': str, 'DT_COMPTC': str})
        d = d.sort_values('DT_COMPTC'); d['ym'] = d.DT_COMPTC.str[:7]
        g = d.groupby(['CNPJ_FUNDO', 'ym'])
        parts.append(pd.DataFrame({'pl': g.VL_PATRIM_LIQ.last(), 'cota': g.VL_QUOTA.last(), 'capt': g.CAPTC_DIA.sum(), 'resg': g.RESG_DIA.sum()}).reset_index())
        print(n, len(d), flush=True)
M = pd.concat(parts).groupby(['CNPJ_FUNDO', 'ym'], as_index=False).last().sort_values(['CNPJ_FUNDO', 'ym'])
M['ret'] = M.groupby('CNPJ_FUNDO').cota.pct_change()
M['pl_mi'] = (M.pl / 1e6).round(1)

S = pd.read_csv(os.path.join(DS, 'serie_mensal.csv'))
S = S[(S.ym >= '2013-12') & (S.ym <= '2018-12')]
F = pd.read_csv(os.path.join(DS, 'fundos.csv'), dtype=str)
pref = dict(zip(F.id.astype(int), F.cnpj_master_2018))
byPL = M.groupby('pl_mi')
out = []
for r in S.itertuples():
    if pd.isna(r.PL_mi):
        continue
    try:
        c = byPL.get_group(round(r.PL_mi, 1))
    except KeyError:
        c = M.iloc[0:0]
    c = c[c.ym == r.ym]
    if len(c) > 1 and not pd.isna(r.ret_fundo):
        c = c[(c.ret - r.ret_fundo).abs() < 2e-4]
    if len(c) > 1:
        c2 = c[c.CNPJ_FUNDO == pref.get(r.id)]
        c = c2 if len(c2) else c
    if len(c) != 1:
        out.append({'id': r.id, 'ym': r.ym, 'cnpj': '', 'capt_mi': '', 'resg_mi': ''})
        continue
    x = c.iloc[0]
    out.append({'id': r.id, 'ym': r.ym, 'cnpj': x.CNPJ_FUNDO, 'capt_mi': round(x.capt / 1e6, 2), 'resg_mi': round(x.resg / 1e6, 2)})
O = pd.DataFrame(out)
O.to_csv(os.path.join(DS, 'captacao_bruta.csv'), index=False)
miss = O[O.cnpj == '']
print('linhas', len(O), 'sem master identificado', len(miss))
print(miss.groupby('id').size().to_string())
