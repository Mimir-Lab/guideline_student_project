import json
from pathlib import Path

def convert():
    json_path = Path("structured_boxes.json")
    out_dir = Path("data/chunks")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not json_path.exists():
        print("Note: structured_boxes.json does not yet exist. Skip...")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    
    content = "### MEDIZINISCHER ENTSCHEIDUNGS-ALGORITHMUS (FLOWCHART)\n\n"
    for item in data:
        text = item.get("text", "").strip()
        label = item.get("type", "NODE")
        if text:
            content += f"- Schritt: {text} (Typ: {label})\n"

    out_file = out_dir / "flowchart_data.chunks.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump([content], f, ensure_ascii=False, indent=2)
    
    print(f"✅ Flowchart logic converted: {out_file}")

if __name__ == "__main__":
    convert()
