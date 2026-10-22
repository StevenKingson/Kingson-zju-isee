"""Scan local artbooks and create the site's image list. No extra packages needed."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARTBOOKS = DOCS / "assets" / "artbooks"


def natural_key(path):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", path.name)]


albums = []
for folder in sorted(ARTBOOKS.iterdir()):
    if not folder.is_dir():
        continue
    metadata_path = folder / "album.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    files = sorted((p for p in folder.iterdir()
                    if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif"}),
                   key=natural_key)
    images = []
    for index, path in enumerate(files, 1):
        number = int(path.stem) if path.stem.isdigit() else index
        images.append({"number": number, "name": path.name,
                       "src": path.relative_to(DOCS).as_posix()})
    if len({item["number"] for item in images}) != len(images):
        raise ValueError(f"Duplicate image numbers in {folder.name}; use unique numeric filenames.")
    if images:
        albums.append({"id": folder.name, "title": metadata.get("title", folder.name),
                       "description": metadata.get("description", ""), "images": images})

output = DOCS / "assets" / "gallery.json"
output.write_text(json.dumps({"albums": albums}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Gallery updated: {len(albums)} album(s), {sum(len(a['images']) for a in albums)} images.")
