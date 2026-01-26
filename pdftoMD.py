import os
from docling.document_converter import DocumentConverter

# 1. Setup the converter
converter = DocumentConverter()

# 2. Tell the code where your PDF is
pdf_path = "001-012l_S3_Analgesie-Sedierung-Delirmanagement-in-der-Intensivmedizin-DAS_2021-08.pdf" 

# 3. Convert the PDF
result = converter.convert(pdf_path)

# 4. Save the result as a text-friendly Markdown file
markdown_output = result.document.export_to_markdown()

with open("mimir_data.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)

print("Step 1 Complete: PDF converted to Markdown!")