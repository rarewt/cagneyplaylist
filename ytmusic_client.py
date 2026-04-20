import os
from ytmusicapi import YTMusic, OAuthCredentials
from dotenv import load_dotenv

load_dotenv()

OAUTH_FILE = "oauth.json"
_yt = None


def _client() -> YTMusic:
    global _yt
    if _yt is None:
        _yt = YTMusic(
            OAUTH_FILE,
            oauth_credentials=OAuthCredentials(
                client_id=os.environ["GOOGLE_CLIENT_ID"],
                client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            ),
        )
    return _yt


def search_song(name: str, artist: str) -> str | None:
    """Return videoId of the best YouTube Music match, or None."""
    yt = _client()
    query = f"{artist} - {name}" if artist else name
    results = yt.search(query, filter="songs", limit=1)
    if results:
        return results[0].get("videoId")
    return None


def create_playlist(name: str, description: str = "") -> str:
    """Return the new playlistId."""
    yt = _client()
    return yt.create_playlist(name, description)


def add_tracks(playlist_id: str, video_ids: list[str]) -> None:
    """Add video_ids to playlist in batches of 50."""
    yt = _client()
    batch_size = 50
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i : i + batch_size]
        yt.add_playlist_items(playlist_id, batch, duplicates=False)
