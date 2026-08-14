import re

EMERGENCY_PATTERNS = [
    r"\b(?:chest\s* pain|heart\s* attack|cardiac)\b",
    r"\b(?:difficult\s* breath|shortness\s* of\s* breath|can'?t\s* breathe|choking)\b",
    r"\b(?:severe\s* bleeding|bleeding\s* heavily|haemorrhage|hemorrhage)\b",
    r"\b(?:unconscious|passed\s* out|fainted|lost\s* consciousness)\b",
    r"\b(?:stroke|seizure|fitting|convuls)\b",
    r"\b(?:suicid|self-?harm|want\s* to\s* die)\b",
    r"\b(?:accident|car\s* crash|road\s* traffic|mvc|rti)\b",
    r"\b(?:severe\s* pain|excruciating|agonizing)\b",
    r"\b(?:pregnancy\s* emergenc|labour\s* pain|water\s* broke|heavy\s* bleeding\s* pregnant)\b",
    r"\b(?:allergic\s* reaction|anaphylax|difficulty\s* swallowing)\b",
    r"\b(?:burn\s* severe|third.degree|electrocution|drowning)\b",
    r"\bpoisoning|overdose\b",
    r"\b(?:193|112|999)\b",
]

EMERGENCY_RESPONSES = {
    "english": (
        "Your symptoms may require urgent medical attention. Please visit the nearest "
        "Emergency Unit immediately or call 112 (National Emergency) or 193 (Ambulance)."
    ),
    "twi": (
        "Wo yare no hia nnuruyɛ ho mmɔden a ɛho hia. Yɛsrɛ sɛ kɔ Ɔhaw Ho Dwumadibea a "
        "ɛbɛn wo hɔ ntɛm anaasɛ frɛ 112 (Ɔman Ɔhaw) anaa 193 (Ambulance)."
    ),
    "ga": (
        "Onyɛ ni mli hi feo ni ehia saji awoho yelikɛbɔmɔ. Nyɛ fee nyɛya Emergency Unit "
        "ni ete kpalamɔ lɛ nɔ kwraa loo nyɛ tsɛ 112 (National Emergency) loo 193 (Ambulance)."
    ),
    "ewe": (
        "Wò dɔléle áte ŋu áhiã numakpekpe. Taflatsɛ yi Kpɔɖeamedziƒe si gbɔ wò le enu "
        "enumake alo yɔ 112 (Dukɔ Ƒe Kpɔɖeame) alo 193 (Ambulancedziƒe)."
    ),
    "hausa": (
        "Alamomin ku na iya buƙatar kulawar gaggawa. Da fatan za ku je Sashen Gaggawa "
        "mafi kusa nan take ko kuma ku kira 112 (Gaggawa ta Ƙasa) ko 193 (Motar Asibiti)."
    ),
    "dagbani": (
        "A doriti maa ni tooi bɔri yomyom dɔŋ. Pahimi ni a tam yomyom shee din be yina "
        "bee a bolimi 112 (Tiŋa yomyom) bee 193 (Ambulance)."
    ),
}


def contains_emergency(text: str) -> bool:
    text_lower = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def get_emergency_response(language: str = "english") -> str:
    return EMERGENCY_RESPONSES.get(language, EMERGENCY_RESPONSES["english"])
