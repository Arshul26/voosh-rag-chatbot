# worker/ingest.py
import requests
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import re, time

# ----------------------------- CONFIG -----------------------------
QDRANT_URL = "https://aca9274a-6430-4023-9279-e0ce1ecbb869.us-east-1-1.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Hi0SEAiR5h2m76YITXnath_WUSV-UoAEjTb2zFfVkVA"
COLLECTION = "news_articles"
MODEL_NAME = "all-MiniLM-L6-v2"

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.theguardian.com/world/rss",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html"
]

# ----------------------------- INITIALIZE -----------------------------
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer(MODEL_NAME)

# ----------------------------- HELPERS -----------------------------
def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def fetch_articles_from_rss(url, max_articles=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"⚠️ Failed to fetch RSS feed {url}: {e}")
        return []

    soup = BeautifulSoup(r.content, "xml")
    items = soup.find_all('item')[:max_articles]
    articles = []

    for it in items:
        title = it.find('title').text if it.find('title') else ''
        link = it.find('link').text if it.find('link') else ''
        try:
            page = requests.get(link, headers=headers, timeout=10)
            ps = BeautifulSoup(page.content, 'html.parser').find_all('p')
            text = " ".join([p.get_text() for p in ps])
            text = clean_text(text)
            if len(text) > 200:
                articles.append({'title': title, 'link': link, 'text': text})
        except Exception as e:
            print(f"fetch error for {link}: {e}")

    return articles

def upsert_to_qdrant(items):
    # Try to create collection; ignore if it already exists
    try:
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
        )
        print(f"✅ Created collection '{COLLECTION}' in Qdrant Cloud.")
    except Exception as e:
        if "already exists" in str(e):
            print(f"ℹ️ Collection '{COLLECTION}' already exists, reusing it.")
        else:
            raise e

    # Prepare points
    points = []
    for i, art in enumerate(items):
        vec = model.encode(art['text']).tolist()
        points.append(
            models.PointStruct(
                id=i + int(time.time()),
                vector=vec,
                payload={"title": art['title'], "link": art['link'], "text": art['text'][:10000]}
            )
        )

    # Upload points
    qdrant.upsert(
        collection_name=COLLECTION,
        points=points
    )
    print(f"✅ Upserted {len(points)} articles to Qdrant Cloud.")

# ----------------------------- MAIN -----------------------------
if __name__ == "__main__":
    all_articles = []
    for feed in RSS_FEEDS:
        arts = fetch_articles_from_rss(feed, max_articles=20)
        print(f"📄 Fetched {len(arts)} articles from {feed}")
        all_articles.extend(arts)
        if len(all_articles) >= 60:
            break

    if not all_articles:
        print("⚠️ No articles fetched. Exiting.")
    else:
        print(f"📊 Total articles ready to upsert: {len(all_articles)}")
        upsert_to_qdrant(all_articles[:60])



# # worker/ingest.py
# import requests 
# from bs4 import BeautifulSoup
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# from sentence_transformers import SentenceTransformer
# import re, time

# # ✅ Use Qdrant Cloud (replace with your actual cluster URL + API key)
# QDRANT_URL = "https://aca9274a-6430-4023-9279-e0ce1ecbb869.us-east-1-1.aws.cloud.qdrant.io"
# QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Hi0SEAiR5h2m76YITXnath_WUSV-UoAEjTb2zFfVkVA"
# COLLECTION = "news_articles"
# MODEL_NAME = "all-MiniLM-L6-v2"

# # ✅ Connect to Qdrant Cloud with API key
# qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
# model = SentenceTransformer(MODEL_NAME)

# # ✅ Reliable public news RSS feeds
# RSS_FEEDS = [
#     "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
#     "https://www.theguardian.com/world/rss",
#     "https://feeds.bbci.co.uk/news/rss.xml",
#     "https://www.cnbc.com/id/100003114/device/rss/rss.html"
# ]

