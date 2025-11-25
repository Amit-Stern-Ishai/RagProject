import os
import threading
import numpy as np
from flask import Flask, request, jsonify, render_template

from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError

# app = Flask(__name__)

# Your S3 settings
S3_BUCKET = "amit-ishai-rag-bucket-2"
s3 = boto3.client("s3")

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
    return render_template("index.html")

# ---------------------------
# APIs
# ---------------------------
@app.get("/health")
def health():
    with _lock:
        return jsonify({"status": "ok"})

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    key = f"{file.filename}"

    try:
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=S3_BUCKET,
            Key=key,
            ExtraArgs={"ContentType": file.content_type}
        )
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "File uploaded successfully",
        "s3_key": key
    })

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8009)), debug=True)
