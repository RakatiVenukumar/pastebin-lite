# pastebin-lite

A simple Pastebin-like application where users can create text pastes and share them via a URL.  
Pastes can optionally expire after a given time or number of views.

## Features
- Create a paste with optional TTL and view limit
- Fetch paste via API (with view count enforcement)
- View paste in browser (safe HTML rendering)
- Automatic expiry handling
- Deterministic time support for testing
- Persistent storage using Redis

## Tech Stack
- Python
- FastAPI
- Redis (Upstash)
- Jinja2
- Render (deployment)

## Running Locally

```bash
git clone <your-repo-url>
cd pastebin-lite
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