# def clean_text(t):
#     t = re.sub(r'\s+', ' ', t)
#     return t.strip()

# def fetch_articles_from_rss(url, max_articles=20):
#     r = requests.get(url, timeout=20)
#     soup = BeautifulSoup(r.content, "xml")
#     items = soup.find_all('item')[:max_articles]  # ✅ use find_all (not deprecated)
#     articles = []
#     for it in items:
#         title = it.find('title').text if it.find('title') else ''
#         link = it.find('link').text if it.find('link') else ''
#         try:
#             page = requests.get(link, timeout=10)
#             ps = BeautifulSoup(page.content, 'html.parser').find_all('p')
#             text = " ".join([p.get_text() for p in ps])
#             text = clean_text(text)
#             if len(text) > 200:
#                 articles.append({'title': title, 'link': link, 'text': text})
#         except Exception as e:
#             print("fetch error", e)
#     return articles

# def upsert_to_qdrant(items):
#     # ✅ Check if collection exists, create if not
#     if not qdrant.collection_exists(COLLECTION):
#         qdrant.create_collection(
#             collection_name=COLLECTION,
#             vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
#         )
#         print(f"✅ Created collection '{COLLECTION}' in Qdrant Cloud.")
#     else:
#         print(f"ℹ️ Collection '{COLLECTION}' already exists, reusing it.")

#     # ✅ Prepare points
#     points = []
#     for i, art in enumerate(items):
#         vec = model.encode(art['text']).tolist()
#         points.append(
#             models.PointStruct(
#                 id=i + int(time.time()),
#                 vector=vec,
#                 payload={"title": art['title'], "link": art['link'], "text": art['text'][:10000]}
#             )
#         )

#     # ✅ Upload points
#     qdrant.upsert(
#         collection_name=COLLECTION,
#         points=points
#     )
#     print(f"✅ Upserted {len(points)} items to Qdrant Cloud.")

# # worker/ingest.py
# import requests 
# from bs4 import BeautifulSoup
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# from sentence_transformers import SentenceTransformer
# import re, time

# # ✅ Use Qdrant Cloud (replace with your actual cluster URL + API key)
# QDRANT_URL = "https://aca9274a-6430-4023-9279-e0ce1ecbb869.us-east-1-1.aws.cloud.qdrant.io"
# QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Hi0SEAiR5h2m76YITXnath_WUSV-UoAEjTb2zFfVkVA"
# COLLECTION = "news_articles"
# MODEL_NAME = "all-MiniLM-L6-v2"

# # ✅ Connect to Qdrant Cloud with API key
# qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
# model = SentenceTransformer(MODEL_NAME)

# # ✅ Reliable public news RSS feeds
# RSS_FEEDS = [
#     "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
#     "https://www.theguardian.com/world/rss",
#     "https://feeds.bbci.co.uk/news/rss.xml",
#     "https://www.cnbc.com/id/100003114/device/rss/rss.html"
# ]

# def clean_text(t):
#     t = re.sub(r'\s+', ' ', t)
#     return t.strip()

# def fetch_articles_from_rss(url, max_articles=20):
#     r = requests.get(url, timeout=20)
#     soup = BeautifulSoup(r.content, "xml")
#     items = soup.find_all('item')[:max_articles]  # ✅ use find_all (not deprecated)
#     articles = []
#     for it in items:
#         title = it.find('title').text if it.find('title') else ''
#         link = it.find('link').text if it.find('link') else ''
#         try:
#             page = requests.get(link, timeout=10)
#             ps = BeautifulSoup(page.content, 'html.parser').find_all('p')
#             text = " ".join([p.get_text() for p in ps])
#             text = clean_text(text)
#             if len(text) > 200:
#                 articles.append({'title': title, 'link': link, 'text': text})
#         except Exception as e:
#             print("fetch error", e)
#     return articles

