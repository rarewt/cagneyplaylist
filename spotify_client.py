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


def _get_tracks_from_data(data: dict) -> tuple[str, list]:
    """Navigate __NEXT_DATA__ JSON to extract playlist name and track items."""
    try:
        playlist = data["props"]["pageProps"]["state"]["data"]["playlist"]
    except KeyError:
        raise RuntimeError(
            "Unexpected __NEXT_DATA__ structure — Spotify may have changed their page format"
        )
    name = playlist["name"]
    items = playlist.get("tracks", {}).get("items", [])
    return name, items


def _parse_track(item: dict, position: int) -> dict | None:
    track = item.get("track") or {}

    # Newer Spotify page format wraps data under itemV2
    if not track:
        item_v2 = item.get("itemV2") or {}
        track = item_v2.get("data") or {}

    song_name = track.get("name", "")
    if not song_name:
        return None

    # Artists can be a list of dicts or nested under trackUnion
    artists = track.get("artists") or track.get("trackUnion", {}).get("artists", {}).get("items", [])
    artist = artists[0].get("name", "") if artists else ""

    return {"name": song_name, "artist": artist, "position": position}


def fetch_playlist(url: str) -> tuple[str, list[dict]]:
    """Return (playlist_name, tracks) by scraping the public Spotify playlist page."""
    playlist_id = _extract_playlist_id(url)
    page_url = f"https://open.spotify.com/playlist/{playlist_id}"

    resp = requests.get(page_url, headers=_HEADERS, timeout=15)
    if resp.status_code == 404:
        raise ValueError("Playlist not found — make sure it's public and the URL is correct")
    resp.raise_for_status()

    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.+?)</script>', resp.text, re.DOTALL)
    if not match:
        raise RuntimeError("Could not find track data in Spotify page — the page format may have changed")

    data = json.loads(match.group(1))
    playlist_name, items = _get_tracks_from_data(data)

    tracks = []
    for i, item in enumerate(items):
        track = _parse_track(item, i + 1)
        if track:
            tracks.append(track)

    return playlist_name, tracks
