# Analisador de Avaliações → Relatório em PDF

Aplicação web simples (Flask) que recebe uma avaliação em PDF, usa a API da
Anthropic (Claude) para identificar cada questão e gera um relatório em PDF
com paleta de cores suaves contendo:

1. As alternativas corretas das questões objetivas;
2. As resoluções de todas as questões (objetivas e dissertativas);
3. O objetivo pedagógico de cada questão.

## Como rodar

```bash
cd assessment_analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env e defina ANTHROPIC_API_KEY com sua chave da Anthropic

python app.py
```

Acesse `http://localhost:5000`, envie o PDF da prova e baixe o relatório
gerado.

## Estrutura

```
assessment_analyzer/
├── app.py                  # servidor Flask (upload, orquestração, download)
├── services/
│   ├── pdf_extract.py      # extrai texto do PDF enviado
│   ├── analyzer.py         # chama a IA e retorna JSON estruturado das questões
│   └── report.py           # gera o PDF final com ReportLab (paleta suave)
├── templates/               # páginas HTML (upload / resultado)
├── static/style.css         # estilo visual da interface web
└── uploads/, reports/       # arquivos temporários (ignorados no git)
```

## Observações

- Requer uma chave de API válida da Anthropic (`ANTHROPIC_API_KEY`).
- O texto do PDF precisa ser selecionável (não é feito OCR de imagens/scans).
- Sempre revise o relatório gerado pela IA antes de usá-lo com alunos.
