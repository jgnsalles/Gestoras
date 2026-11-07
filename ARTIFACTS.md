# Artifacts ↔ repositório

| Artifact | Fonte neste repo | Situação |
|---|---|---|
| [Navegando Dilma 2 v2](https://claude.ai/artifact/3UFyQdFMNvtVdBw1QJFQZ7) | `output/navegando_dilma_2_v2.html`, gerado por `scripts/build_artifact.py` a partir de `output/artifact/navegando_dilma_2_v2.template.html` + `output/dashboard/*.csv` | Os 12 CSVs embutidos são idênticos aos do repo (`captacao_bruta.csv` foi extraído do artifact). |
| [Navegando Dilma 2](https://claude.ai/artifact/2BvQ6VfT7xhmGHKeVHmeLe) | mesmo arquivo acima (versão sem o link do repo) | Duplicata criada em 07/11/2026; pode ser apagada. |
| [Gestoras CVM](https://claude.ai/artifact/Q23RciSP79xPyVvTYkMUuh) | `output/artifact/gestoras_cvm.html` (dados embutidos, gerado em 02/10/2026) | Formulário de Referência da CVM 2016–2025. Os dados não vêm dos scripts deste repo; o HTML publicado foi guardado aqui como fonte. |
| [Carteiras das Gestoras](https://claude.ai/artifact/FgEspc6hKKbuF83qguuiz1) | `output/artifact/carteiras_gestoras.html` (dados embutidos, gerado em 03/10/2026) | CDA da CVM 2005–2026 agregada por gestora. Os dados não vêm dos scripts deste repo; o HTML publicado foi guardado aqui como fonte. |

Versões anteriores da página Navegando Dilma 2 (5 abas, sem Ciclo): `output/navegando_dilma_2.html` e `output/dashboard/index.html` (`scripts/standalone.py`).

Para atualizar a Navegando Dilma 2 depois de mudar os CSVs: `python scripts/build_artifact.py` e republicar o HTML gerado.
