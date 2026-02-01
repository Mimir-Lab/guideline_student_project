import json
from pathlib import Path

def convert():
    json_path = Path("structured_boxes.json")
    out_dir = Path("data/chunks")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not json_path.exists():
        print("Hinweis: structured_boxes.json noch nicht vorhanden. Überspringe...")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Wir bauen eine Text-Beschreibung des Algorithmus
    content = "### MEDIZINISCHER ENTSCHEIDUNGS-ALGORITHMUS (FLOWCHART)\n\n"
    for item in data:
        text = item.get("text", "").strip()
        label = item.get("type", "NODE")
        if text:
            content += f"- Schritt: {text} (Typ: {label})\n"

    out_file = out_dir / "flowchart_data.chunks.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump([content], f, ensure_ascii=False, indent=2)
    
    print(f"✅ Flowchart-Logik konvertiert: {out_file}")

if __name__ == "__main__":
    convert()