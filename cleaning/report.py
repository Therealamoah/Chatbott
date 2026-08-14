import json
from datetime import datetime
from pathlib import Path
from cleaning.yaml_cleaner import validate_yaml_file


def generate_cleaning_report(knowledge_dir: str, output_path: str = None) -> dict:
    knowledge_path = Path(knowledge_dir)
    yaml_files = list(knowledge_path.glob('*.yaml'))

    report = {
        'generated_at': datetime.now().isoformat(),
        'knowledge_dir': str(knowledge_path),
        'total_files': len(yaml_files),
        'valid_files': 0,
        'invalid_files': 0,
        'files_with_phi': 0,
        'stale_files': 0,
        'files': [],
        'summary': {},
    }

    all_issues = []

    for yaml_file in sorted(yaml_files):
        file_report = validate_yaml_file(str(yaml_file))
        report['files'].append(file_report)

        if file_report['valid']:
            report['valid_files'] += 1
        else:
            report['invalid_files'] += 1

        if file_report.get('phi') and file_report['phi']['has_phi']:
            report['files_with_phi'] += 1

        stale = [
            w for w in file_report.get('warnings', [])
            if 'days ago' in str(w.get('message', ''))
        ]
        if stale:
            report['stale_files'] += 1

        all_issues.extend(file_report.get('issues', []))
        all_issues.extend(file_report.get('warnings', []))

    report['summary'] = {
        'ready_to_ingest': report['valid_files'],
        'blocked': report['invalid_files'],
        'needs_review': report['files_with_phi'],
            'stale_files': report['stale_files'],
        'total_issues': len([i for i in all_issues if i.get('severity') == 'error']),
        'total_warnings': len([i for i in all_issues if i.get('severity') == 'warning']),
    }

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Cleaning report saved to: {output_path}")

    return report


def print_report_summary(report: dict):
    print("\n" + "="*60)
    print("MEDIGUIDE CLEANING REPORT")
    print("="*60)
    print(f"Generated: {report['generated_at']}")
    print(f"Directory: {report['knowledge_dir']}")
    print(f"Total files: {report['total_files']}")
    print()
    print(f"  Ready to ingest:  {report['summary']['ready_to_ingest']}")
    print(f"  Blocked (errors): {report['summary']['blocked']}")
    print(f"  PHI detected:     {report['summary']['needs_review']}")
    print(f"  Stale info:       {report['summary']['stale_files']}")
    print(f"  Total errors:     {report['summary']['total_issues']}")
    print(f"  Total warnings:   {report['summary']['total_warnings']}")
    print()

    for file_report in report['files']:
        status = "OK" if file_report['valid'] else "BLOCKED"
        fname = Path(file_report['file']).name
        phi = "PHI!" if file_report.get('phi') and file_report['phi']['has_phi'] else ""
        print(f"  [{status}] {fname} {phi}")
        for issue in file_report.get('issues', []):
            print(f"       ERROR: {issue.get('message', issue)}")
        for warn in file_report.get('warnings', [])[:3]:
            field = warn.get('field', '?')
            msg = warn.get('message', warn.get('error', ''))
            print(f"       WARN:  {field} — {msg}")

    print("="*60 + "\n")
