import re
from typing import Optional

DAYS_MAP = {
    'monday': 'monday', 'mon': 'monday', 'mo': 'monday',
    'tuesday': 'tuesday', 'tue': 'tuesday', 'tu': 'tuesday',
    'wednesday': 'wednesday', 'wed': 'wednesday', 'we': 'wednesday',
    'thursday': 'thursday', 'thu': 'thursday', 'th': 'thursday',
    'friday': 'friday', 'fri': 'friday', 'fr': 'friday',
    'saturday': 'saturday', 'sat': 'saturday', 'sa': 'saturday',
    'sunday': 'sunday', 'sun': 'sunday', 'su': 'sunday',
    'weekdays': 'weekdays', 'weekday': 'weekdays', 'work days': 'weekdays',
    'weekend': 'weekend', 'weekends': 'weekend',
    'daily': 'all', 'every day': 'all', '7 days': 'all', 'all week': 'all',
    'all': 'all',
}

TIME_ALIASES = {
    'midnight': '00:00',
    'noon': '12:00',
    'midday': '12:00',
}


def parse_time_string(raw: str) -> Optional[str]:
    if not raw:
        return None

    raw = raw.strip().lower()

    if raw in TIME_ALIASES:
        return TIME_ALIASES[raw]

    pattern = r'(\d{1,2})[:.h]?(\d{0,2})\s*(am|pm)?'
    match = re.match(pattern, raw)
    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2)) if match.group(2) else 0
    ampm = match.group(3)

    if ampm == 'pm' and hours != 12:
        hours += 12
    elif ampm == 'am' and hours == 12:
        hours = 0

    if hours > 23 or minutes > 59:
        return None

    return f'{hours:02d}:{minutes:02d}'


def parse_hours_string(raw: str) -> Optional[dict]:
    if not raw:
        return None

    raw_lower = raw.strip().lower()

    if any(word in raw_lower for word in ['24 hour', '24-hour', '24hrs', 'always open', 'round the clock']):
        return {'open': '00:00', 'close': '23:59', 'is_24h': True}

    if any(word in raw_lower for word in ['closed', 'not open', 'not available']):
        return {'open': None, 'close': None, 'is_closed': True}

    time_pattern = r'(\d{1,2}[:.h]?\d{0,2}\s*(?:am|pm)?)'
    times = re.findall(time_pattern, raw_lower, re.IGNORECASE)

    if len(times) >= 2:
        open_time = parse_time_string(times[0])
        close_time = parse_time_string(times[1])
        if open_time and close_time:
            return {'open': open_time, 'close': close_time, 'is_24h': False}

    return None


def validate_hours_yaml(hours_dict: dict) -> list[dict]:
    issues = []

    if not isinstance(hours_dict, dict):
        return [{'field': 'hours', 'error': 'hours field is not a dict'}]

    for day, hours_str in hours_dict.items():
        day_canonical = DAYS_MAP.get(day.lower().strip())
        if not day_canonical:
            issues.append({'field': f'hours.{day}', 'error': f'unrecognized day: {day}'})
            continue

        if isinstance(hours_str, str) and hours_str.lower().strip() not in ['closed', 'n/a', '']:
            parsed = parse_hours_string(hours_str)
            if not parsed:
                issues.append({
                    'field': f'hours.{day}',
                    'value': hours_str,
                    'error': 'could not parse hours string',
                    'hint': 'use format: "7:30 AM - 5:00 PM" or "24 hours"'
                })
            elif not parsed.get('is_24h') and not parsed.get('is_closed'):
                open_h = int(parsed['open'].split(':')[0])
                close_h = int(parsed['close'].split(':')[0])
                if close_h < open_h:
                    issues.append({
                        'field': f'hours.{day}',
                        'value': hours_str,
                        'error': 'close time is before open time — check if AM/PM was included'
                    })
                if open_h < 4:
                    issues.append({
                        'field': f'hours.{day}',
                        'value': hours_str,
                        'error': 'open time before 4 AM — is this correct for a hospital dept?'
                    })

    return issues


def format_hours_for_chunk(hours_dict: dict) -> str:
    parts = []
    for day, hours in hours_dict.items():
        if isinstance(hours, str):
            parts.append(f'{day.capitalize()}: {hours}')
    return ' | '.join(parts)
