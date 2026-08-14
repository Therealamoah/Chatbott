from retrieval.detector import detect_language, classify_intent, detect_department
from retrieval.emergency import contains_emergency, get_emergency_response
from retrieval.out_of_scope import is_out_of_scope, get_refusal_response
from retrieval.search import search_knowledge_base, format_context
from ingestion.embedder import get_collection


class RetrievalResult:
    def __init__(self, bypassed: bool = False, response: str | None = None):
        self.bypassed = bypassed
        self.response = response
        self.context = ""
        self.context_chunks = []
        self.language = "english"
        self.intent = "general"
        self.department = None


def process_query(query: str, collection=None) -> RetrievalResult:
    result = RetrievalResult()

    if collection is None:
        collection = get_collection()

    result.language = detect_language(query)
    result.intent = classify_intent(query)
    result.department = detect_department(query)

    if contains_emergency(query):
        result.bypassed = True
        result.response = get_emergency_response(result.language)
        return result

    if is_out_of_scope(query):
        result.bypassed = True
        result.response = get_refusal_response(result.language)
        return result

    dept_filter = result.department
    chunks = search_knowledge_base(
        query,
        collection=collection,
        department_filter=dept_filter,
    )

    result.context = format_context(chunks)
    result.context_chunks = chunks

    return result
