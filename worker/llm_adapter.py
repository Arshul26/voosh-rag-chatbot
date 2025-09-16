from flask import Flask, request, jsonify
import os

app = Flask(__name__)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/llm", methods=["POST"])
def llm():
    data = request.json
    prompt = data.get("prompt", "")
    if GEMINI_API_KEY:
        # Implement Gemini call here later
        return jsonify({"text": "Gemini placeholder response."})
    return jsonify({"text": "Mock answer: " + prompt[:200]})

if __name__ == "__main__":
    app.run(port=5002, host="0.0.0.0")
