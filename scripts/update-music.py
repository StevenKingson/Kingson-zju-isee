"""Build the BGM playlist from local audio files without extra dependencies."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MUSIC = ROOT / "docs" / "assets" / "music"
MUSIC.mkdir(parents=True, exist_ok=True)
tracks = [{"id": p.name, "title": p.stem, "src": "assets/music/" + quote(p.name)}
          for p in sorted(MUSIC.iterdir(), key=lambda p: p.name.casefold())
          if p.suffix.lower() in {".mp3", ".ogg", ".wav", ".m4a", ".aac", ".flac"}]
(MUSIC / "playlist.json").write_text(
    json.dumps({"tracks": tracks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Playlist updated: {len(tracks)} track(s).")
