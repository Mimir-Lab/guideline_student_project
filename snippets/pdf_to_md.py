"""
PDF to Markdown converter using docling.
Extracts text and images from PDF files.
"""

import os
import re
import argparse
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption


def get_next_output_folder(base_path: Path) -> Path:
    """Find the next available output_n folder."""
    n = 1
    while True:
        output_folder = base_path / f"output_{n}"
        if not output_folder.exists():
            return output_folder
        n += 1


def convert_pdf_to_markdown(pdf_path: str, output_base: str = None) -> Path:
    """
    Convert a PDF file to markdown with image extraction.
    
    Args:
        pdf_path: Path to the input PDF file
        output_base: Base directory for output (defaults to same directory as PDF)
    
    Returns:
        Path to the created output folder
    """
    pdf_path = Path(pdf_path).resolve()
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.suffix.lower() == '.pdf':
        raise ValueError(f"File must be a PDF: {pdf_path}")
    
    # Determine output base directory
    if output_base:
        base_path = Path(output_base).resolve()
    else:
        base_path = pdf_path.parent
    
    # Create the next available output folder
    output_folder = get_next_output_folder(base_path)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting: {pdf_path}")
    print(f"Output folder: {output_folder}")
    
    # Configure docling pipeline for image extraction
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = 2.0  # Higher resolution for extracted images
    pipeline_options.generate_picture_images = True
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    # Convert the PDF
    result = converter.convert(pdf_path)
    
    # Get the markdown content
    markdown_content = result.document.export_to_markdown()
    
    # Extract and save images, replace references with placeholders
    image_counter = 1
    image_map = {}  # Maps original image references to our placeholder format
    
    # Extract images from the document
    for element in result.document.iterate_items():
        if hasattr(element, 'image') and element.image is not None:
            image_data = element.image
            if hasattr(image_data, 'pil_image') and image_data.pil_image is not None:
                img_filename = f"img_{image_counter}.png"
                img_path = output_folder / img_filename
                image_data.pil_image.save(img_path, "PNG")
                print(f"  Saved: {img_filename}")
                image_counter += 1
    
    # Also try to get images from pictures
    if hasattr(result.document, 'pictures'):
        for pic in result.document.pictures:
            if hasattr(pic, 'image') and pic.image is not None:
                if hasattr(pic.image, 'pil_image') and pic.image.pil_image is not None:
                    img_filename = f"img_{image_counter}.png"
                    img_path = output_folder / img_filename
                    pic.image.pil_image.save(img_path, "PNG")
                    print(f"  Saved: {img_filename}")
                    image_counter += 1
    
    # Replace image references in markdown with placeholders
    # Docling typically uses ![...](...) format for images
    img_pattern = r'!\[([^\]]*)\]\([^)]+\)'
    placeholder_counter = 1
    
    def replace_image(match):
        nonlocal placeholder_counter
        placeholder = f"<--- image {placeholder_counter} --->"
        placeholder_counter += 1
        return placeholder
    
    markdown_content = re.sub(img_pattern, replace_image, markdown_content)
    
    # Also handle any remaining image-like patterns
    # Some converters use different formats
    img_pattern2 = r'<img[^>]*>'
    markdown_content = re.sub(img_pattern2, replace_image, markdown_content)
    
    # Save the markdown file
    md_filename = pdf_path.stem + ".md"
    md_path = output_folder / md_filename
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  Saved: {md_filename}")
    print(f"Conversion complete! {image_counter - 1} images extracted.")
    
    return output_folder


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown with image extraction using docling"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Base directory for output folder (default: same as PDF location)"
    )
    
    args = parser.parse_args()
    
    try:
        output_folder = convert_pdf_to_markdown(args.pdf_path, args.output)
        print(f"\nSuccess! Output saved to: {output_folder}")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