# def upsert_to_qdrant(items):
#     # ✅ Check if collection exists, create if not
#     if not qdrant.collection_exists(COLLECTION):
#         qdrant.create_collection(
#             collection_name=COLLECTION,
#             vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
#         )
#         print(f"✅ Created collection '{COLLECTION}' in Qdrant Cloud.")
#     else:
#         print(f"ℹ️ Collection '{COLLECTION}' already exists, reusing it.")

#     # ✅ Prepare points
#     points = []
#     for i, art in enumerate(items):
#         vec = model.encode(art['text']).tolist()
#         points.append(
#             models.PointStruct(
#                 id=i + int(time.time()),
#                 vector=vec,
#                 payload={"title": art['title'], "link": art['link'], "text": art['text'][:10000]}
#             )
#         )

#     # ✅ Upload points
#     qdrant.upsert(
#         collection_name=COLLECTION,
#         points=points
#     )
#     print(f"✅ Upserted {len(points)} items to Qdrant Cloud.")

# if __name__ == "__main__":
#     all_articles = []
#     for feed in RSS_FEEDS:
#         arts = fetch_articles_from_rss(feed, max_articles=20)
#         print(f"Fetched {len(arts)} articles from {feed}")  # ✅ Print fetched articles per feed
#         all_articles.extend(arts)
#         if len(all_articles) >= 60:
#             break
#     print(f"Total articles ready to upsert: {len(all_articles)}")  # ✅ Print total articles before upsert

#     upsert_to_qdrant(all_articles[:60])



# def upsert_to_qdrant(items):
#     try:
#         qdrant.recreate_collection(
#             collection_name=COLLECTION,
#             vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
#         )
#     except Exception as e:
#         print("collection recreate warning:", e)

#     payloads, vectors, ids = [], [], []
#     for i, art in enumerate(items):
#         vec = model.encode(art['text']).tolist()
#         payload = {"title": art['title'], "link": art['link'], "text": art['text'][:10000]}
#         payloads.append(payload)
#         vectors.append(vec)
#         ids.append(i + int(time.time()))

#     qdrant.upload_collection(
#         collection_name=COLLECTION,
#         vectors=vectors,
#         payloads=payloads,
#         ids=ids
#     )
#     print("✅ Upserted", len(items), "items to Qdrant Cloud.")

# if __name__ == "__main__":
#     all_articles = []
#     for feed in RSS_FEEDS:
#         arts = fetch_articles_from_rss(feed, max_articles=20)
#         all_articles.extend(arts)
#         if len(all_articles) >= 60:
#             break
#     upsert_to_qdrant(all_articles[:60])



# # worker/ingest.py
# import requests 
# from bs4 import BeautifulSoup
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# from sentence_transformers import SentenceTransformer
# import re, time

# QDRANT_URL = "http://localhost:6333"
# COLLECTION = "news_articles"
# MODEL_NAME = "all-MiniLM-L6-v2"

# qdrant = QdrantClient(url=QDRANT_URL)
# model = SentenceTransformer(MODEL_NAME)

# # ✅ Replace RSS_FEEDS with reliable public feeds
# RSS_FEEDS = [
#     "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
#     "https://www.theguardian.com/world/rss",
#     "https://feeds.bbci.co.uk/news/rss.xml",
#     "https://www.cnbc.com/id/100003114/device/rss/rss.html"
# ]

# def clean_text(t):
#     t = re.sub(r'\s+', ' ', t)
#     return t.strip()

# def fetch_articles_from_rss(url, max_articles=20):
#     r = requests.get(url, timeout=20)
#     soup = BeautifulSoup(r.content, "xml")
#     items = soup.findAll('item')[:max_articles]
#     articles = []
#     for it in items:
#         title = it.find('title').text if it.find('title') else ''
#         link = it.find('link').text if it.find('link') else ''
#         try:
#             page = requests.get(link, timeout=10)
#             ps = BeautifulSoup(page.content, 'html.parser').find_all('p')
#             text = " ".join([p.get_text() for p in ps])
#             text = clean_text(text)
#             if len(text) > 200:
#                 articles.append({'title': title, 'link': link, 'text': text})
#         except Exception as e:
#             print("fetch error", e)
#     return articles

