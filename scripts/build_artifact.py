"""Monta o artifact "Navegando Dilma 2 v2" a partir do template e dos CSVs do repo.

Uso: python scripts/build_artifact.py
Entrada: output/artifact/navegando_dilma_2_v2.template.html + output/dashboard/*.csv
Saída:   output/navegando_dilma_2_v2.html (arquivo único, dados embutidos)
"""
import re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
tpl = (R / 'output/artifact/navegando_dilma_2_v2.template.html').read_text()
def fill(m):
    return (R / 'output/dashboard' / (m.group(1) + '.csv')).read_text()
out = re.sub(r'\{\{CSV:(\w+)\}\}', fill, tpl)
(R / 'output/navegando_dilma_2_v2.html').write_text(out)
print('ok', len(out))
