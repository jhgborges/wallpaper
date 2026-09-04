import pdfplumber


def extract_text(pdf_path: str) -> str:
    """Extrai todo o texto selecionável de um PDF de avaliação, página por página."""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
    return "\n\n".join(pages_text).strip()
