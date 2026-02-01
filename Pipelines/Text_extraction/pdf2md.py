import os
from pathlib import Path
from docling.document_converter import DocumentConverter

PDF_DIR = Path("data/pdfs")
MD_DIR = Path("data/md")
MD_DIR.mkdir(parents=True, exist_ok=True)

converter = DocumentConverter()

pdf_files = sorted(PDF_DIR.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No PDFs found in: {PDF_DIR.resolve()}")

for pdf_path in pdf_files:
    print(f"\n[1/3] Converting to Markdown: {pdf_path.name}")

    result = converter.convert(str(pdf_path))
    markdown_output = result.document.export_to_markdown()

    md_path = MD_DIR / (pdf_path.stem + ".md")
    md_path.write_text(markdown_output, encoding="utf-8")

    print(f"Saved: {md_path}")
