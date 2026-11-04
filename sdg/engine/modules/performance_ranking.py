"""SDGIndex performance times and intersections of direction-specific top tens."""
import math

TOP_N = 10


def performance_time(points, trend):
    observations = [(year, score) for year, score in points
                    if isinstance(score, (int, float)) and math.isfinite(score)]
    year, score = max(observations, default=(None, None))
    slope = trend.get('slope')
    direction = trend.get('progress_direction')
    reach = zero = None
    if score is not None and slope is not None and math.isfinite(slope):
        if direction == 'forward' and slope > 0:
            reach = max(0.0, 100.0 - score) / slope
        elif direction == 'backward' and slope < 0:
            zero = max(0.0, score) / abs(slope)
    return dict(latest_year=year, latest_score=score, slope=slope,
                years_to_target=reach, years_to_zero=zero)


def positions(nodes, field, direction, ascending=False, positive=False):
    pool = [n for n in nodes if n['direction'] == direction
            and isinstance(n.get(field), (int, float)) and math.isfinite(n[field])
            and (not positive or n[field] > 0)]
    pool.sort(key=lambda n: (n[field] if ascending else -n[field], n['id']))
    return {n['id']: i for i, n in enumerate(pool, 1)}


RANK_FIELDS = (
    ('colab_rank', 'colab', 'forward', False, True),
    ('neglect_rank', 'neglect', 'backward', False, True),
    ('target_time_rank', 'years_to_target', 'forward', True, False),
    ('zero_time_rank', 'years_to_zero', 'backward', False, False),
    ('receiver_rank', 'tradeoff_received_from_backward', 'forward', False, True),
    ('sender_rank', 'backward_synergy_sent', 'backward', False, True),
    ('spreader_rank', 'forward_synergy_sent', 'forward', False, True),
    ('cost_sender_rank', 'tradeoff_sent_to_backward', 'forward', False, True),
    ('bridge_rank', 'bridge_flow', 'backward', False, True),
    ('relay_rank', 'relay_flow', 'backward', False, True))
RANK_KEYS = tuple(spec[0] for spec in RANK_FIELDS)


def highlight_groups(nodes, edges):
    """Six interface roles; at most ten per ranking, exact ties broken by stable node ID.

    Years to target (improving) or to zero (deteriorating) characterise each selected
    node in its row; they do not filter role membership."""
    from roles import ROLES, interface_measures, select_roles
    byid = {n['id']: n for n in nodes}
    measures = interface_measures({i: n['direction'] for i, n in byid.items()},
                                  [(e['source'], e['target'], e['interaction'], e['weight']) for e in edges])
    for n in nodes:
        n.update(measures[n['id']])
    field_rank, top = {}, {}
    for rank, field, direction, ascending, positive in RANK_FIELDS:
        ranking = positions(nodes, field, direction, ascending, positive)
        for n in nodes:
            n[rank] = ranking.get(n['id'])
        field_rank[field] = rank
        top[rank] = {i for i, position in ranking.items() if position <= TOP_N}
    selected = select_roles(lambda field, direction: top[field_rank[field]],
                            {i: n['forward_ratio'] for i, n in byid.items()})
    groups = []
    for slug, title, metric, label, direction in ROLES:
        time = 'years_to_target' if direction == 'forward' else 'years_to_zero'
        ordered = sorted(selected[slug], key=lambda i: (-byid[i][metric], i))
        rows = [[byid[i][field_rank[metric]], i, byid[i][metric], byid[i]['description'],
                 byid[i]['indicator'], byid[i]['description'], byid[i][time],
                 byid[i]['direction'], ''] for i in ordered]
        groups.append(dict(id=slug, title=title, metric=label, rows=rows,
                           base='Intersection of top 10 rankings; ties resolved by node ID.'))
    return groups


def format_years(workbook):
    """Numeric cells keep precision; display ordinary decimal years to three places."""
    for sheet in workbook:
        headers = next(sheet.values, ())
        for col, field in enumerate(headers, 1):
            if field in ('years_to_target', 'years_to_zero', 'Years'):
                for row in sheet.iter_rows(min_row=2, min_col=col, max_col=col):
                    row[0].number_format = '0.000'
