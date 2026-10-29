from __future__ import annotations

import os
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

_store: dict[int, dict] = {}
_lock = threading.Lock()
_next_id = {"v": 1}


def _seed():
    with _lock:
        _store.clear()
        _next_id["v"] = 1
        for item in ({"name": "Amethyst", "category": "Healing", "description": "violet quartz", "price": 20.0},
                     {"name": "Ruby", "category": "Gemstones", "description": "heart crystal", "price": 50.0}):
            _store[_next_id["v"]] = {"id": _next_id["v"], **item}
            _next_id["v"] += 1


_seed()


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.post("/reset")
def reset():
    _seed()
    return jsonify(status="reset", count=len(_store)), 200


@app.post("/api/crystals")                      # CREATE
def create():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("name"), str) or not data["name"].strip():
        return jsonify(error="Field 'name' is required"), 400
    with _lock:
        _id = _next_id["v"]; _next_id["v"] += 1
        rec = {"id": _id, "name": data["name"], "category": data.get("category", "Uncategorised"),
               "description": data.get("description", ""), "price": data.get("price", 0.0)}
        _store[_id] = rec
    return jsonify(rec), 201


@app.get("/api/crystals")                       # READ (list)
def list_all():
    return jsonify(list(_store.values())), 200


@app.get("/api/crystals/<int:cid>")             # READ (one)
def get_one(cid):
    rec = _store.get(cid)
    return (jsonify(rec), 200) if rec else (jsonify(error="Not found"), 404)


@app.put("/api/crystals/<int:cid>")             # UPDATE
def update(cid):
    with _lock:
        rec = _store.get(cid)
        if not rec:
            return jsonify(error="Not found"), 404
        data = request.get_json(silent=True) or {}
        for f in ("name", "category", "description", "price"):
            if f in data:
                rec[f] = data[f]
    return jsonify(rec), 200


@app.delete("/api/crystals/<int:cid>")          # DELETE
def delete(cid):
    with _lock:
        if cid not in _store:
            return jsonify(error="Not found"), 404
        del _store[cid]
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5099")), debug=False)
