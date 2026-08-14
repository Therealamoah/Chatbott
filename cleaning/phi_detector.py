import re

PHI_PATTERNS = {
    'full_name_pattern': {
        'pattern': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Asante|Mensah|Boateng|Owusu|Acheampong|Osei|Amoah|Darko|Kwame|Ama|Akua|Kofi|Kwesi|Abena|Adjoa|Yaw|Akosua|Kwabena|Efua)\b',
        'severity': 'medium',
        'description': 'possible Ghanaian full name',
    },
    'ghana_card': {
        'pattern': r'\bGHA-\d{9}-\d\b',
        'severity': 'high',
        'description': 'Ghana Card number',
    },
    'nhis_card_number': {
        'pattern': r'\bNHIS[/\-]?\d{8,12}\b',
        'severity': 'high',
        'description': 'NHIS card number',
    },
    'mrn': {
        'pattern': r'\b(?:MRN|Medical Record|File No|File Number)[:\s#]*\d{4,10}\b',
        'severity': 'high',
        'description': 'Medical Record Number',
    },
    'ghana_phone': {
        'pattern': r'\b0[2-5]\d{8}\b',
        'severity': 'low',
        'description': 'phone number (verify it is a dept contact, not a patient number)',
    },
    'dob': {
        'pattern': r'\b(?:DOB|Date of Birth|Born)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'severity': 'high',
        'description': 'date of birth',
    },
    'age_with_name': {
        'pattern': r'\b(?:age|aged|yrs?|years? old)[:\s]*\d{1,3}\b',
        'severity': 'low',
        'description': 'age mention (low risk, but check context)',
    },
    'diagnosis_pattern': {
        'pattern': r'\b(?:diagnosed with|presenting with|c/o|complains? of|suffering from)\b.{0,50}',
        'severity': 'medium',
        'description': 'possible patient diagnosis mention',
    },
    'prescription_pattern': {
        'pattern': r'\b\d+\s*mg\s+(?:twice|once|three times|BD|OD|TDS|QDS|PRN)\b',
        'severity': 'medium',
        'description': 'possible prescription — dosages should not be in KB',
    },
}


def detect_phi(text: str) -> list[dict]:
    findings = []

    for phi_type, config in PHI_PATTERNS.items():
        pattern = config['pattern']
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            findings.append({
                'phi_type': phi_type,
                'severity': config['severity'],
                'description': config['description'],
                'match': match.group()[:50],
                'position': match.start(),
                'context': text[max(0, match.start()-30):match.end()+30]
            })

    return findings


def has_high_severity_phi(text: str) -> bool:
    findings = detect_phi(text)
    return any(f['severity'] == 'high' for f in findings)


def phi_report(text: str, source: str = 'unknown') -> dict:
    findings = detect_phi(text)
    return {
        'source': source,
        'has_phi': len(findings) > 0,
        'has_high_phi': any(f['severity'] == 'high' for f in findings),
        'finding_count': len(findings),
        'findings': findings,
        'recommendation': 'BLOCK from ingestion' if any(f['severity'] == 'high' for f in findings)
                          else 'review before ingesting' if findings
                          else 'ok to ingest'
    }
