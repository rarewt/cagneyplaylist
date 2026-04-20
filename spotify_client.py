import re
import json
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _extract_playlist_id(url: str) -> str:
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"Could not extract playlist ID from URL: {url}")
    return match.group(1)


def fetch_playlist(url: str) -> tuple[str, list[dict]]:
    """Return (playlist_name, tracks) by scraping the Spotify embed page."""
    playlist_id = _extract_playlist_id(url)
    embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"

    resp = requests.get(embed_url, headers=_HEADERS, timeout=15)
    if resp.status_code == 404:
        raise ValueError("Playlist not found — make sure it's public and the URL is correct")
    resp.raise_for_status()

    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>', resp.text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not find track data in Spotify embed page — the page format may have changed")

    data = json.loads(match.group(1))
    try:
        entity = data["props"]["pageProps"]["state"]["data"]["entity"]
    except KeyError:
        raise RuntimeError("Unexpected embed page structure — Spotify may have changed their format")

    playlist_name = entity.get("name") or entity.get("title", "Spotify Playlist")
    track_list = entity.get("trackList", [])

    tracks = []
    for i, item in enumerate(track_list):
        title = item.get("title", "")
        if not title:
            continue
        # subtitle is "Artist1,\xa0Artist2" for multi-artist tracks; take only the first
        subtitle = item.get("subtitle", "")
        artist = re.split(r",\s*\xa0|,\s+", subtitle)[0].strip()
        tracks.append({"name": title, "artist": artist, "position": i + 1})

    return playlist_name, tracks
