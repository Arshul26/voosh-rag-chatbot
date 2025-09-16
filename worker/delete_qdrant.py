from qdrant_client import QdrantClient

QDRANT_URL = "https://aca9274a-6430-4023-9279-e0ce1ecbb869.us-east-1-1.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Hi0SEAiR5h2m76YITXnath_WUSV-UoAEjTb2zFfVkVA"
COLLECTION = "news_articles"

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Delete the entire collection
qdrant.delete_collection(collection_name=COLLECTION)
print(f"🗑️ Collection '{COLLECTION}' deleted successfully!")
