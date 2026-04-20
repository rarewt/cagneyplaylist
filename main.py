import uuid
import time
import threading
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from spotify_client import fetch_playlist
from ytmusic_client import search_song, create_playlist, add_tracks

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# job_id -> {"status", "progress", "total", "result_url", "not_found", "error"}
jobs: dict[str, dict] = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/convert")
async def convert(spotify_url: str = Form(...)):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "progress": 0, "total": 0, "result_url": None, "not_found": [], "error": None}
    thread = threading.Thread(target=_run_conversion, args=(job_id, spotify_url), daemon=True)
    thread.start()
    return JSONResponse({"job_id": job_id})


@app.get("/job/{job_id}")
async def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(job)


def _run_conversion(job_id: str, spotify_url: str) -> None:
    job = jobs[job_id]
    try:
        playlist_name, tracks = fetch_playlist(spotify_url)
    except Exception as exc:
        job["status"] = "error"
        job["error"] = f"Spotify fetch failed: {exc}"
        return

    if not tracks:
        job["status"] = "error"
        job["error"] = "No tracks found — playlist may be empty or the Spotify embed format changed"
        return

    job["total"] = len(tracks)

    video_ids = []
    not_found = []
    for track in tracks:
        try:
            vid = search_song(track["name"], track["artist"])
        except Exception:
            vid = None
        if vid:
            video_ids.append(vid)
        else:
            not_found.append(f"{track['artist']} - {track['name']}")
        job["progress"] += 1
        time.sleep(0.15)

    safe_name = (playlist_name or "").strip().replace("<", "").replace(">", "")[:150] or "Spotify Playlist"
    # deduplicate while preserving order (duplicate videoIds cause add_playlist_items to 400)
    seen: set[str] = set()
    video_ids = [v for v in video_ids if not (v in seen or seen.add(v))]
    try:
        playlist_id = create_playlist(
            safe_name,
            f"Imported from Spotify: {spotify_url}"[:500],
        )
    except Exception as exc:
        job["status"] = "error"
        job["error"] = f"Failed to create YouTube Music playlist: {exc}"
        return

    try:
        if video_ids:
            add_tracks(playlist_id, video_ids)
    except Exception as exc:
        job["status"] = "error"
        job["error"] = f"Failed to add tracks: {exc}"
        return

    job["result_url"] = f"https://music.youtube.com/playlist?list={playlist_id}"
    job["not_found"] = not_found
    job["status"] = "done"
