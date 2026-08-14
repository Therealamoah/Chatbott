import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingestion.config import KB_JSON_PATH, CHUNK_SIZE, CHUNK_OVERLAP


_splitter = None


def _get_splitter():
    global _splitter
    if _splitter is None:
        _splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " "],
        )
    return _splitter


def load_clean_kb() -> dict:
    with open(KB_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _split_text(text: str, metadata: dict) -> list[dict]:
    splitter = _get_splitter()
    texts = splitter.split_text(text)
    if not texts:
        return []
    return [{"text": t, "metadata": dict(metadata)} for t in texts]


def create_department_chunks(department: dict) -> list[dict]:
    chunks = []
    dept_name = department["department"]

    main_text = (
        f"Department: {dept_name}\n"
        f"Location: {department.get('location', '')}\n"
        f"Hours: {format_hours(department.get('hours', {}))}\n"
        f"Contact: {department.get('contact', '')}\n"
        f"NHIS Accepted: {department.get('nhis_accepted', False)}\n"
        f"Services: {', '.join(department.get('services', []))}"
    )

    chunks.extend(_split_text(main_text, {
        "type": "department",
        "department": dept_name,
        "source": dept_name,
    }))

    if department.get("description"):
        chunks.extend(_split_text(department["description"], {
            "type": "department_description",
            "department": dept_name,
            "source": dept_name,
        }))

    if department.get("nhis_notes"):
        chunks.extend(_split_text(department["nhis_notes"], {
            "type": "nhis_info",
            "department": dept_name,
            "source": dept_name,
        }))

    return chunks


def create_faq_chunks(faq: dict) -> list[dict]:
    text = f"Q: {faq['question']}\nA: {faq['answer']}"
    return _split_text(text, {
        "type": "faq",
        "department": faq.get("department", "General"),
        "topic": faq.get("topic", "general"),
        "faq_id": faq.get("id", ""),
    })


def format_hours(hours: dict) -> str:
    if not hours:
        return "Not specified"
    parts = []
    for day, value in hours.items():
        if isinstance(value, str):
            parts.append(f"{day.capitalize()}: {value}")
    return " | ".join(parts)


def load_all_chunks() -> list[dict]:
    kb = load_clean_kb()
    chunks = []

    for dept in kb.get("departments", []):
        chunks.extend(create_department_chunks(dept))

    for faq in kb.get("faqs", []):
        chunks.extend(create_faq_chunks(faq))

    return chunks
