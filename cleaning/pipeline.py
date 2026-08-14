from pathlib import Path
from cleaning.text_cleaner import clean_raw_text
from cleaning.ocr_cleaner import clean_ocr_text
from cleaning.yaml_cleaner import clean_and_load_yaml
from cleaning.phi_detector import phi_report
from cleaning.report import generate_cleaning_report, print_report_summary


def clean_text_document(text: str, is_ocr: bool = False, source: str = 'unknown') -> dict:
    phi = phi_report(text, source=source)
    if phi['has_high_phi']:
        return {
            'cleaned_text': None,
            'phi': phi,
            'blocked': True,
            'reason': 'high severity PHI detected'
        }

    if is_ocr:
        text = clean_ocr_text(text)
    text = clean_raw_text(text)

    return {
        'cleaned_text': text,
        'phi': phi,
        'blocked': False,
        'reason': None
    }


def clean_knowledge_base(knowledge_dir: str, report_path: str = None) -> list[dict]:
    report = generate_cleaning_report(knowledge_dir, output_path=report_path)
    print_report_summary(report)

    valid_docs = []
    for yaml_file in Path(knowledge_dir).glob('*.yaml'):
        data = clean_and_load_yaml(str(yaml_file))
        if data is not None:
            valid_docs.append({
                'source': str(yaml_file),
                'data': data
            })

    print(f"Cleaning complete: {len(valid_docs)} files ready for ingestion")
    return valid_docs
