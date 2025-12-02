import os
from flask import Flask, request, jsonify
from flask import render_template

from bedrock_util import get_grounded_answer
from s3_util import upload_files
from text_processing import convert_uploaded_json_to_fileobj

app = Flask(__name__)

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
    return jsonify({"status": "ok"})

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    files_to_upload = convert_uploaded_json_to_fileobj(file)
    upload_files(files_to_upload)
    return jsonify({
        "message": "File uploaded successfully"
    })

@app.post("/ask")
def ask():
    data = request.get_json()  # read JSON body
    question = data.get("question")  # extract the prompt text

    if not question:
        return {"error": "Missing question"}, 400

    answer, chunks = get_grounded_answer(prompt=question)

    return jsonify({"answer": answer, "chunks": chunks})

# ---------------------------
# Start
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8009)), debug=True)
