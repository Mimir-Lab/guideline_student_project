import json
from langchain_text_splitters import MarkdownHeaderTextSplitter

# 1. Loading MD
try:
    with open("mimir_data.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
except FileNotFoundError:
    raise FileNotFoundError(
        "Error: 'mimir_data.md' not found. Run pdftoMD.py first."
    )

# 2. Defining chonking strategy
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

# 3. Splitting MD
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)
chunks = md_splitter.split_text(markdown_content)

# 4. Saving chunks
chunk_data = [doc.page_content for doc in chunks]

with open("mimir_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunk_data, f, indent=4, ensure_ascii=False)

print(
    f"Step 2 Complete: Created {len(chunks)} chunks "
    "and saved to 'mimir_chunks.json'."
)
