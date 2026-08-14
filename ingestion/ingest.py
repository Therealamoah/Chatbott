import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.loaders import load_all_chunks
from ingestion.embedder import get_collection, ingest_documents, collection_stats


def main():
    print("Loading knowledge base chunks...")
    chunks = load_all_chunks()
    print(f"Loaded {len(chunks)} chunks from clean KB")

    print("\nInitializing ChromaDB collection...")
    collection = get_collection()

    print("Ingesting documents...")
    ingest_documents(chunks, collection)

    print("\nFinal stats:")
    collection_stats(collection)
    print("Done.")


if __name__ == "__main__":
    main()
