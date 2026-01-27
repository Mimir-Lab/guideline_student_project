import json
from langchain_text_splitters import MarkdownHeaderTextSplitter

try:
    with open("mimir_data.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
except FileNotFoundError:
    print("Error: 'mimir_data.md' not found. Please run Step 1 (pdf_md.py) first!")
    exit()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = md_splitter.split_text(markdown_content)

chunk_data = [doc.page_content for doc in chunks]
with open("mimir_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunk_data, f, indent=4) 

print(f"Step 2 Complete: Created {len(chunks)} medical chunks and saved to 'mimir_chunks.json'.")