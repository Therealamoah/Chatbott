import re

TWI_KEYWORDS = {
    "mepɛ", "mihyia", "adwenkyerɛfo", "wɔ", "wo", "yoo", "anka", "ɛyɛ",
    "sɛ", "na", "akyiri", "benkum", "nifa", "kosi", "anɔpa", "anwummerɛ",
    "da", "nnɛ", "ɔkyena", "nnansa", "awia", "anadwo",
    "akwadaa", "ayare", "ayaresa", "ba", "bɛ", "bɔ", "daabi", "de",
    "di", "dua", "dwɛ", "fa", "fie", "firi", "gye", "hɔ", "hyɛ",
    "ka", "kɔ", "kum", "kyɛ", "ma", "mɛ", "ne", "nni", "no",
    "nso", "ntɛm", "nye", "nyina", "pɛ", "sa", "so", "sɔ", "te",
    "to", "tumi", "twa", "wɔn", "yi", "bɛyɛ", "akwan", "bepadwofoɔ",
    "adwuma", "ayarefoɔ", "beaeɛ", "dan", "din", "edin", "ho",
    "nhwehwɛmu", "nkonta", "nsɛm", "ntoma", "nwura", "nyarewa",
    "odwuro", "opanyin", "asante", "medaase", "mepaakyɛw",
}

GA_KEYWORDS = {
    "mii", "afee", "ŋmɛlɛ", "gbɛ", "shia", "tswa", "kɛ", "kwra",
    "nii", "nyɛ", "wɔ", "fee", "mɔ", "hɔ", "kwɛ", "sɛ", "tɛ",
    "yɛ", "gbi", "je", "ke", "le", "mo", "na", "ne", "ni",
    "no", "nyɛmɔ", "ŋaa", "ŋoo", "sawane", "shɛ", "shwie", "tã",
    "toi", "tsɔ", "tsui", "wo", "wolo", "yaa", "yɛhwe",
}

EWE_KEYWORDS = {
    "menye", "afɔ", "ƒe", "ŋkeke", "ɣeyiɣi", "kplɔ", "ɖo", "ga",
    "kafe", "kple", "kpɔ", "le", "me", "na", "ne", "nu", "nye",
    "si", "ta", "to", "tsɔ", "va", "wo", "ɖe", "ɖo", "ɖu",
    "gbɔ", "gbɔe", "gbɔgblɔ", "gbɔna", "hedede", "hekpɔ",
    "hosital", "kɔdzo", "kplɔnya", "ŋutifafa", "nyametsotso",
    "nyateƒe", "ɔkɛ", "tede", "tsitsi", "wɔdɔ", "wɔna",
}

HAUSA_KEYWORDS = {
    "ina", "ba", "da", "ga", "ka", "ma", "na", "sa", "ta", "ya",
    "yi", "zo", "aka", "bai", "ban", "baya", "bene", "ciki",
    "daɗi", "daga", "doki", "fada", "gida", "girma", "gudu",
    "haka", "hanya", "hawan", "jiya", "jini", "jirga", "kada",
    "kama", "kana", "kaza", "kuma", "kunya", "lafiya", "lokaci",
    "magana", "maganin", "mara", "maza", "na'am", "natsuwa",
    "rashin", "ruwa", "sai", "sama", "sanda", "sanyi", "soma",
    "suka", "sun", "suna", "tare", "tashi", "wani", "wata",
    "wuri", "yana", "yaƙi", "yara", "yau", "za", "zafi",
    "zamani", "zama", "zane",
}

DAGBANI_KEYWORDS = {
    "mama", "a", "ba", "be", "bo", "che", "da", "di", "din", "do",
    "du", "ga", "gba", "gbi", "gbu", "ha", "ka", "ko", "kpa",
    "kpi", "ku", "la", "li", "lo", "ma", "mi", "mo", "mu",
    "na", "ŋma", "ŋme", "nya", "nyo", "pa", "pi", "pu",
    "sa", "si", "so", "su", "ta", "ti", "to", "tu",
    "yi", "yu", "za", "zɔ", "zu",
}

EMERGENCY_KEYWORDS = {
    "emergency", "accident", "unconscious", "bleeding", "chest pain",
    "heart attack", "stroke", "seizure", "breathing", "choking",
    "overdose", "suicide", "severe", "urgent", "trauma",
    "ambulance", "critical", "life-threatening",
    "koko", "hia", "ntɛm", "awerɛho", "yaw", "yare",
}

NHIS_KEYWORDS = {
    "nhis", "insurance", "health insurance", "premium", "registration",
    "renew", "renewal", "ghana card", "national health",
}

LOCATION_KEYWORDS = {
    "where", "location", "find", "located", "near", "direction",
    "block", "floor", "entrance", "wɔ he", "beaeɛ", "gbɛ",
    "afi", "wuri", "zabuɣu",
}

HOURS_KEYWORDS = {
    "open", "close", "hours", "time", "24", "hour", "when",
    "operating", "working hour", "bue", "tumi", "ɛbue",
    "ɣeyiɣi", "lokaci",
}

CONTACT_KEYWORDS = {
    "contact", "call", "phone", "number", "reach", "mobile",
    "telephone", "frɛ", "telephone", "lambar waya",
}

DEPARTMENT_KEYWORDS = {
    "opd": "OPD",
    "outpatient": "OPD",
    "pharmacy": "Pharmacy",
    "drug": "Pharmacy",
    "laboratory": "Laboratory",
    "lab": "Laboratory",
    "test": "Laboratory",
    "blood": "Laboratory",
    "maternity": "Maternity",
    "pregnancy": "Maternity",
    "antenatal": "Maternity",
    "delivery": "Maternity",
    "childbirth": "Maternity",
    "nhis": "NHIS",
    "insurance": "NHIS",
    "emergency": "Emergency",
    "accident": "Emergency",
    "casualty": "Emergency",
}


def detect_language(text: str) -> str:
    words = set(re.findall(r"[a-zA-ZɛɔƐƆɖƒɣŋɄɅ]+", text.lower()))

    if not words:
        return "english"

    twi_score = len(words & TWI_KEYWORDS)
    ga_score = len(words & GA_KEYWORDS)
    ewe_score = len(words & EWE_KEYWORDS)
    hausa_score = len(words & HAUSA_KEYWORDS)
    dagbani_score = len(words & DAGBANI_KEYWORDS)

    scores = {
        "twi": twi_score,
        "ga": ga_score,
        "ewe": ewe_score,
        "hausa": hausa_score,
        "dagbani": dagbani_score,
    }

    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return best

    return "english"


def classify_intent(text: str) -> str:
    text_lower = text.lower()

    if any(kw in text_lower for kw in EMERGENCY_KEYWORDS):
        return "emergency"

    if any(kw in text_lower for kw in NHIS_KEYWORDS):
        return "nhis"

    if any(kw in text_lower for kw in LOCATION_KEYWORDS):
        return "location"

    if any(kw in text_lower for kw in HOURS_KEYWORDS):
        return "hours"

    if any(kw in text_lower for kw in CONTACT_KEYWORDS):
        return "contact"

    for keyword, dept in DEPARTMENT_KEYWORDS.items():
        if keyword in text_lower:
            return f"department:{dept}"

    return "general"


def detect_department(text: str) -> str | None:
    text_lower = text.lower()
    for keyword, dept in DEPARTMENT_KEYWORDS.items():
        if keyword in text_lower:
            return dept
    return None
