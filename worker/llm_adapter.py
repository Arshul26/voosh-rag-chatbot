# worker/llm_adapter.py
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()  # loads GEMINI_API_KEY from worker/.env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

app = Flask(__name__)

if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
else:
    model = None

@app.route("/llm", methods=["POST"])
def llm():
    data = request.json or {}
    prompt = data.get("prompt", "")
    if not GEMINI_API_KEY or model is None:
        return jsonify({"text": "No GEMINI_API_KEY set or model unavailable."}), 500
    try:
        # generate content (simple usage)
        resp = model.generate_content(prompt)
        # resp.text is expected to contain the generated string
        text = getattr(resp, "text", None)
        if text is None:
            # fallback - convert response to string if structure differs
            text = str(resp)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5002, host="0.0.0.0")


