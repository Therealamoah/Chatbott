import yaml
import re
from pathlib import Path
from datetime import date
from typing import Optional

from cleaning.dept_normalizer import normalize_department
from cleaning.phone_validator import validate_phones_in_yaml
from cleaning.hours_validator import validate_hours_yaml
from cleaning.phi_detector import phi_report


REQUIRED_FIELDS_DEPARTMENT = [
    'department', 'full_name', 'location', 'hours', 'last_verified'
]

REQUIRED_FIELDS_FAQ = [
    'id', 'question', 'answer', 'department', 'topic'
]


def validate_yaml_structure(data: dict, yaml_type: str = 'department') -> list[dict]:
    issues = []

    if yaml_type == 'department':
        for field in REQUIRED_FIELDS_DEPARTMENT:
            if field not in data:
                issues.append({
                    'field': field,
                    'severity': 'error',
                    'message': f'required field "{field}" is missing'
                })

    elif yaml_type == 'faq':
        if 'faqs' not in data:
            issues.append({'field': 'faqs', 'severity': 'error', 'message': 'faqs list missing'})
            return issues
        for i, faq in enumerate(data.get('faqs', [])):
            for field in REQUIRED_FIELDS_FAQ:
                if field not in faq:
                    issues.append({
                        'field': f'faqs[{i}].{field}',
                        'severity': 'error',
                        'message': f'required field "{field}" missing in FAQ #{i}'
                    })

    return issues


def validate_dates(data: dict) -> list[dict]:
    issues = []
    date_fields = ['last_verified', 'valid_until']

    for field in date_fields:
        if field not in data:
            continue
        try:
            d = date.fromisoformat(str(data[field]))
            days_old = (date.today() - d).days

            if field == 'last_verified' and days_old > 30:
                issues.append({
                    'field': field,
                    'value': str(data[field]),
                    'severity': 'warning',
                    'message': f'last_verified is {days_old} days ago — please re-verify this info'
                })
            if field == 'valid_until' and d < date.today():
                issues.append({
                    'field': field,
                    'value': str(data[field]),
                    'severity': 'error',
                    'message': 'valid_until is in the past — this info may be expired'
                })
        except (ValueError, TypeError):
            issues.append({
                'field': field,
                'value': str(data.get(field)),
                'severity': 'error',
                'message': 'invalid date format. use YYYY-MM-DD'
            })

    return issues


def normalize_yaml_departments(data: dict) -> dict:
    if 'department' in data:
        canonical = normalize_department(data['department'])
        if canonical and canonical != data['department']:
            data['_original_department'] = data['department']
            data['department'] = canonical

    if 'faqs' in data:
        for faq in data['faqs']:
            if 'department' in faq:
                canonical = normalize_department(faq['department'])
                if canonical:
                    faq['department'] = canonical

    return data


def clean_text_fields(data: dict) -> dict:
    def clean_value(v):
        if isinstance(v, str):
            return v.strip()
        if isinstance(v, dict):
            return {k: clean_value(val) for k, val in v.items()}
        if isinstance(v, list):
            return [clean_value(item) for item in v]
        return v

    return {k: clean_value(v) for k, v in data.items()}


def validate_yaml_file(yaml_path: str) -> dict:
    path = Path(yaml_path)
    report = {
        'file': str(path),
        'valid': True,
        'issues': [],
        'warnings': [],
        'phi': None,
    }

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            data = yaml.safe_load(raw_text)
    except yaml.YAMLError as e:
        report['valid'] = False
        report['issues'].append({'severity': 'error', 'message': f'YAML parse error: {e}'})
        return report
    except FileNotFoundError:
        report['valid'] = False
        report['issues'].append({'severity': 'error', 'message': 'file not found'})
        return report

    if data is None:
        report['valid'] = False
        report['issues'].append({'severity': 'error', 'message': 'empty YAML file'})
        return report

    yaml_type = 'faq' if 'faqs' in data else 'department'
    report['type'] = yaml_type

    struct_issues = validate_yaml_structure(data, yaml_type)
    report['issues'].extend(struct_issues)

    phone_issues = validate_phones_in_yaml(data)
    for issue in phone_issues:
        issue['severity'] = 'warning'
    report['warnings'].extend(phone_issues)

    if 'hours' in data:
        hours_issues = validate_hours_yaml(data['hours'])
        for issue in hours_issues:
            issue['severity'] = 'warning'
        report['warnings'].extend(hours_issues)

    date_issues = validate_dates(data)
    for issue in date_issues:
        if issue['severity'] == 'error':
            report['issues'].append(issue)
        else:
            report['warnings'].append(issue)

    phi = phi_report(raw_text, source=str(path))
    report['phi'] = phi
    if phi['has_high_phi']:
        report['valid'] = False
        report['issues'].append({
            'severity': 'error',
            'message': 'HIGH severity PHI detected — block from ingestion',
            'details': phi['findings']
        })

    error_issues = [i for i in report['issues'] if i.get('severity') == 'error']
    if error_issues:
        report['valid'] = False

    return report


def clean_and_load_yaml(yaml_path: str) -> Optional[dict]:
    validation = validate_yaml_file(yaml_path)

    if not validation['valid']:
        print(f"BLOCKED: {yaml_path}")
        for issue in validation['issues']:
            print(f"  ERROR: {issue['message']}")
        return None

    if validation['warnings']:
        print(f"WARNINGS: {yaml_path}")
        for w in validation['warnings']:
            print(f"  WARN: {w.get('field', '?')} — {w.get('message', w.get('error', ''))}")

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    data = clean_text_fields(data)
    data = normalize_yaml_departments(data)
    return data
