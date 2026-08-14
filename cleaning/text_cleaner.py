import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
    return text.strip()


def remove_page_artifacts(text: str) -> str:
    patterns = [
        r'page\s+\d+\s+of\s+\d+',
        r'^\s*\d+\s*$',
        r'confidential\s*[-–]\s*internal\s+use\s+only',
        r'printed\s+on\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'©\s*\d{4}.*?hospital',
        r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def fix_encoding(text: str) -> str:
    replacements = {
        '\u2019': "'",
        '\u2018': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2013': '-',
        '\u2014': '-',
        '\u00a0': ' ',
        '\u2022': '-',
        '\u00b7': '-',
        '\ufeff': '',
        '\x00': '',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def remove_special_chars(text: str, keep_ghanaian: bool = True) -> str:
    if keep_ghanaian:
        ghanaian_chars = 'ɛɔƐƆɖƒɣŋɄɅɐɑɒɓɔɕɖɗɘəɚɛɜɝɞɟɠɡɢɣɤɥɦɧɨɩɪɫɬɭɮɯɰɱɲɳɴɵɶɷɸɹɺɻɼɽɾɿ'
        pattern = f'[^\\w\\s\\-.,;:!?/()\'"@+{ghanaian_chars}]'
        text = re.sub(pattern, ' ', text)
    else:
        text = re.sub(r'[^\w\s\-.,;:!?/()\'"@+]', ' ', text)
    return text


def lowercase_except_acronyms(text: str) -> str:
    acronyms = {
        'OPD', 'NHIS', 'ICU', 'HDU', 'A&E', 'ENT', 'OBGYN',
        'OB/GYN', 'ER', 'OR', 'GP', 'TB', 'HIV', 'AIDS',
        'ANC', 'PNC', 'LMIC', 'GHS', 'NLM', 'WHO', 'CDC',
        'BP', 'RBS', 'FBS', 'HBA1C', 'ECG', 'EEG', 'MRI',
        'CT', 'XR', 'USS', 'IV', 'IM', 'SC', 'PO',
        'NITA', 'MOH', 'KATH', 'KBTH', 'CCTH', 'TTH',
        'LEKMA', 'LEKMA HOSPITAL', '37 MILITARY',
    }

    words = text.split()
    result = []
    for word in words:
        clean_word = re.sub(r'[^\w&/]', '', word.upper())
        if clean_word in acronyms:
            result.append(word.upper() if word == clean_word else word)
        else:
            result.append(word.lower() if word.isupper() and len(word) > 2 else word)
    return ' '.join(result)


def clean_raw_text(text: str, keep_ghanaian: bool = True) -> str:
    text = fix_encoding(text)
    text = remove_page_artifacts(text)
    text = remove_special_chars(text, keep_ghanaian=keep_ghanaian)
    text = normalize_whitespace(text)
    return text


def extract_sections(text: str) -> dict:
    section_patterns = {
        'services':       r'(?:services?|we offer|what we do)[:\s]*(.+?)(?=\n[A-Z]|\Z)',
        'hours':          r'(?:hours?|opening times?|working hours?)[:\s]*(.+?)(?=\n[A-Z]|\Z)',
        'location':       r'(?:location|address|where to find us|directions?)[:\s]*(.+?)(?=\n[A-Z]|\Z)',
        'contact':        r'(?:contact|phone|telephone|call us)[:\s]*(.+?)(?=\n[A-Z]|\Z)',
        'nhis':           r'(?:nhis|insurance|payment)[:\s]*(.+?)(?=\n[A-Z]|\Z)',
        'requirements':   r'(?:requirements?|what to bring|documents?)[:\s]*(.+?)(?=\n[A-Z]|\Z)',
    }

    sections = {}
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            sections[section_name] = clean_raw_text(match.group(1))

    return sections
