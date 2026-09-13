from pathlib import Path
import fitz


def load_pdf(pdf_path: Path):
    """
    Extract text from a single PDF.

    Returns:
        list of dictionaries containing page text and metadata.
    """

    pdf_path = Path(pdf_path)

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text("text").strip()

        if text:
            pages.append({
                "text": text,
                "metadata": {
                    "source": pdf_path.name,
                    "page": page_number + 1
                }
            })

    document.close()

    return pages