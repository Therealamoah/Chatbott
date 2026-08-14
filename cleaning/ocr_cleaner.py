import re

OCR_FIXES = {
    r'\b0PD\b':      'OPD',
    r'\bNHl5\b':     'NHIS',
    r'\bNH1S\b':     'NHIS',
    r'\bPharrn':     'Pharm',
    r'\bphorrn':     'pharm',
    r'\bErnergency': 'Emergency',
    r'\bErner':      'Emer',
    r'\brnatem':     'matern',
    r'\brnater':     'mater',
    r'\blahoratory': 'laboratory',
    r'\bLahoratory': 'Laboratory',
    r'\bIaboratory': 'Laboratory',
    r'\bphysio1ogy': 'physiology',
    r'\b1aboratory': 'laboratory',
    r'\bNurs1ng':    'Nursing',
    r'\bnurs1ng':    'nursing',

    r'\bKor1e':      'Korle',
    r'\bAkos0mbo':   'Akosombo',
    r'\bGHana':      'Ghana',
    r'\bGhana5':     'Ghanas',
    r'\bAccna':      'Accra',
    r'\bAccia':      'Accra',
    r'\bKum0si':     'Kumasi',

    r'(\d+)\s*[.:]\s*(\d+)\s*Arn\b': r'\1:\2 AM',
    r'(\d+)\s*[.:]\s*(\d+)\s*Prn\b': r'\1:\2 PM',
    r'(\d+)\s*,\s*(\d+)\s*(am|pm)':  r'\1:\2 \3',

    r'0(?:ZO|2O)\b':   '020',
    r'O24\b':          '024',
    r'O54\b':          '054',

    r'\brnorning\b':   'morning',
    r'\bafternoon\b':  'afternoon',
    r'\brnedical\b':   'medical',
    r'\bMedica1\b':    'Medical',
    r'\bdoctor\b':     'doctor',
    r'\bdoctors\b':    'doctors',
    r'\bpatient5\b':   'patients',
    r'\bpatient\b':    'patient',
    r'\bward5\b':      'wards',
    r'\bnurse5\b':     'nurses',
}


def fix_ocr_errors(text: str) -> str:
    for pattern, replacement in OCR_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def fix_broken_words(text: str) -> str:
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    text = re.sub(r'\bout patient\b', 'outpatient', text, flags=re.IGNORECASE)
    text = re.sub(r'\bout-patient\b', 'outpatient', text, flags=re.IGNORECASE)
    text = re.sub(r'\blab oratory\b', 'laboratory', text, flags=re.IGNORECASE)
    text = re.sub(r'\bphar macy\b', 'pharmacy', text, flags=re.IGNORECASE)
    text = re.sub(r'\bemer gency\b', 'emergency', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmate rnity\b', 'maternity', text, flags=re.IGNORECASE)
    return text


def remove_ocr_garbage_lines(text: str) -> str:
    lines = text.split('\n')
    clean_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            clean_lines.append(line)
            continue

        alnum_count = sum(1 for c in stripped if c.isalnum())
        if len(stripped) > 3 and alnum_count / len(stripped) < 0.4:
            continue

        if re.search(r'(.)\1{4,}', stripped):
            continue

        if len(stripped) < 3 and not stripped.isdigit():
            continue

        clean_lines.append(line)

    return '\n'.join(clean_lines)


def clean_ocr_text(text: str) -> str:
    text = fix_ocr_errors(text)
    text = fix_broken_words(text)
    text = remove_ocr_garbage_lines(text)
    return text
