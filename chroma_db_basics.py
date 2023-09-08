
import chromadb

chroma_client = chromadb.Client()

# place where we store embeddings
collection = chroma_client.create_collection(name = "my_collection")
collection.add(
    documents = ["this is a test", "this is not a test"],
    metadatas = [{"source": "test true"},
                 {"source": "test false"}],
    ids = ["id1", "id2"],
)

# performs cosine similarity: dict contains attribute 'distances'
results = collection.query(
    query_texts = ["is this a test?"],
    n_results = 2
)
print(results)
