from pathlib import Path
import pymupdf


def load_pdf(pdf_path):
    path = Path(pdf_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"PDF not found: {path.resolve()}"
        )

    pages = []

    with pymupdf.open(path) as document:
        for page_number, page in enumerate(document, 1):
            text = page.get_text("text").strip()

            if not text:
                continue

            pages.append({
                "source": path.name,
                "page": page_number,
                "text": text
            })

    return pages