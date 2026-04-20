  How to get it running

  1. Install dependencies
  pip install -r requirements.txt

  2. Create your .env (copy .env.example, fill in credentials)
  - Google: Create a project at https://console.cloud.google.com, enable YouTube Data API v3, create an OAuth client (type: "TVs and
  Limited Input devices") → get Client ID + Secret

  3. Authenticate YouTube Music once
  python setup_ytmusic.py
  This opens a browser, you approve access, and it saves oauth.json.

  4. Start the server
  uvicorn main:app --host 0.0.0.0 --port 8000

  5. Expose publicly via Cloudflare Tunnel
  # Quick (no account needed, URL changes on restart):
  cloudflared tunnel --url http://localhost:8000

  # Permanent URL (requires free Cloudflare account + custom domain):
  cloudflared tunnel create cagney
  # then configure as per Cloudflare docs

  Paste the *.trycloudflare.com URL on your phone and you're set.