import re
from typing import Optional

GHANA_MOBILE_PREFIXES = [
    '020', '023', '024', '025', '026', '027', '028', '029',
    '050', '054', '055', '056', '057', '059',
]

GHANA_LANDLINE_PREFIXES = [
    '030', '031', '032', '033', '035', '036', '037', '038', '039', '034',
]

SPECIAL_NUMBERS = {
    '112':   'National Emergency',
    '999':   'Police Emergency',
    '193':   'Ambulance (NITA)',
    '18555': 'NHIS Call Center',
    '191':   'Fire Service',
}


def clean_phone_number(raw: str) -> Optional[str]:
    if not raw:
        return None

    cleaned = re.sub(r'[^\d+]', '', raw.strip())

    if cleaned.startswith('+233'):
        cleaned = '0' + cleaned[4:]
    elif cleaned.startswith('233'):
        cleaned = '0' + cleaned[3:]
    elif cleaned.startswith('00233'):
        cleaned = '0' + cleaned[5:]

    return cleaned if cleaned else None


def validate_ghana_phone(raw: str) -> dict:
    cleaned = clean_phone_number(raw)

    if not cleaned:
        return {'valid': False, 'number': None, 'error': 'empty or unparseable'}

    if cleaned in SPECIAL_NUMBERS:
        return {
            'valid': True,
            'number': cleaned,
            'type': 'emergency',
            'network': SPECIAL_NUMBERS[cleaned],
            'error': None
        }

    if len(cleaned) == 10 and cleaned.startswith('0'):
        prefix = cleaned[:3]

        if prefix in GHANA_MOBILE_PREFIXES:
            network = get_network(prefix)
            return {
                'valid': True,
                'number': cleaned,
                'formatted': f'{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}',
                'type': 'mobile',
                'network': network,
                'error': None
            }

        if prefix in GHANA_LANDLINE_PREFIXES:
            return {
                'valid': True,
                'number': cleaned,
                'formatted': f'{cleaned[:3]}-{cleaned[3:]}',
                'type': 'landline',
                'network': 'Ghana Telecom',
                'error': None
            }

        return {
            'valid': False,
            'number': cleaned,
            'error': f'unrecognized Ghana prefix: {prefix}'
        }

    return {
        'valid': False,
        'number': cleaned,
        'error': f'wrong length ({len(cleaned)} digits, expected 10)'
    }


def get_network(prefix: str) -> str:
    networks = {
        '024': 'MTN', '054': 'MTN', '055': 'MTN', '059': 'MTN',
        '020': 'Vodafone', '050': 'Vodafone',
        '026': 'AirtelTigo', '056': 'AirtelTigo',
        '027': 'AirtelTigo', '057': 'AirtelTigo',
        '025': 'Telecel', '028': 'Telecel',
        '023': 'MTN', '029': 'MTN',
    }
    return networks.get(prefix, 'Unknown')


def extract_phone_numbers(text: str) -> list[dict]:
    patterns = [
        r'\+233\s*\d{2}\s*\d{3}\s*\d{4}',
        r'\+233\d{9}',
        r'0\d{2}[\s\-]?\d{3}[\s\-]?\d{4}',
        r'0\d{9}',
        r'\b(?:112|999|193|18555|191)\b',
    ]

    found = []
    seen = set()

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            raw = match.group()
            result = validate_ghana_phone(raw)
            if result['number'] and result['number'] not in seen:
                seen.add(result['number'])
                result['raw'] = raw
                result['position'] = match.start()
                found.append(result)

    return found


def validate_phones_in_yaml(yaml_data: dict) -> list[dict]:
    issues = []
    phone_fields = ['contact', 'contact_main', 'contact_backup', 'phone', 'telephone']

    for field in phone_fields:
        if field in yaml_data:
            raw = str(yaml_data[field])
            result = validate_ghana_phone(raw)
            if not result['valid']:
                issues.append({
                    'field': field,
                    'value': raw,
                    'error': result['error']
                })

    return issues
