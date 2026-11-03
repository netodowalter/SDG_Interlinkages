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


def highlight_groups(nodes, edges):
    """Keep at most ten per group; break exact ties by stable node identifier."""
    byid = {n['id']: n for n in nodes}
    for n in nodes:
        n.update(tradeoff_received_from_backward=0.0, backward_synergy_sent=0.0)
    for edge in edges:
        a, b = byid[edge['source']], byid[edge['target']]
        weight = abs(edge['weight'])
        if edge['interaction'] == 'trade-off' and a['direction'] == 'backward' and b['direction'] == 'forward':
            b['tradeoff_received_from_backward'] += weight
        if edge['interaction'] == 'synergy' and a['direction'] == 'backward':
            a['backward_synergy_sent'] += weight
    specs = [('colab_rank', 'colab', 'forward', False, True),
             ('neglect_rank', 'neglect', 'backward', False, True),
             ('target_time_rank', 'years_to_target', 'forward', True, False),
             ('zero_time_rank', 'years_to_zero', 'backward', False, False),
             ('receiver_rank', 'tradeoff_received_from_backward', 'forward', False, True),
             ('sender_rank', 'backward_synergy_sent', 'backward', False, True)]
    ranks = {}
    for rank, field, direction, ascending, positive in specs:
        ranks[rank] = positions(nodes, field, direction, ascending, positive)
        for n in nodes:
            n[rank] = ranks[rank].get(n['id'])
    top = {key: {i for i, rank in values.items() if rank <= TOP_N}
           for key, values in ranks.items()}
    selected = [(top['colab_rank'] & top['target_time_rank']) - top['receiver_rank'],
                top['colab_rank'] & top['receiver_rank'],
                (top['neglect_rank'] & top['zero_time_rank']) - top['sender_rank'],
                top['neglect_rank'] & top['sender_rank']]
    definitions = [
        ('autonomous_collaborators', 'a · Collaborators — shortest target times, outside top receivers', 'colab', 'years_to_target'),
        ('contextual_collaborators', 'b · Collaborators — top receivers of trade-offs from regression', 'colab', 'years_to_target'),
        ('resilient_neglected', 'c · Resilient neglected indicators — longest times to zero, outside top senders', 'neglect', 'years_to_zero'),
        ('propagating_neglected', 'd · Neglected indicators — top senders of backward synergies', 'neglect', 'years_to_zero')]
    groups = []
    for (slug, title, metric, time), ids in zip(definitions, selected):
        ordered = sorted(ids, key=lambda i: (-byid[i][metric], i))
        rows = [[byid[i][metric + '_rank'], i, byid[i][metric], byid[i]['description'],
                 byid[i]['indicator'], byid[i]['description'], byid[i][time],
                 byid[i]['direction'], ''] for i in ordered]
        groups.append(dict(id=slug, title=title, metric=metric, rows=rows,
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
