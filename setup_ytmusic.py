"""
Run this once on your mini PC to authenticate with YouTube Music.
It will print a URL — open it in a browser, approve access, then paste the
redirected URL back here. Saves oauth.json for use by the main app.

Usage:
    python setup_ytmusic.py
"""
import os
from dotenv import load_dotenv
from ytmusicapi import YTMusic, OAuthCredentials

load_dotenv()

client_id = os.environ.get("GOOGLE_CLIENT_ID")
client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

if not client_id or not client_secret:
    raise SystemExit("ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")

YTMusic.setup_oauth(
    filepath="oauth.json",
    credentials=OAuthCredentials(client_id=client_id, client_secret=client_secret),
    open_browser=True,
)

print("\nDone! oauth.json has been created. You can now start the server.")
