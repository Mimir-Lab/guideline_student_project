import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from docling.document_converter import DocumentConverter

# Verzeichnis-Setup
PDF_DIR = Path("data/pdfs")
MD_DIR = Path("data/md")
CHUNK_DIR = Path("data/chunks")
IMAGE_DIR = Path("extracted_images")

for d in [MD_DIR, CHUNK_DIR, IMAGE_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

def extract_flowchart_logic(pdf_path):
    """Simuliert die Logik aus deinem Notebook: Findet Textboxen und Koordinaten."""
    doc = fitz.open(pdf_path)
    structured_data = []
    
    for page in doc:
        # Hier extrahieren wir Text-Blöcke (als Ersatz für die Bild-Extraktion im Notebook)
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                text = " ".join([span["text"] for line in b["lines"] for span in line["spans"]])
                if len(text.strip()) > 2:  # Nur relevantes speichern
                    structured_data.append({
                        "text": text.strip(),
                        "type": "NODE" if "Falls" not in text else "YES/NO"
                    })
    return structured_data

def run_pipeline():
    converter = DocumentConverter()
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    
    all_flowchart_nodes = []

    for pdf_path in pdf_files:
        print(f"🔄 Verarbeite: {pdf_path.name}")
        
        # 1. Text-Extraktion (Markdown)
        result = converter.convert(str(pdf_path))
        md_text = result.document.export_to_markdown()
        (MD_DIR / f"{pdf_path.stem}.md").write_text(md_text, encoding="utf-8")
        
        # 2. Flowchart-Extraktion (Code aus deinem Notebook integriert)
        nodes = extract_flowchart_logic(str(pdf_path))
        all_flowchart_nodes.extend(nodes)

    # 3. Speichere die JSON-Datei automatisch (ersetzt den manuellen Notebook-Schritt)
    with open("structured_boxes.json", "w", encoding="utf-8") as f:
        json.dump(all_flowchart_nodes, f, ensure_ascii=False, indent=4)
    
    print("✅ Fertig: Markdown erstellt UND structured_boxes.json generiert!")

if __name__ == "__main__":
    run_pipeline()