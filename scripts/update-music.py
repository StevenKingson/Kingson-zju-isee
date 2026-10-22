"""Build the BGM playlist from local audio files without extra dependencies."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MUSIC = ROOT / "docs" / "assets" / "music"
MUSIC.mkdir(parents=True, exist_ok=True)
files = {p.name: p for p in sorted(MUSIC.iterdir(), key=lambda p: p.name.casefold())
         if p.suffix.lower() in {".mp3", ".ogg", ".wav", ".m4a", ".aac", ".flac"}}
catalogue = MUSIC / "library.json"
entries = json.loads(catalogue.read_text(encoding="utf-8"))["tracks"] if catalogue.exists() else []
tracks = []
seen_numbers = set()
for entry in entries:
    name, number = entry["file"], entry["number"]
    if name not in files:
        raise ValueError(f"Music catalogue entry is missing or duplicated: {name}")
    if not isinstance(number, int) or number < 1 or number in seen_numbers:
        raise ValueError(f"Music catalogue number must be unique and positive: {number}")
    seen_numbers.add(number)
    tracks.append({"id": name, "title": entry["title"], "number": number,
                   "src": "assets/music/" + quote(name),
                   "version": entry.get("version", ""),
                   "duration": entry.get("duration_seconds")})
    files.pop(name)
for name in files:
    number = max(seen_numbers, default=0) + 1
    seen_numbers.add(number)
    tracks.append({"id": name, "title": Path(name).stem, "number": number,
                   "src": "assets/music/" + quote(name)})
(MUSIC / "playlist.json").write_text(
    json.dumps({"tracks": tracks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Playlist updated: {len(tracks)} track(s).")
