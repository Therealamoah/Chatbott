import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cleaning.yaml_cleaner import clean_and_load_yaml
from cleaning.report import generate_cleaning_report, print_report_summary

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base_clean.json"
REPORT_PATH = Path(__file__).resolve().parent.parent / "reports" / "cleaning_report.json"


def main():
    report = generate_cleaning_report(str(KNOWLEDGE_DIR), output_path=str(REPORT_PATH))
    print_report_summary(report)

    departments = []
    faqs = []

    for yaml_file in sorted(KNOWLEDGE_DIR.glob("*.yaml")):
        data = clean_and_load_yaml(str(yaml_file))
        if data is None:
            continue

        if "faqs" in data:
            faqs.extend(data["faqs"])
        else:
            departments.append(data)

    clean_kb = {
        "metadata": {
            "version": "1.0",
            "generated": report["generated_at"],
            "description": "MediGuide AI Clean Knowledge Base",
            "source_dir": str(KNOWLEDGE_DIR),
        },
        "summary": {
            "departments": len(departments),
            "faqs": len(faqs),
            "validation": {
                "total_files": report["total_files"],
                "valid": report["valid_files"],
                "invalid": report["invalid_files"],
                "warnings": report["summary"]["total_warnings"],
            },
        },
        "departments": departments,
        "faqs": faqs,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_kb, f, indent=2, default=str, ensure_ascii=False)

    print(f"\nClean knowledge base exported to: {OUTPUT_PATH}")
    print(f"  Departments: {len(departments)}")
    print(f"  FAQs: {len(faqs)}")


if __name__ == "__main__":
    main()
