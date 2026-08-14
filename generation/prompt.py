from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parent.parent / "skill.md"


def load_skill() -> str:
    with open(SKILL_PATH, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt(retrieved_context: str = "") -> str:
    skill_content = load_skill()

    context_section = ""
    if retrieved_context:
        context_section = f"""
## Retrieved Hospital Information

Use the following verified information to answer the user's question.
ONLY use this information. Do NOT invent phone numbers, hours, or locations.

{retrieved_context}
"""

    return f"""You are MediGuide AI, an AI Hospital Inquiry Assistant. Follow these rules:

{skill_content}
{context_section}
## Final Instructions
- Answer ONLY using the retrieved information above. Never invent contacts, hours, or locations.
- If the retrieved information does not answer the question, say "I do not have that information. Please contact the hospital directly."
- Always respond in the same language the user uses.
- Be professional, calm, and helpful.
- Keep responses short and clear.
- If the user asks for emergency help, redirect to Emergency Unit or call 112/193 immediately."""
