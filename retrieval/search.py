from ingestion.config import TOP_K_RESULTS
from ingestion.embedder import get_collection


def search_knowledge_base(
    query: str,
    collection=None,
    top_k: int = TOP_K_RESULTS,
    department_filter: str | None = None,
) -> list[dict]:
    if collection is None:
        collection = get_collection()

    where = None
    if department_filter:
        where = {"department": department_filter}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
    )

    chunks = []
    if results and results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0
            chunks.append({
                "text": doc,
                "metadata": metadata,
                "score": 1.0 - distance,
            })

    return chunks


def format_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""

    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("department", "Unknown")
        chunk_type = chunk["metadata"].get("type", "info")
        parts.append(f"[{i}] ({source} - {chunk_type}):\n{chunk['text']}")

    return "\n\n".join(parts)
