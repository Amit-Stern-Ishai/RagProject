import json

import boto3
from botocore.exceptions import ClientError

from environment_variables import REGION, KNOWLEDGE_BASE_ID, MODEL_ID

client = boto3.client("bedrock-agent-runtime")
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

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
                        food advice on the context. Answer in a human like fashion, but stay to the point.
                        Please note: all dietary advice should abide by kosher law, meaning:
                        1. No pig
                        2. No shellfish
                        3. No mixing of dairy and meat
                        Don't offer explanations regarding kosher laws
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
