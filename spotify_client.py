import re
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

_sp = None


def _client() -> spotipy.Spotify:
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
            )
        )
    return _sp


def _extract_playlist_id(url: str) -> str:
    match = re.search(r"playlist[/:]([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"Could not extract playlist ID from URL: {url}")
    return match.group(1)


def fetch_playlist(url: str) -> tuple[str, list[dict]]:
    """Return (playlist_name, tracks) where each track has name, artist, position."""
    sp = _client()
    playlist_id = _extract_playlist_id(url)

    meta = sp.playlist(playlist_id, fields="name")
    playlist_name = meta["name"]

    results = sp.playlist_tracks(playlist_id)
    items = results["items"]
    while results["next"]:
        results = sp.next(results)
        items.extend(results["items"])

    tracks = []
    for i, item in enumerate(items):
        track = item.get("track")
        if not track:
            continue
        tracks.append(
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"] if track["artists"] else "",
                "position": i + 1,
            }
        )

    return playlist_name, tracks
