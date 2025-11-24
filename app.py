import os
import threading
import numpy as np
from flask import Flask, request, jsonify, render_template

# ---------------------------
# Config
# ---------------------------
DATA_DIR = os.environ.get("RAG_DATA_DIR", "data")
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-2.5-flash")
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyDqI2y9hM97eWENW0KxY5zVO3MNYKMotcw") or os.environ.get("GEMINI_API_KEY")

# ---------------------------
# Flask + globals
# ---------------------------
app = Flask(__name__)
os.makedirs(DATA_DIR, exist_ok=True)

_lock = threading.Lock()

# ---------------------------
# Pages
# ---------------------------
@app.get("/")
def home():
    return jsonify({"status": "ok"})

# ---------------------------
# APIs
# ---------------------------
@app.get("/health")
def health():
    with _lock:
        return jsonify({"status": "ok"})

@app.post("/upload")
def upload():
    return jsonify({"saved": "saved bla bla"})

@app.post("/reindex")
def reindex():
    return jsonify({"docs_indexed": "Docs indexed"})

@app.post("/ask")
def ask():
    return jsonify({"question": "question"})

# ---------------------------
# Start
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
