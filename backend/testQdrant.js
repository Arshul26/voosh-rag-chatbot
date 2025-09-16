const { QdrantClient } = require('@qdrant/js-client-rest');

const client = new QdrantClient({
    url: process.env.QDRANT_URL,
    apiKey: process.env.QDRANT_API_KEY,
    checkCompatibility: false
});

(async () => {
    try {
        const res = await client.search("news_articles", {
            vector: Array(384).fill(0), // dummy vector
            limit: 1
        });
        console.log("Qdrant search result:", res);
    } catch (err) {
        console.error("Error connecting to Qdrant:", err);
    }
})();
