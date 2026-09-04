from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Paleta de cores suaves
COLOR_BG_PAGE = colors.HexColor("#FBFAF8")
COLOR_PRIMARY = colors.HexColor("#6E85A6")      # azul acinzentado suave
COLOR_PRIMARY_DARK = colors.HexColor("#4F6280")
COLOR_ACCENT_GREEN = colors.HexColor("#BFE3D0")  # verde pastel (resposta correta)
COLOR_ACCENT_GREEN_TEXT = colors.HexColor("#2F6B4F")
COLOR_ACCENT_LILAC = colors.HexColor("#E3DDF0")  # lilás pastel (resolução)
COLOR_ACCENT_PEACH = colors.HexColor("#F6E4D7")  # pêssego pastel (objetivo pedagógico)
COLOR_TEXT = colors.HexColor("#4A4A4A")
COLOR_TEXT_LIGHT = colors.HexColor("#7A7A7A")
COLOR_CARD_BORDER = colors.HexColor("#E3E0DA")


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "TitleCustom", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=22, textColor=COLOR_PRIMARY_DARK, alignment=TA_CENTER, spaceAfter=6,
        ),
        "Subtitle": ParagraphStyle(
            "SubtitleCustom", parent=base["Normal"], fontName="Helvetica",
            fontSize=12, textColor=COLOR_TEXT_LIGHT, alignment=TA_CENTER, spaceAfter=20,
        ),
        "QuestionHeader": ParagraphStyle(
            "QuestionHeader", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, textColor=colors.white, alignment=TA_CENTER,
        ),
        "Statement": ParagraphStyle(
            "Statement", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, textColor=COLOR_TEXT, alignment=TA_JUSTIFY, leading=15, spaceAfter=8,
        ),
        "Alternative": ParagraphStyle(
            "Alternative", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, textColor=COLOR_TEXT, leading=14,
        ),
        "AlternativeCorrect": ParagraphStyle(
            "AlternativeCorrect", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10, textColor=COLOR_ACCENT_GREEN_TEXT, leading=14,
        ),
        "SectionLabel": ParagraphStyle(
            "SectionLabel", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9.5, textColor=COLOR_PRIMARY_DARK, spaceAfter=3,
        ),
        "SectionBody": ParagraphStyle(
            "SectionBody", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, textColor=COLOR_TEXT, alignment=TA_JUSTIFY, leading=14,
        ),
        "FooterNote": ParagraphStyle(
            "FooterNote", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=8, textColor=COLOR_TEXT_LIGHT, alignment=TA_CENTER,
        ),
    }
    return styles


def _question_card(question: dict, styles) -> KeepTogether:
    numero = question.get("numero", "?")
    tipo = question.get("tipo", "objetiva")
    enunciado = question.get("enunciado", "")
    alternativas = question.get("alternativas") or {}
    resposta_correta = (question.get("resposta_correta") or "").strip().upper()
    resolucao = question.get("resolucao", "Não informado.")
    objetivo = question.get("objetivo_pedagogico", "Não informado.")

    flow = []

    header_table = Table(
        [[Paragraph(f"Questão {numero}  ·  {tipo.capitalize()}", styles["QuestionHeader"])]],
        colWidths=[17 * cm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [6, 6, 0, 0]),
    ]))
    flow.append(header_table)
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(enunciado.replace("\n", "<br/>"), styles["Statement"]))

    if tipo == "objetiva" and alternativas:
        items = []
        for letra in sorted(alternativas.keys()):
            texto = alternativas[letra]
            is_correct = letra.strip().upper() == resposta_correta
            style = styles["AlternativeCorrect"] if is_correct else styles["Alternative"]
            marker = "✔ " if is_correct else ""
            items.append(Paragraph(f"{marker}<b>{letra})</b> {texto}", style))
        flow.append(ListFlowable(
            [ListItem(p, leftIndent=6) for p in items],
            bulletType="bullet", start="circle", leftIndent=10, spaceBefore=2, spaceAfter=8,
        ))
        if resposta_correta:
            answer_table = Table(
                [[Paragraph(f"Alternativa correta: <b>{resposta_correta}</b>", styles["Alternative"])]],
                colWidths=[17 * cm],
            )
            answer_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_ACCENT_GREEN),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            flow.append(answer_table)
            flow.append(Spacer(1, 8))

    resolucao_table = Table(
        [[Paragraph("Resolução", styles["SectionLabel"])],
         [Paragraph(resolucao.replace("\n", "<br/>"), styles["SectionBody"])]],
        colWidths=[17 * cm],
    )
    resolucao_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_ACCENT_LILAC),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(resolucao_table)
    flow.append(Spacer(1, 6))

    objetivo_table = Table(
        [[Paragraph("Objetivo pedagógico", styles["SectionLabel"])],
         [Paragraph(objetivo.replace("\n", "<br/>"), styles["SectionBody"])]],
        colWidths=[17 * cm],
    )
    objetivo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_ACCENT_PEACH),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(objetivo_table)
    flow.append(Spacer(1, 18))

    return KeepTogether(flow)


def _page_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(COLOR_BG_PAGE)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLOR_TEXT_LIGHT)
    canvas.drawRightString(doc.pagesize[0] - 1.5 * cm, 1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def generate_report(data: dict, output_path: str) -> str:
    styles = _styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
    )

    story = []
    titulo = data.get("titulo_avaliacao") or "Relatório de Análise da Avaliação"
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(titulo, styles["Title"]))
    story.append(Paragraph(
        "Gabarito, resoluções comentadas e objetivos pedagógicos por questão",
        styles["Subtitle"],
    ))
    story.append(HRFlowable(width="100%", color=COLOR_CARD_BORDER, thickness=1))
    story.append(Spacer(1, 1 * cm))

    for questao in data.get("questoes", []):
        story.append(_question_card(questao, styles))

    if not data.get("questoes"):
        story.append(Paragraph("Nenhuma questão foi identificada no documento enviado.", styles["Statement"]))

    doc.build(story, onFirstPage=_page_background, onLaterPages=_page_background)
    return output_path
