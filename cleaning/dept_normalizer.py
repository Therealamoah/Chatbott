import re
from typing import Optional

CANONICAL_DEPARTMENTS = {
    'OPD', 'Emergency', 'Pharmacy', 'Laboratory',
    'Maternity', 'NHIS', 'Radiology', 'Physiotherapy',
    'Pediatrics', 'Surgery', 'Medicine', 'Cardiology',
    'Ophthalmology', 'ENT', 'Dermatology', 'Psychiatry',
    'Dental', 'Nutrition', 'Records', 'Accounts', 'Mortuary',
}

DEPARTMENT_ALIASES = {
    'outpatient department':       'OPD',
    'outpatients':                 'OPD',
    'outpatient':                  'OPD',
    'opd clinic':                  'OPD',
    'general outpatient':          'OPD',
    'general opd':                 'OPD',
    'general clinic':              'OPD',
    'walk-in clinic':              'OPD',

    'accident and emergency':      'Emergency',
    'a&e':                         'Emergency',
    'a & e':                       'Emergency',
    'a and e':                     'Emergency',
    'emergency unit':              'Emergency',
    'emergency ward':              'Emergency',
    'emergency room':              'Emergency',
    'casualty':                    'Emergency',
    'casualty unit':               'Emergency',
    'casualty ward':               'Emergency',
    'trauma unit':                 'Emergency',
    'accident unit':               'Emergency',
    'er':                          'Emergency',

    'dispensary':                  'Pharmacy',
    'drug dispensing':             'Pharmacy',
    'pharmacy unit':               'Pharmacy',
    'drug store':                  'Pharmacy',
    'chemist':                     'Pharmacy',

    'lab':                         'Laboratory',
    'pathology lab':               'Laboratory',
    'clinical laboratory':         'Laboratory',
    'diagnostic laboratory':       'Laboratory',
    'blood bank':                  'Laboratory',
    'path lab':                    'Laboratory',

    'maternity ward':              'Maternity',
    'labour ward':                 'Maternity',
    'labour suite':                'Maternity',
    'delivery suite':              'Maternity',
    'delivery ward':               'Maternity',
    'obstetrics':                  'Maternity',
    'obstetrics ward':             'Maternity',
    'antenatal clinic':            'Maternity',
    'antenatal ward':              'Maternity',
    'postnatal ward':              'Maternity',
    'womens health':               'Maternity',
    "women's health":              'Maternity',
    "women's ward":                'Maternity',
    'gynae':                       'Maternity',
    'gynaecology':                 'Maternity',
    'obstetrics and gynaecology':  'Maternity',
    'ob/gyn':                      'Maternity',
    'obgyn':                       'Maternity',

    'nhis desk':                   'NHIS',
    'insurance desk':              'NHIS',
    'health insurance':            'NHIS',
    'national health insurance':   'NHIS',
    'nhis office':                 'NHIS',

    'imaging':                     'Radiology',
    'x-ray':                       'Radiology',
    'xray':                        'Radiology',
    'ultrasound':                  'Radiology',
    'scan':                        'Radiology',
    'ct scan':                     'Radiology',
    'mri':                         'Radiology',
    'diagnostic imaging':          'Radiology',

    'paediatrics':                 'Pediatrics',
    'pediatric ward':              'Pediatrics',
    'paediatric ward':             'Pediatrics',
    'childrens ward':              'Pediatrics',
    "children's ward":             'Pediatrics',
    'child health':                'Pediatrics',
    'neonatal':                    'Pediatrics',
    'nicu':                        'Pediatrics',

    'medical records':             'Records',
    'records office':              'Records',
    'patient records':             'Records',
    'admissions':                  'Records',
    'registration':                'Records',
    'health records':              'Records',

    'billing':                     'Accounts',
    'fees':                        'Accounts',
    'accounts office':             'Accounts',
    'payment':                     'Accounts',
    'cashier':                     'Accounts',

    'physio':                      'Physiotherapy',
    'rehabilitation':              'Physiotherapy',
    'rehab':                       'Physiotherapy',
    'physiotherapy unit':          'Physiotherapy',

    'surgical ward':               'Surgery',
    'surgical unit':               'Surgery',
    'theatre':                     'Surgery',
    'operating theatre':           'Surgery',
    'operating room':              'Surgery',
    'or':                          'Surgery',

    'dentist':                     'Dental',
    'dental unit':                 'Dental',
    'oral health':                 'Dental',
    'dentistry':                   'Dental',

    'ear nose and throat':         'ENT',
    'ear, nose and throat':        'ENT',
    'ear nose throat':             'ENT',

    'mental health':               'Psychiatry',
    'psychiatric unit':            'Psychiatry',
    'psychiatry unit':             'Psychiatry',
    'psychology':                  'Psychiatry',
}


def normalize_department(text: str) -> Optional[str]:
    cleaned = text.strip().lower()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    if cleaned in DEPARTMENT_ALIASES:
        return DEPARTMENT_ALIASES[cleaned]

    if text.strip().title() in CANONICAL_DEPARTMENTS:
        return text.strip().title()

    for alias, canonical in DEPARTMENT_ALIASES.items():
        if alias in cleaned:
            return canonical

    return None


def normalize_departments_in_text(text: str) -> str:
    result = text
    for alias, canonical in sorted(DEPARTMENT_ALIASES.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(alias), re.IGNORECASE)
        result = pattern.sub(canonical, result)
    return result


def extract_department_mentions(text: str) -> list[str]:
    mentions = []
    text_lower = text.lower()

    for alias, canonical in DEPARTMENT_ALIASES.items():
        if alias in text_lower:
            mentions.append(canonical)

    for dept in CANONICAL_DEPARTMENTS:
        if dept.lower() in text_lower and dept not in mentions:
            mentions.append(dept)

    return list(set(mentions))
