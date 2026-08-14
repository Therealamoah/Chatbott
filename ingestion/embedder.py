import chromadb
from chromadb.utils import embedding_functions
from ingestion.config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL


def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def get_client() -> chromadb.PersistentClient:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection(client: chromadb.PersistentClient = None):
    if client is None:
        client = get_client()
    ef = get_embedding_function()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def ingest_documents(chunks: list[dict], collection=None):
    if collection is None:
        collection = get_collection()

    existing = collection.count()
    if existing > 0:
        print(f"Collection already has {existing} documents. Clearing...")
        collection.delete(ids=collection.get()["ids"])

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i:05d}")
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Ingested {len(chunks)} document chunks into '{COLLECTION_NAME}'")
    return collection


def collection_stats(collection=None):
    if collection is None:
        collection = get_collection()
    count = collection.count()
    print(f"Collection '{COLLECTION_NAME}': {count} documents")
    return count
