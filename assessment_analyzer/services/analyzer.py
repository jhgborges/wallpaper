import json
import os
import re

from anthropic import Anthropic

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = """Você é um especialista pedagógico que analisa avaliações escolares/acadêmicas.
Dado o texto extraído de uma prova, identifique cada questão (objetiva de múltipla escolha ou
dissertativa/aberta) e produza, para cada uma:

1. A alternativa correta (apenas para questões objetivas, no formato da letra, ex: "B").
2. A resolução completa e didática da questão (o raciocínio passo a passo que leva à resposta,
   mesmo para questões dissertativas — nesse caso, apresente uma resposta modelo/esperada).
3. O objetivo pedagógico da questão (qual habilidade, conceito ou competência ela avalia).

Responda SOMENTE com um JSON válido, sem texto antes ou depois, sem blocos de código markdown,
seguindo exatamente este formato:

{
  "titulo_avaliacao": "string com o título/disciplina da avaliação, se identificável",
  "questoes": [
    {
      "numero": 1,
      "tipo": "objetiva" | "dissertativa",
      "enunciado": "texto do enunciado da questão",
      "alternativas": {"A": "texto", "B": "texto", "C": "texto", "D": "texto", "E": "texto"},
      "resposta_correta": "B",
      "resolucao": "explicação passo a passo da resolução",
      "objetivo_pedagogico": "o que a questão avalia"
    }
  ]
}

Para questões dissertativas, omita ou deixe vazio o campo "alternativas" e "resposta_correta".
Se o texto de entrada estiver incompleto ou ilegível em algum trecho, faça o melhor possível e
indique isso no campo "resolucao" da questão afetada, mas nunca deixe de responder o JSON.
"""


class AnalysisError(Exception):
    pass


def _extract_json(raw_text: str) -> dict:
    text = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]
    return json.loads(text)


def analyze_assessment(assessment_text: str) -> dict:
    if not assessment_text.strip():
        raise AnalysisError("Não foi possível extrair texto do PDF enviado.")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise AnalysisError(
            "ANTHROPIC_API_KEY não configurada no ambiente. Defina a variável de ambiente "
            "com sua chave da API da Anthropic para usar o analisador."
        )

    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Analise a avaliação abaixo e produza o JSON solicitado.\n\n"
                    f"--- TEXTO DA AVALIAÇÃO ---\n{assessment_text}"
                ),
            }
        ],
    )

    raw_text = "".join(
        block.text for block in message.content if getattr(block, "type", None) == "text"
    )

    try:
        data = _extract_json(raw_text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise AnalysisError(f"Falha ao interpretar a resposta da IA como JSON: {exc}") from exc

    if "questoes" not in data or not isinstance(data["questoes"], list):
        raise AnalysisError("Resposta da IA não contém a lista de questões esperada.")

    return data
