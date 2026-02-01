import os
from docling.document_converter import DocumentConverter

pdf_path = "001-012l_S3_Analgesie-Sedierung-Delirmanagement-in-der-Intensivmedizin-DAS_2021-08.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

converter = DocumentConverter()
result = converter.convert(pdf_path)

markdown_output = result.document.export_to_markdown()

with open("mimir_data.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)

print("Step 1 Complete: PDF converted to Markdown!")
