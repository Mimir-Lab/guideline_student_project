# 1. INSTALLATION: Run 'pip install langchain-text-splitters' in terminal first
import json
from langchain_text_splitters import MarkdownHeaderTextSplitter

# 2. LOAD THE DATA
# We open the Markdown file created in Step 1
try:
    with open("mimir_data.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
except FileNotFoundError:
    print("Error: 'mimir_data.md' not found. Please run Step 1 (pdf_md.py) first!")
    exit()

# 3. DEFINE THE CHUNKING STRATEGY
# The project plan asks for cutting at paragraphs/headers.
# This method ensures that medical sections (like 'Diagnosis') stay together.
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

# 4. EXECUTE THE SPLIT
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = md_splitter.split_text(markdown_content)

# 5. JUSTIFICATION (For your Project Plan)
# We use MarkdownHeaderTextSplitter because medical guidelines are hierarchical. 
# Splitting by headers prevents the AI from mixing up symptoms of 'Disease A' 
# with treatments for 'Disease B'.

# 6. SAVE FOR NEXT STEP
# We save the chunks as a list of strings so Step 3 can read them.
chunk_data = [doc.page_content for doc in chunks]
with open("mimir_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunk_data, f, indent=4) # This adds spaces and lines

print(f"Step 2 Complete: Created {len(chunks)} medical chunks and saved to 'mimir_chunks.json'.")