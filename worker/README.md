# 🧠 Worker Services – Embedding & LLM Adapters

This folder contains **two lightweight Python Flask APIs** that act as adapters for the backend.  
They are essential for the **RAG (Retrieval-Augmented Generation) pipeline**.

---

## 📌 Overview

1. **`adapter.py`**  
   - Converts input text into embeddings (vector representation).  
   - Used by the backend to query Qdrant for similar news articles.  
   - You can use **Jina Embeddings**, **SentenceTransformers**, or any open-source embedding model.

2. **`llm_adapter.py`**  
   - Takes the **prompt** (built by the backend) and calls **Google Gemini API** (or any other LLM).  
   - Returns the generated text back to the backend.

---

## ⚙️ Setup Instructions

### 1. Install Dependencies
> Run this in the `worker/` folder.

```bash
pip install -r requirements.txt

```
---
### 2. Run two separate terminals
```bash
cd worker
venv\Scripts\Activate

#In one terminal run
python adapter.py
#And in another
python llm_adapter.py
