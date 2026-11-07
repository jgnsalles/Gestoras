# CFA Level 1 · Caderno de estudos

App estilo Notion para estudar as 10 apostilas do CFA Level 1 (Academia Rafael Toro).

- `structure.json`: módulos → capítulos → assuntos, com o intervalo de páginas de cada assunto na apostila.
- `build_structure.py`: gera o `structure.json` a partir do texto das apostilas (cabeçalho de cada página + ajustes manuais).
- `template.html`: o app. O `structure.json` entra no lugar de `/*STRUCT*/`.

Os PDFs (apostila inteira e recortes por assunto) não ficam no repositório; eles são publicados junto com o app.

- `build_app_offline.py`: gera a versão instalável no celular (pasta com index.html, manifest, service worker, ícones, pdf.js e os recortes), para hospedar e adicionar à Tela de Início.
