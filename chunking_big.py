# chunking_big.py
import json
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

# -------------------- SETTINGS --------------------
MIN_TOKENS = 1000          # each final chunk must be at least this many tokens
TARGET_TOKENS = 1300       
MAX_CHARS_PER_CHUNK = 14000  # safety cap to prevent extremely huge chunks

MD_DIR = Path("data/md")
CHUNK_DIR = Path("data/chunks")
CHUNK_DIR.mkdir(parents=True, exist_ok=True)



def approx_token_count(text: str) -> int:
    """
    Token approximation (beginner-safe):
    ~1 token ~= 4 characters for typical text.
    This is not perfect, but good enough for controlling chunk size.
    """
    text = re.sub(r"\s+", " ", text).strip()
    return max(1, len(text) // 4)


def clean_md_text(text: str) -> str:
    """
    Fix common PDF->text artifacts:
    - non-breaking spaces
    - huge multiple spaces
    - collapsed list lines (e.g., many "Deutsche Gesellschaft..." in one line)
    - hyphenation across line breaks
    - too many blank lines
    Keeps paragraph structure as much as possible.
    """
    # 1) Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2) Non-breaking spaces -> normal spaces
    text = text.replace("\u00A0", " ")

    # 3) Fix hyphenation across line breaks: "exam-\nple" -> "example"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # 4) Break up collapsed "society lists" / long lines that should be separate bullets/lines
    
    # We insert paragraph breaks before repeated "Deutsche Gesellschaft..." patterns.
    text = re.sub(r"\)\s+(Deutsche\s+Gesellschaft)", r")\n\n\1", text)

    r
    text = re.sub(r"\)\s+(Deutschen\s+Gesellschaft)", r")\n\n\1", text)

    # 5) Collapse huge internal spacing but keep newlines:
    # Do it line-by-line so we don't destroy paragraph breaks.
    lines = text.split("\n")
    cleaned_lines = []
    for ln in lines:
        # Replace multiple spaces/tabs with a single space
        ln = re.sub(r"[ \t]{2,}", " ", ln)
        
        ln = ln.strip()
        cleaned_lines.append(ln)
    text = "\n".join(cleaned_lines)

    # 6) Remove excessive blank lines (keep max 1 empty line)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def merge_to_big_chunks(pieces, min_tokens=MIN_TOKENS, target_tokens=TARGET_TOKENS):
    """
    Merge sentence/paragraph-safe pieces until each final chunk >= min_tokens.
    We try to flush at target_tokens. We avoid breaking sentences by only merging whole pieces.
    """
    chunks = []
    buf = ""

    def flush():
        nonlocal buf
        if buf.strip():
            chunks.append(buf.strip())
        buf = ""

    for p in pieces:
        p = p.strip()
        if not p:
            continue

        if not buf:
            buf = p
            continue

        candidate = buf + "\n\n" + p

        # If too many characters, flush current buffer if it is "big enough"
        if len(candidate) > MAX_CHARS_PER_CHUNK:
            flush()
            buf = p
            continue

        buf = candidate

        # If we hit target size, flush buffer
        if approx_token_count(buf) >= target_tokens:
            flush()

    flush()

    # Second pass: ensure EVERY chunk >= min_tokens by merging small chunks forward/back
    fixed = []
    i = 0
    while i < len(chunks):
        cur = chunks[i]
        if approx_token_count(cur) >= min_tokens:
            fixed.append(cur)
            i += 1
            continue

        # If current chunk is too small, merge with the next chunk if possible
        if i + 1 < len(chunks):
            merged = cur + "\n\n" + chunks[i + 1]
            fixed.append(merged)
            i += 2
        else:
            # Last chunk is too small -> merge into previous if exists
            if fixed:
                fixed[-1] = fixed[-1] + "\n\n" + cur
            else:
                fixed.append(cur)
            i += 1

    return fixed


def chunk_one_markdown(md_text: str):
    """
    1) Clean text
    2) Create smaller "pieces" using safe separators (paragraph/newline/sentence endings)
    3) Merge pieces into BIG chunks (>= 1000 tokens)
    """
    md_text = clean_md_text(md_text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3500,     # piece size in characters (NOT final chunk size)
        chunk_overlap=0,
        separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ": ", " "],
    )

    pieces = splitter.split_text(md_text)
    big_chunks = merge_to_big_chunks(pieces)
    return big_chunks


def main():
    md_files = sorted(MD_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in: {MD_DIR.resolve()}")

    for md_path in md_files:
        md_text = md_path.read_text(encoding="utf-8", errors="ignore")

        print("\n==============================")
        print(f"Processing: {md_path.name}")
        print("Chars:", len(md_text))
        print("Head preview:", md_text[:120].replace("\n", " "))

        chunks = chunk_one_markdown(md_text)

        out_path = CHUNK_DIR / f"{md_path.stem}.chunks.json"
        out_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

        sizes = [approx_token_count(c) for c in chunks]
        print(f"Saved: {out_path}")
        print(f"Chunks: {len(chunks)} | min_tokens={min(sizes)} | avg_tokens={sum(sizes)//len(sizes)}")

        # Extra safety check
        if min(sizes) < MIN_TOKENS:
            print("⚠️ WARNING: Some chunks fell below MIN_TOKENS. Increase TARGET_TOKENS or MAX_CHARS_PER_CHUNK.")


if __name__ == "__main__":
    main()
