import os
from pathlib import Path
from docling.document_converter import DocumentConverter

# Define directories
PDF_DIR = Path("data/pdfs")
MD_DIR = Path("data/md")

# Make sure the output directory exists
MD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize the document converter
converter = DocumentConverter()

# Get a sorted list of all PDF files in the PDF_DIR
pdf_files = sorted(PDF_DIR.glob("*.pdf"))

# Raise an error if no PDFs are found
if not pdf_files:
    raise FileNotFoundError(f"No PDFs found in: {PDF_DIR.resolve()}")

# Loop through each PDF and convert to Markdown
for index, pdf_path in enumerate(pdf_files, start=1):
    print(f"\n[{index}/{len(pdf_files)}] Converting PDF to Markdown: '{pdf_path.name}'")

    # Convert PDF to document object
    result = converter.convert(str(pdf_path))

    # Export the document as Markdown
    markdown_output = result.document.export_to_markdown()

    # Save the Markdown file to MD_DIR
    md_path = MD_DIR / (pdf_path.stem + ".md")
    md_path.write_text(markdown_output, encoding="utf-8")

    print(f"[{index}/{len(pdf_files)}] Saved Markdown: '{md_path}'")
