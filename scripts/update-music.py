"""Build separate BGM playlists from local audio folders without extra dependencies."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
MUSIC = ROOT / "docs" / "assets" / "music"
MUSIC.mkdir(parents=True, exist_ok=True)
AUDIO_EXTENSIONS = {".mp3", ".ogg", ".wav", ".m4a", ".aac", ".flac"}


def build_playlist(folder):
    # Root audio remains the original K-ON! playlist. Each subfolder is independent.
    candidates = folder.iterdir() if folder == MUSIC else folder.rglob("*")
    files = {p.relative_to(folder).as_posix(): p
             for p in sorted(candidates, key=lambda p: p.as_posix().casefold())
             if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS}
    catalogue = folder / "library.json"
    metadata = json.loads(catalogue.read_text(encoding="utf-8")) if catalogue.exists() else {}
    playlist_id = metadata.get("id", "k-on" if folder == MUSIC else folder.name)
    title = metadata.get("title", "轻音少女" if folder == MUSIC else folder.name)
    if not isinstance(playlist_id, str) or not playlist_id.strip() or not isinstance(title, str) or not title.strip():
        raise ValueError(f"Music playlist must have a non-empty id and title: {folder}")
    tracks, seen_numbers = [], set()
    prefix = "" if folder == MUSIC else folder.relative_to(MUSIC).as_posix() + "/"

    def add_track(name, number, entry):
        tracks.append({"id": prefix + name, "title": entry.get("title", Path(name).stem),
                       "number": number, "src": "assets/music/" + quote(prefix + name, safe="/"),
                       "artist": entry.get("artist", ""), "version": entry.get("version", ""),
                       "duration": entry.get("duration_seconds")})

    for entry in metadata.get("tracks", []):
        name, number = entry["file"], entry["number"]
        if name not in files:
            raise ValueError(f"Music catalogue entry is missing or duplicated in {title}: {name}")
        if type(number) is not int or number < 1 or number in seen_numbers:
            raise ValueError(f"Music catalogue number must be unique and positive in {title}: {number}")
        seen_numbers.add(number)
        add_track(name, number, entry)
        files.pop(name)
    for name in files:
        number = max(seen_numbers, default=0) + 1
        seen_numbers.add(number)
        add_track(name, number, {})
    return {"id": playlist_id, "title": title, "tracks": tracks}


folders = [MUSIC] + sorted((p for p in MUSIC.iterdir() if p.is_dir()), key=lambda p: p.name.casefold())
playlists = []
for folder in folders:
    playlist = build_playlist(folder)
    if folder != MUSIC and not playlist["tracks"] and not (folder / "library.json").exists():
        continue
    if any(p["id"] == playlist["id"] for p in playlists):
        raise ValueError(f"Duplicate music playlist id: {playlist['id']}")
    playlists.append(playlist)

# Keep the original flat K-ON! list for visitors with a cached older player script.
(MUSIC / "playlist.json").write_text(
    json.dumps({"playlists": playlists, "tracks": playlists[0]["tracks"]}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")
print("Playlists updated: " + ", ".join(f"{p['title']} ({len(p['tracks'])} tracks)" for p in playlists))
