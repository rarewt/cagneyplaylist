"""
Run this once on your mini PC to authenticate with YouTube Music.
It will print a URL — open it in a browser, approve access, then paste the
redirected URL back here. Saves oauth.json for use by the main app.

Usage:
    python setup_ytmusic.py
"""
import dataclasses
import os

from dotenv import load_dotenv
from ytmusicapi import setup_oauth
from ytmusicapi.auth.oauth.token import RefreshingToken

# ytmusicapi doesn't handle newer Google OAuth responses that include
# refresh_token_expires_in — filter unknown fields before dataclass init.
_valid_fields = {f.name for f in dataclasses.fields(RefreshingToken)}
_orig_init = RefreshingToken.__init__

def _patched_init(self, *args, **kwargs):
    kwargs = {k: v for k, v in kwargs.items() if k in _valid_fields}
    _orig_init(self, *args, **kwargs)

RefreshingToken.__init__ = _patched_init

load_dotenv(override=True)

client_id = os.environ.get("GOOGLE_CLIENT_ID")
client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

if not client_id or not client_secret:
    raise SystemExit("ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")

setup_oauth(
    client_id=client_id,
    client_secret=client_secret,
    filepath="oauth.json",
    open_browser=True,
)

print("\nDone! oauth.json has been created. You can now start the server.")
