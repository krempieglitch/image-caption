# app.py
from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# твой токен Hugging Face (лучше в ENV переменную!)
HF_API_KEY = "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"

HF_MODEL_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"

@app.route("/analyze-photo", methods=["POST"])
def analyze_photo():
    try:
        data = request.json
        image_base64 = data.get("image_base64")

        if not image_base64:
            return jsonify({"error": "No image provided"}), 400

        # Декодируем base64 → отправляем на Hugging Face
        image_bytes = base64.b64decode(image_base64)

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}"
        }

        response = requests.post(
            HF_MODEL_URL,
            headers=headers,
            data=image_bytes
        )

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
            return jsonify({"caption": caption})

        return jsonify({"error": "Unexpected response", "details": result}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if name == "__main__":
    app.run(host="0.0.0.0", port=5000)
