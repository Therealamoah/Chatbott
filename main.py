import os
import sys
from dotenv import load_dotenv

load_dotenv()

from ingestion.embedder import get_collection, collection_stats
from retrieval.router import process_query, RetrievalResult
from generation.prompt import build_system_prompt
from generation.generate import generate_response


def ensure_collection():
    try:
        collection = get_collection()
        count = collection.count()
        if count == 0:
            print("Vector store is empty. Run ingestion first:")
            print("  python scripts/ingest_kb.py")
            print("Or: python -m ingestion.ingest\n")
        else:
            print(f"Vector store ready: {count} documents loaded")
        return collection
    except Exception as e:
        print(f"Warning: Could not initialize vector store: {e}")
        print("RAG features will be disabled.\n")
        return None


def chat():
    collection = ensure_collection()
    conversation_history = []

    print("MediGuide AI - Hospital Inquiry Assistant (RAG)")
    print("Type 'exit' to quit | 'status' to check system\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Take care.")
            break

        if not user_input:
            continue

        if user_input.lower() == "status":
            if collection:
                c = collection.count()
                print(f"Vector store: {c} documents | Model: {os.getenv('OPENROUTER_MODEL', 'google/gemma-4-31b-it:free')}\n")
            else:
                print("Vector store: not initialized\n")
            continue

        if collection:
            retrieval = process_query(user_input, collection)

            if retrieval.bypassed:
                print(f"MediGuide: {retrieval.response}\n")
                continue

            system_prompt = build_system_prompt(retrieved_context=retrieval.context)
        else:
            from generation.prompt import load_skill
            skill_content = load_skill()
            system_prompt = f"""You are MediGuide AI, an AI Hospital Inquiry Assistant. Follow these rules:

{skill_content}

Remember: Always respond in the same language the user uses. Be professional, calm, and helpful."""
            retrieval = RetrievalResult()

        try:
            reply = generate_response(
                system_prompt=system_prompt,
                user_query=user_input,
                conversation_history=conversation_history,
            )
            print(f"MediGuide: {reply}\n")
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"Error: {e}\n")


def main():
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not set in .env file")
        print("Please edit .env and add your API key")
        sys.exit(1)

    chat()


if __name__ == "__main__":
    main()
