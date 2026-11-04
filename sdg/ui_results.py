"""Dataset-specific result tables for the Gradio interface."""
from zipfile import ZIP_DEFLATED, ZipFile
from openpyxl import load_workbook


def table_headers(version):
    context = ['Ambitiousness'] if version == 'IGES_JRC' else ['Years to target', 'Years to zero']
    return (['Method', 'Ranking', 'Position', 'Target', 'Score', 'Performance direction'] + context,
            ['Method', 'Group', 'Target / indicator', 'Score'] + (['Ambitiousness'] if version == 'IGES_JRC' else ['Years']))


def direction_label(value):
    key = str(value or '').strip().lower()
    return {'forward': 'Improvement', 'progressing': 'Improvement', 'improving': 'Improvement',
            'improvement': 'Improvement', 'backward': 'Deterioration', 'regressing': 'Deterioration',
            'deteriorating': 'Deterioration', 'deterioration': 'Deterioration',
            'stable': 'Stable', 'undetermined': 'Undetermined'}.get(key, 'Undetermined')


def display_terminology(value):
    return str(value).replace('from regression', 'from deterioration').replace(
        'backward synergies', 'synergies from deteriorating sources')


def decimal(value):
    return format(value, '.3f') if value is not None else ''


def context_values(row, version):
    if version == 'IGES_JRC':
        return [decimal(row.get('target_ambition'))]
    return [decimal(row.get('years_to_target')), decimal(row.get('years_to_zero'))]


def results(folder, version):
    rankings, highlights, images = [], [], []
    files = sorted(path for path in folder.rglob('*') if path.is_file())
    for path in files:
        if path.suffix == '.png':
            images.append((str(path), path.stem))
        pond = path.name.endswith('_interlinkages_pond.xlsx')
        if not (pond or path.name.endswith('_interlinkages.xlsx')):
            continue
        method = (path.parent.name if path.parent != folder else 'pearson') + (' · weighted' if pond else '')
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            for sheet, metric in [('TopCollaborators', 'Colab'), ('TopNeglected', 'Neglect')]:
                rows = iter(book[sheet].values)
                headers = next(rows)
                for pos, values in enumerate(rows, 1):
                    if pos > 10:
                        break
                    row = dict(zip(headers, values))
                    rankings.append([method, metric, row.get('Ranking', pos),
                                     str(row.get('TargetCode', row.get('Target'))),
                                     row.get(metric, row.get('Value')),
                                     direction_label(row.get('progress_direction', row.get('Direction'))),
                                     row.get('IndicatorCode', row.get('Indicator')),
                                     *context_values(row, version)])
            rows = iter(book['Highlights'].values)
            headers = next(rows)
            for values in rows:
                row = dict(zip(headers, values))
                target = row.get('TargetCode') or row.get('Indicator')
                if target:
                    highlights.append([method, display_terminology(row['Group']), str(target), row['Score'], decimal(row.get('target_ambition') if version == 'IGES_JRC' else row.get('Years'))])
        finally:
            book.close()
    archive = folder / 'results.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(folder))
    return rankings, highlights, images, [str(p) for p in files], str(archive)

