import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS

from ingestion.embedder import get_collection
from retrieval.router import process_query, RetrievalResult
from generation.prompt import build_system_prompt, load_skill
from generation.generate import generate_response

app = Flask(__name__)
frontend_url = os.getenv("FRONTEND_URL")
CORS(app, origins=frontend_url if frontend_url else "*")

_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        try:
            col = get_collection()
            if col.count() > 0:
                _collection = col
        except Exception:
            pass
    return _collection


@app.get("/health")
def health():
    col = _get_collection()
    return jsonify({
        "status": "ok",
        "rag": col is not None,
        "documents": col.count() if col else 0,
    })


@app.post("/chat")
def chat():
    body = request.get_json(force=True)
    history: list[dict] = body.get("history", [])

    if not history or history[-1].get("role") != "user":
        return jsonify({"error": "history must end with a user message"}), 400

    user_query = history[-1]["content"]
    prior_history = history[:-1]

    col = _get_collection()

    if col:
        retrieval = process_query(user_query, col)
        if retrieval.bypassed:
            return jsonify({"reply": retrieval.response})
        system_prompt = build_system_prompt(retrieved_context=retrieval.context)
    else:
        skill_content = load_skill()
        system_prompt = (
            "You are MediGuide AI, an AI Hospital Inquiry Assistant.\n\n"
            f"{skill_content}\n\n"
            "Always respond in the same language the user uses. Be professional, calm, and helpful."
        )

    reply = generate_response(
        system_prompt=system_prompt,
        user_query=user_query,
        conversation_history=prior_history,
    )
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting MediGuide AI server on http://localhost:{port}")
    _get_collection()
    app.run(host="0.0.0.0", port=port, debug=False)
