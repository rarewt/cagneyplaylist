from ytmusicapi import YTMusic

AUTH_FILE = "headers_auth.json"
_yt = None


def _client() -> YTMusic:
    global _yt
    if _yt is None:
        _yt = YTMusic(AUTH_FILE)
    return _yt


def search_song(name: str, artist: str) -> str | None:
    """Return videoId of the best YouTube Music match, or None."""
    yt = _client()
    query = f"{artist} - {name}" if artist else name
    results = yt.search(query, filter="songs", limit=1)
    if results:
        return results[0].get("videoId")
    return None


def create_playlist(name: str, description: str = "", privacy_status: str = "PRIVATE") -> str:
    """Return the new playlistId."""
    yt = _client()
    return yt.create_playlist(name, description, privacy_status=privacy_status)


def add_tracks(playlist_id: str, video_ids: list[str]) -> None:
    """Add video_ids to playlist in batches, falling back to one-by-one on failure."""
    yt = _client()
    batch_size = 25
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i : i + batch_size]
        try:
            yt.add_playlist_items(playlist_id, batch, duplicates=True)
        except Exception:
            for vid in batch:
                try:
                    yt.add_playlist_items(playlist_id, [vid], duplicates=True)
                except Exception:
                    pass
