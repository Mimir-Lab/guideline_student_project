"""
Markdown chunking tool with semantic awareness.
Chunks markdown files while preserving sentence and paragraph boundaries.
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict


# Approximate characters per token (GPT-style tokenizers average ~4 chars/token)
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string."""
    return len(text) // CHARS_PER_TOKEN


def tokens_to_chars(tokens: int) -> int:
    """Convert token count to approximate character count."""
    return tokens * CHARS_PER_TOKEN


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences while preserving markdown structure.
    Handles common sentence endings and markdown elements.
    """
    # Pattern to split on sentence boundaries while keeping the delimiter
    # Matches: . ! ? followed by space or newline, but not abbreviations
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\n+'
    
    sentences = re.split(sentence_pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs based on double newlines."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def extract_markdown_sections(text: str) -> List[Dict]:
    """
    Extract markdown sections based on headers.
    Returns list of dicts with 'header', 'level', and 'content'.
    """
    # Pattern to match markdown headers
    header_pattern = r'^(#{1,6})\s+(.+)$'
    
    lines = text.split('\n')
    sections = []
    current_section = {'header': None, 'level': 0, 'content': []}
    
    for line in lines:
        header_match = re.match(header_pattern, line)
        if header_match:
            # Save previous section if it has content
            if current_section['content'] or current_section['header']:
                current_section['content'] = '\n'.join(current_section['content'])
                sections.append(current_section)
            
            # Start new section
            level = len(header_match.group(1))
            header = header_match.group(2).strip()
            current_section = {'header': header, 'level': level, 'content': []}
        else:
            current_section['content'].append(line)
    
    # Don't forget the last section
    if current_section['content'] or current_section['header']:
        current_section['content'] = '\n'.join(current_section['content'])
        sections.append(current_section)
    
    return sections


def chunk_text_with_overlap(
    text: str,
    max_chunk_size: int,
    overlap_percent: float
) -> List[str]:
    """
    Chunk text while respecting sentence boundaries and adding overlap.
    
    Args:
        text: The text to chunk
        max_chunk_size: Maximum chunk size in tokens
        overlap_percent: Overlap between chunks (0.0 to 1.0)
    
    Returns:
        List of text chunks
    """
    max_chars = tokens_to_chars(max_chunk_size)
    overlap_chars = int(max_chars * overlap_percent)
    
    # First try to split by paragraphs
    paragraphs = split_into_paragraphs(text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        
        # If single paragraph is too large, split by sentences
        if para_size > max_chars:
            # Flush current chunk first
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Split large paragraph by sentences
            sentences = split_into_sentences(para)
            sentence_chunk = []
            sentence_size = 0
            
            for sentence in sentences:
                sent_size = len(sentence)
                
                if sentence_size + sent_size + 1 <= max_chars:
                    sentence_chunk.append(sentence)
                    sentence_size += sent_size + 1
                else:
                    if sentence_chunk:
                        chunks.append(' '.join(sentence_chunk))
                    sentence_chunk = [sentence]
                    sentence_size = sent_size
            
            if sentence_chunk:
                chunks.append(' '.join(sentence_chunk))
        
        # Normal case: paragraph fits
        elif current_size + para_size + 2 <= max_chars:
            current_chunk.append(para)
            current_size += para_size + 2
        
        # Need to start new chunk
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_size
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    # Apply overlap
    if overlap_percent > 0 and len(chunks) > 1:
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
            else:
                # Get overlap from previous chunk
                prev_chunk = chunks[i - 1]
                overlap_text = prev_chunk[-overlap_chars:] if len(prev_chunk) > overlap_chars else prev_chunk
                
                # Find a clean break point (sentence or paragraph boundary)
                clean_break = overlap_text.rfind('. ')
                if clean_break == -1:
                    clean_break = overlap_text.rfind('\n')
                if clean_break != -1:
                    overlap_text = overlap_text[clean_break + 1:].strip()
                
                overlapped_chunks.append(overlap_text + '\n\n' + chunk if overlap_text else chunk)
        
        chunks = overlapped_chunks
    
    return chunks


def chunk_markdown(
    markdown_text: str,
    max_chunk_size: int = 512,
    overlap_percent: float = 0.1,
    preserve_headers: bool = True
) -> List[Dict]:
    """
    Chunk a markdown document while preserving structure.
    
    Args:
        markdown_text: The markdown content to chunk
        max_chunk_size: Maximum chunk size in tokens (default: 512)
        overlap_percent: Overlap between chunks as decimal (default: 0.1 = 10%)
        preserve_headers: Whether to include section headers in each chunk
    
    Returns:
        List of chunk dictionaries with metadata
    """
    chunks = []
    chunk_id = 0
    
    # Extract sections based on headers
    sections = extract_markdown_sections(markdown_text)
    
    for section in sections:
        header = section['header']
        level = section['level']
        content = section['content'].strip()
        
        if not content and not header:
            continue
        
        # Prepare the section text
        if header:
            header_prefix = '#' * level + ' ' + header + '\n\n'
        else:
            header_prefix = ''
        
        # If content is empty, just the header
        if not content:
            if header:
                chunks.append({
                    'id': chunk_id,
                    'text': header_prefix.strip(),
                    'header': header,
                    'level': level,
                    'tokens_estimate': estimate_tokens(header_prefix)
                })
                chunk_id += 1
            continue
        
        # Check if whole section fits in one chunk
        full_text = header_prefix + content if preserve_headers else content
        if estimate_tokens(full_text) <= max_chunk_size:
            chunks.append({
                'id': chunk_id,
                'text': full_text,
                'header': header,
                'level': level,
                'tokens_estimate': estimate_tokens(full_text)
            })
            chunk_id += 1
        else:
            # Need to split the section content
            content_chunks = chunk_text_with_overlap(content, max_chunk_size, overlap_percent)
            
            for i, chunk_text in enumerate(content_chunks):
                # Add header to first chunk or all chunks if preserve_headers
                if preserve_headers and header:
                    final_text = header_prefix + chunk_text
                else:
                    final_text = chunk_text
                
                chunks.append({
                    'id': chunk_id,
                    'text': final_text,
                    'header': header,
                    'level': level,
                    'chunk_part': i + 1,
                    'total_parts': len(content_chunks),
                    'tokens_estimate': estimate_tokens(final_text)
                })
                chunk_id += 1
    
    return chunks


def chunk_markdown_file(
    input_path: str,
    output_path: str = None,
    max_chunk_size: int = 512,
    overlap_percent: float = 0.1,
    preserve_headers: bool = True
) -> List[Dict]:
    """
    Chunk a markdown file and save to JSON.
    
    Args:
        input_path: Path to input markdown file
        output_path: Path to output JSON file (default: input_path with .json extension)
        max_chunk_size: Maximum chunk size in tokens
        overlap_percent: Overlap between chunks (0.0 to 1.0)
        preserve_headers: Include section headers in each chunk
    
    Returns:
        List of chunk dictionaries
    """
    input_path = Path(input_path).resolve()
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    
    # Default output path
    if output_path is None:
        output_path = input_path.with_suffix('.chunks.json')
    else:
        output_path = Path(output_path).resolve()
    
    # Read markdown file
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    
    # Chunk the markdown
    chunks = chunk_markdown(
        markdown_text,
        max_chunk_size=max_chunk_size,
        overlap_percent=overlap_percent,
        preserve_headers=preserve_headers
    )
    
    # Prepare output with metadata
    output = {
        'source_file': str(input_path),
        'settings': {
            'max_chunk_size_tokens': max_chunk_size,
            'chars_per_token': CHARS_PER_TOKEN,
            'overlap_percent': overlap_percent,
            'preserve_headers': preserve_headers
        },
        'total_chunks': len(chunks),
        'chunks': chunks
    }
    
    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Chunked {input_path.name}")
    print(f"   → {len(chunks)} chunks created")
    print(f"   → Saved to: {output_path}")
    
    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Chunk markdown files for RAG/embedding pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chunk_md.py document.md
  python chunk_md.py document.md -s 256 -o 0.15
  python chunk_md.py document.md --output chunks.json --no-headers
        """
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input markdown file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: input_file.chunks.json)"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=512,
        help="Maximum chunk size in tokens (default: 512)"
    )
    parser.add_argument(
        "-p", "--overlap",
        type=float,
        default=0.1,
        help="Overlap between chunks as decimal, e.g., 0.1 for 10%% (default: 0.1)"
    )
    parser.add_argument(
        "--no-headers",
        action="store_true",
        help="Don't include section headers in each chunk"
    )
    
    args = parser.parse_args()
    
    try:
        chunks = chunk_markdown_file(
            input_path=args.input_file,
            output_path=args.output,
            max_chunk_size=args.size,
            overlap_percent=args.overlap,
            preserve_headers=not args.no_headers
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