# def upsert_to_qdrant(items):
#     try:
#         qdrant.recreate_collection(
#             collection_name=COLLECTION,
#             vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
#         )
#     except Exception as e:
#         print("collection recreate warning:", e)
#     payloads, vectors, ids = [], [], []
#     for i, art in enumerate(items):
#         vec = model.encode(art['text']).tolist()
#         payload = {"title": art['title'], "link": art['link'], "text": art['text'][:10000]}
#         payloads.append(payload)
#         vectors.append(vec)
#         ids.append(i + int(time.time()))
#     qdrant.upload_collection(
#         collection_name=COLLECTION,
#         points=models.Batch(ids=ids, vectors=vectors, payloads=payloads)
#     )
#     print("Upserted", len(items), "items.")

# if __name__ == "__main__":
#     all_articles = []
#     for feed in RSS_FEEDS:
#         arts = fetch_articles_from_rss(feed, max_articles=20)
#         all_articles.extend(arts)
#         if len(all_articles) >= 60:
#             break
#     upsert_to_qdrant(all_articles[:60])


# import requests
# from bs4 import BeautifulSoup
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# from sentence_transformers import SentenceTransformer
# import re, time

# QDRANT_URL = "http://localhost:6333"
# COLLECTION = "news_articles"
# MODEL_NAME = "all-MiniLM-L6-v2"

# qdrant = QdrantClient(url=QDRANT_URL)
# model = SentenceTransformer(MODEL_NAME)

# RSS_FEEDS = [
#     "http://feeds.reuters.com/reuters/topNews",
#     "http://feeds.reuters.com/reuters/businessNews",
#     "http://feeds.reuters.com/reuters/technologyNews"
# ]

# def clean_text(t):
#     t = re.sub(r'\s+', ' ', t)
#     return t.strip()

# def fetch_articles_from_rss(url, max_articles=20):
#     r = requests.get(url, timeout=20)
#     soup = BeautifulSoup(r.content, features="xml")
#     items = soup.findAll('item')[:max_articles]
#     articles = []
#     for it in items:
#         title = it.find('title').text if it.find('title') else ''
#         link = it.find('link').text if it.find('link') else ''
#         try:
#             page = requests.get(link, timeout=10)
#             ps = BeautifulSoup(page.content, 'html.parser').find_all('p')
#             text = " ".join([p.get_text() for p in ps])
#             text = clean_text(text)
#             if len(text) > 200:
#                 articles.append({'title': title, 'link': link, 'text': text})
#         except Exception as e:
#             print("fetch error", e)
#     return articles

# def upsert_to_qdrant(items):
#     try:
#         qdrant.recreate_collection(
#             collection_name=COLLECTION,
#             vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
#         )
#     except Exception as e:
#         print("collection recreate warning:", e)
#     payloads, vectors, ids = [], [], []
#     for i, art in enumerate(items):
#         vec = model.encode(art['text']).tolist()
#         payload = {"title": art['title'], "link": art['link'], "text": art['text'][:10000]}
#         payloads.append(payload)
#         vectors.append(vec)
#         ids.append(i + int(time.time()))
#     qdrant.upload_collection(
#         collection_name=COLLECTION,
#         points=models.Batch(ids=ids, vectors=vectors, payloads=payloads)
#     )
#     print("Upserted", len(items), "items.")

# if __name__ == "__main__":
#     all_articles = []
#     for feed in RSS_FEEDS:
#         arts = fetch_articles_from_rss(feed, max_articles=20)
#         all_articles.extend(arts)
#         if len(all_articles) >= 60:
#             break
#     upsert_to_qdrant(all_articles[:60])
