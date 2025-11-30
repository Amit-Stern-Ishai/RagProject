import os
import threading
import numpy as np
from flask import Flask, request, jsonify, render_template
import json

from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError

from TextProcessing import convert_uploaded_json_to_fileobj

# ---------------------------
# Config
# ---------------------------
REGION   = "us-east-1"
S3_BUCKET = "amit-ishai-rag-bucket-2"
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"  # <-- put your exact Sonnet model ID here
KNOWLEDGE_BASE_ID = "OANROOCWZJ"

s3 = boto3.client("s3")
client = boto3.client("bedrock-agent-runtime")
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# ---------------------------
# Flask + globals
# ---------------------------
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

    for file_to_upload in files_to_upload:
        key = file_to_upload.name

        try:
            s3.upload_fileobj(
                Fileobj=file_to_upload,
                Bucket=S3_BUCKET,
                Key=key,
                ExtraArgs={"ContentType": file_to_upload.content_type}
            )
        except ClientError as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "File uploaded successfully"
    })

@app.post("/reindex")
def reindex():
    return jsonify({"docs_indexed": "Docs indexed"})

@app.post("/ask")
def ask():
    data = request.get_json()  # read JSON body
    question = data.get("question")  # extract the prompt text

    if not question:
        return {"error": "Missing question"}, 400

    answer, chunks = claude_complete(prompt=question)

    return jsonify({"answer": answer, "chunks": chunks})

def claude_complete(prompt: str):
    context = ""

    response = client.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={"text": prompt}
    )

    chunks = []

    for item in response["retrievalResults"]:
        result = item['content']['text']
        context += f"{result}\n"
        chunks.append(result)

    final_prompt = f'''
                        You are a professional chef giving advice with recipes. Please be helpful and creative. Base all
                        food advice on the context. Encourage the user to be creative and try new combinations. Answer in a human like fashion.
                        Please note: all dietary advice should abide by kosher law, meaning:
                        1. No pig
                        2. No shellfish
                        3. No mixing of dairy and meat
                        Prompt: {prompt}
                        Context: {context}
                        '''
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2,
        # optional "system": "You are a concise assistant.",
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": final_prompt}]}
        ]
    }

    try:
        resp = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(body))
        payload = resp["body"].read() if hasattr(resp.get("body"), "read") else resp["body"]
        data = json.loads(payload)

        # Anthropic messages return a list of content blocks; join any text blocks.
        parts = data.get("content", [])
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        return text.strip(), chunks

    except ClientError as e:
        raise RuntimeError(f"Bedrock InvokeModel failed: {e.response.get('Error', {}).get('Message')}") from e

# ---------------------------
# Start
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8009)), debug=True)
