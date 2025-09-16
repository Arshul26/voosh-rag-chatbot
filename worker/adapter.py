from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.route("/embed", methods=["POST"])
def embed():
    data = request.json
    text = data.get("text") or data.get("texts")
    if isinstance(text, list):
        vecs = model.encode(text).tolist()
        return jsonify({"embeddings": vecs})
    vec = model.encode(text).tolist()
    return jsonify({"embedding": vec})

if __name__ == "__main__":
    app.run(port=5001, host="0.0.0.0")
