"""
Run this once to authenticate with YouTube Music using browser headers.
YouTube Music's API requires cookie-based auth — OAuth no longer works for writes.

Steps:
1. Open https://music.youtube.com in your browser while logged in
2. Open DevTools (F12) → Network tab
3. Reload the page, then click any request to music.youtube.com
4. Right-click the request → Copy → Copy request headers
5. Run this script and paste the headers when prompted, then press Enter twice

Usage:
    python setup_ytmusic.py
"""
from ytmusicapi import YTMusic

print("Paste your request headers from DevTools below.")
print("Press Enter twice (blank line) when done.\n")

YTMusic.setup(filepath="headers_auth.json")

print("\nDone! headers_auth.json has been created. You can now start the server.")
