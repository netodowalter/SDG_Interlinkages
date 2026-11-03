'Local SDG Interlinkages interface. Run python app.py.'
import logging
from zipfile import ZIP_DEFLATED, ZipFile

import gradio as gr
from openpyxl import load_workbook

from sdg.service import list_areas, run_analysis


def areas(version, scope):
    return [(f"{name} ({code})", code) for code, name in list_areas(version, scope).items()]


def results(folder):
    rankings, highlights, images = [], [], []
    files = sorted(path for path in folder.rglob('*') if path.is_file())
    for path in files:
        if path.suffix == '.png':
            images.append((str(path), path.stem))
        if not path.name.endswith('_interlinkages.xlsx'):
            continue
        method = path.parent.name if path.parent != folder else 'pearson'
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            for sheet, metric in [('TopCollaborators', 'Colab'), ('TopNeglected', 'Neglect')]:
                rows = iter(book[sheet].values)
                headers = next(rows)
                for pos, values in enumerate(rows, 1):
                    if pos > 5:
                        break
                    row = dict(zip(headers, values))
                    rankings.append([method, metric, row.get('Ranking', pos),
                                     str(row.get('TargetCode', row.get('Target'))),
                                     row.get(metric, row.get('Value')),
                                     row.get('progress_direction', row.get('Direction')),
                                     row.get('IndicatorCode', row.get('Indicator'))])
            rows = iter(book['Highlights'].values)
            headers = next(rows)
            for values in rows:
                row = dict(zip(headers, values))
                target = row.get('TargetCode') or row.get('Indicator')
                if target:
                    highlights.append([method, row['Group'], str(target).split('::')[0], row['Score']])
        finally:
            book.close()
    archive = folder / 'results.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(folder))
    return rankings, highlights, images, [str(p) for p in files], str(archive)


def tab(version, title):
    with gr.Tab(title):
        description = ('UNSD indicators and relationships anticipated by IGES/JRC. Collect data online or upload a UNSD CSV.' if version == 'IGES_JRC' else
                       'Annual SDGIndex scores. Country and aggregate data are read from local workbooks.')
        gr.Markdown(description)
        with gr.Row():
            scope = gr.Radio([('Region or aggregate', 'region'), ('Country', 'country')], value='region', label='Scope')
            choices = areas(version, 'region')
            area = gr.Dropdown(choices, value='1' if version == 'IGES_JRC' else 'World', label='Area')
        if version == 'IGES_JRC':
            option = gr.File(label='UNSD CSV (optional)', file_types=['.csv'], type='filepath')
        else:
            option = gr.Radio([('Pearson', 'pearson'), ('Spearman', 'spearman'), ('Both', 'both')],
                              value='both', label='Correlation')
        button = gr.Button('Run analysis', variant='primary')
        status = gr.Markdown()
        gr.Markdown("""### First five in each ranking
Select a row to see the indicator.""")
        headers = ['Method', 'Ranking', 'Position', 'Target', 'Score', 'Direction']
        grid = gr.Dataframe(headers=headers, interactive=False)
        indicators = gr.State([])
        indicator = gr.Textbox(label='Selected indicator', interactive=False)
        gr.Markdown("""### Highlights by progress direction
Groups a–d with eligible targets, including ties at the cutoff.""")
        groups = gr.Dataframe(headers=['Method', 'Group', 'Target', 'Score'], interactive=False)
        gallery = gr.Gallery(label='Networks', columns=3, height='auto')
        bundle = gr.File(label='Download all results as ZIP')
        files = gr.File(label='Individual files', file_count='multiple')

        def change_scope(value):
            options = areas(version, value)
            return gr.Dropdown(choices=options, value=options[0][1])

        def calculate(kind, code, selection):
            try:
                kwargs = {'csv_path': selection} if version == 'IGES_JRC' else {'method': selection}
                folder = run_analysis(version, kind, code, **kwargs)
                ranked, highlighted, previews, paths, archive = results(folder)
                name = list_areas(version, kind)[code]
                return (f"**{name} ({code})** · {title} · {len(paths)} files generated.",
                        [r[:6] for r in ranked], [r[6] for r in ranked], '', highlighted,
                        previews, archive, paths)
            except Exception as exc:
                logging.exception('Analysis failed for %s/%s', version, code)
                raise gr.Error(str(exc)) from exc

        def show_indicator(values, event: gr.SelectData):
            index = event.index[0]
            return str(values[index] or '') if 0 <= index < len(values) else ''

        scope.change(change_scope, scope, area, queue=False)
        grid.select(show_indicator, indicators, indicator, queue=False)
        button.click(calculate, [scope, area, option],
                     [status, grid, indicators, indicator, groups, gallery, bundle, files],
                     concurrency_id='motor_sdg', concurrency_limit=1)


def build_app():
    with gr.Blocks(title='SDG Interlinkages') as demo:
        gr.Markdown("""# SDG Interlinkages
Networks of collaboration and neglect among SDG targets.""")
        with gr.Tabs():
            tab('IGES_JRC', 'IGES/JRC')
            tab('SDGIndex', 'SDGIndex')
    return demo.queue()


if __name__ == '__main__':
    build_app().launch(inbrowser=True, share=False)
