import json
import os
from pathlib import Path

from flask import Flask, Response, request

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent / "data"))

# In the Docker image, index.html is copied next to app.py; in local dev
# (running `python server/app.py` from the repo root) it lives one level up.
_index_candidates = [Path(__file__).parent / "index.html", Path(__file__).parent.parent / "index.html"]
INDEX_HTML = Path(os.environ["INDEX_HTML_PATH"]) if "INDEX_HTML_PATH" in os.environ else next(
    (p for p in _index_candidates if p.exists()), _index_candidates[0]
)

VALID_COLLECTIONS = {"tasks", "rooms", "boxes", "people", "floors", "settings", "furniture", "pausedWeeks"}

app = Flask(__name__, static_folder="floors", static_url_path="/floors")


def collection_path(collection: str) -> Path:
    return DATA_DIR / f"{collection}.json"


@app.get("/")
@app.get("/index.html")
def index():
    return Response(INDEX_HTML.read_text(encoding="utf-8"), mimetype="text/html")


@app.get("/api/umzug/<collection>")
def get_collection(collection: str):
    if collection not in VALID_COLLECTIONS:
        return {"error": "unknown collection"}, 400
    path = collection_path(collection)
    if not path.exists():
        return {"error": "not found"}, 404
    return Response(path.read_text(encoding="utf-8"), mimetype="application/json")


@app.put("/api/umzug/<collection>")
def put_collection(collection: str):
    if collection not in VALID_COLLECTIONS:
        return {"error": "unknown collection"}, 400
    try:
        data = request.get_json(force=True)
    except Exception:
        return {"error": "invalid json"}, 400

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = collection_path(collection)
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data), encoding="utf-8")
    os.replace(tmp_path, path)
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
