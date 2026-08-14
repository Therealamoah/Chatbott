from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT / "chroma_db"
KB_JSON_PATH = ROOT / "data" / "knowledge_base_clean.json"

COLLECTION_NAME = "mediguide_kb"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128
TOP_K_RESULTS = 3

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
