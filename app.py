# app.py
from flask import Flask, request, jsonify
from transformers import pipeline
from PIL import Image
import requests, io, logging, os, base64

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# модель
MODEL_NAME = "nlpconnect/vit-gpt2-image-captioning"

# Загружаем pipeline при старте (может занять время)
logging.info("Loading captioning pipeline... (это может занять ~1-2 минуты)")
captioner = pipeline("image-to-text", model=MODEL_NAME)
logging.info("Model loaded.")

def load_image_from_url_or_b64(image_url_or_b64):
    # если data:base64
    if isinstance(image_url_or_b64, str) and image_url_or_b64.startswith("data:"):
        header, b64 = image_url_or_b64.split(",", 1)
        data = base64.b64decode(b64)
        return Image.open(io.BytesIO(data)).convert("RGB")
    # иначе считаем, что это URL
    resp = requests.get(image_url_or_b64, timeout=20)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")

@app.route("/analyze-photo", methods=["POST"])
def analyze_photo():
    try:
        data = request.get_json(force=True)
        logging.info("Received request JSON: %s", data)
        image_url = data.get("image_url") or data.get("image")
        if not image_url:
            return jsonify({"error":"image_url is required"}), 400

        try:
            image = load_image_from_url_or_b64(image_url)
        except Exception as e:
            logging.exception("Failed to load image")
            return jsonify({"error":"failed_to_load_image","details": str(e)}), 400

        # запустить модель
        try:
            result = captioner(image)
            logging.info("Model raw result: %s", result)
        except Exception as e:
            logging.exception("Model inference error")
            return jsonify({"error":"model_inference_error","details": str(e)}), 500

        # result обычно list: либо list[str], либо list[dict]
        if isinstance(result, list):
            first = result[0]
            if isinstance(first, dict):
                # ключ может называться generated_text или caption
                caption = first.get("generated_text") or first.get("caption") or str(first)
            else:
                caption = first
        else:
            caption = str(result)

        return jsonify({"description": caption, "raw": result})

    except Exception as e:
        logging.exception("Server error")
        return jsonify({"error":"server_error","details": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    return "Image caption service is running."

if name == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
