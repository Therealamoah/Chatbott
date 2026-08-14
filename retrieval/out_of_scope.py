import re

OUT_OF_SCOPE_KEYWORDS = [
    "politics", "politician", "vote", "election", "president", "parliament",
    "sport", "football", "soccer", "basketball", "tennis", "cricket", "match", "game",
    "entertainment", "movie", "music", "song", "celebrity", "actor",
    "religion", "prayer", "church", "mosque", "bible", "quran", "god",
    "cryptocurrency", "bitcoin", "ethereum", "crypto", "blockchain", "nft",
    "coding", "programming", "python", "javascript", "html", "software",
    "hacking", "hack", "crack", "exploit", "malware", "virus",
    "gambling", "casino", "bet", "lottery", "slot",
    "illegal", "drug", "weapon", "gun", "knife",
    "adult", "porn", "nsfw", "nude",
    "personal opinion", "i think", "in my opinion",
    "financial advice", "invest", "stock", "trading", "forex",
    "legal advice", "lawsuit", "sue", "attorney", "lawyer",
]

OUT_OF_SCOPE_PATTERNS = [
    r"\b(?:who\s+will\s+win|who\s+is\s+the\s+best|predict\s+the)\b",
    r"\b(?:teach\s+me\s+how\s+to\s+hack|how\s+do\s+i\s+hack)\b",
    r"\b(?:make\s+me\s+a\s+website|write\s+code\s+for)\b",
    r"\b(?:what\s+is\s+the\s+meaning\s+of\s+life|tell\s+me\s+a\s+joke)\b",
    r"\b(?:recommend\s+a\s+(?:movie|song|book|game))\b",
]

OUT_OF_SCOPE_RESPONSES = {
    "english": "I'm sorry, but I can only assist with healthcare and hospital-related questions.",
    "twi": "Ɛfirɛ me, nanso mɛtumi aboa w'ayaresa ne asopitadwuma ho nsɛm nkutoo.",
    "ga": "Jaje, shi moŋ miinyɛɛ nyɛmi ashwɛ lɛ he jogbaŋŋ yɛ saji ni kpa yelikɛbɔmɔ kɛ asopita he.",
    "ewe": "Taflatsɛ, ke nye ŋusẽ tsona ɖe aɖaŋu kple ɣeyiɣi siwo ku ɖe dɔléle kple kɔdzi dzi ko.",
    "hausa": "Yi hakuri, amma zan iya taimakawa ne kawai game da lafiya da tambayoyi masu alaka da asibiti.",
    "dagbani": "Nyarigi ma, amaa n ni tooi sɔŋ a doro mini ashibiti yɛltɔɣa zaa."
}


def is_out_of_scope(text: str) -> bool:
    text_lower = text.lower()

    for keyword in OUT_OF_SCOPE_KEYWORDS:
        if keyword in text_lower:
            return True

    for pattern in OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, text_lower):
            return True

    return False


def get_refusal_response(language: str = "english") -> str:
    return OUT_OF_SCOPE_RESPONSES.get(language, OUT_OF_SCOPE_RESPONSES["english"])
