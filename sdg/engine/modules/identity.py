'Identify shared measures by series, dimensions and unit rather than by correlation or target wording.'
import json
import re
from collections import defaultdict

def target_key(value):
    goal, suffix = str(value).split('.', 1)
    return int(goal), (0, int(suffix)) if suffix.isdigit() else (1, suffix)

def measure_key(row):
    api = str(row.get('api_series') or '').strip()
    if not api:
        return ('unidentified', str(row['series_id']))
    raw = row.get('dimensions') or '{}'
    dims = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(dims, dict):
        raise ValueError('Invalid dimensions: '+str(row['series_id']))
    return (api, json.dumps(dims, sort_keys=True, ensure_ascii=False), str(row.get('unit') or '').strip())

def representatives(rows):
    'Return canonical IDs and a legend. A measure is API series + dimensions + unit. Prefer its native target, then the lowest SDG code. Do not merge distinct measures based on identical observations or perfect correlations.'
    groups = defaultdict(list)
    for row in rows:
        groups[measure_key(row)].append(row)
    mapping, legend = {}, []
    for key, items in groups.items():
        def priority(row):
            targets = re.findall('(?:1[0-7]|[1-9])\\.(?:\\d+|[a-z])', str(row.get('targets') or ''))
            target = min(targets, key=target_key) if targets else '99.99'
            native = str(row.get('indicator_used') or '').rsplit('.', 1)[0]
            return target != native, target_key(target), str(row['series_id'])
        chosen = min(items, key=priority)
        canonical = str(chosen['series_id'])
        targets = sorted({t for row in items for t in re.findall('(?:1[0-7]|[1-9])\\.(?:\\d+|[a-z])', str(row.get('targets') or ''))}, key=target_key)
        target = min(re.findall('(?:1[0-7]|[1-9])\\.(?:\\d+|[a-z])', str(chosen.get('targets') or '')), key=target_key)
        for row in items:
            mapping[str(row['series_id'])] = canonical
        if len(items)>1 or len(targets)>1:
            legend.append(dict(representative=target, represents=targets, api_series=chosen.get('api_series') or '',
                               dimensions=chosen.get('dimensions') or '{}', unit=chosen.get('unit') or '',
                               canonical_series_id=canonical, excluded_series_ids=[str(row['series_id']) for row in items if str(row['series_id'])!=canonical]))
    return mapping, sorted(legend, key=lambda row:target_key(row['representative']))
