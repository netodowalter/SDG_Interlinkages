'Local SDG Interlinkages interface. Run python app.py.'
import logging

import gradio as gr

from sdg.service import list_areas, run_analysis
from sdg.ui_results import results, table_headers


def areas(version, scope):
    return [(f"{name} ({code})", code) for code, name in list_areas(version, scope).items()]




def tab(version, title):
    with gr.Tab(title):
        description = ('UNSD indicators and relationships anticipated by IGES/JRC. Collect data online or upload a UNSD CSV.' if version == 'IGES_JRC' else
                       'Annual SDGIndex scores. Country and aggregate data are read from local workbooks.')
        gr.Markdown(description)
        gr.Markdown('Improvement means movement towards the desired outcome; deterioration means movement away from it. These describe the observed trajectory, not whether a target is on track for 2030. Stable indicates negligible fitted change; undetermined indicates insufficient evidence.')
        with gr.Row():
            scope = gr.Radio([('Region or aggregate', 'region'), ('Country', 'country')], value='region', label='Scope')
            choices = areas(version, 'region')
            area = gr.Dropdown(choices, value='1' if version == 'IGES_JRC' else 'World', label='Area')
        if version == 'IGES_JRC':
            gr.Markdown('OECD and World Bank income groups are listed by their UNSD API codes. Verification returned no aggregate observations for these codes; live collection can be retried. Coverage and membership can differ from SDGIndex. BRICS groups have no UNSD catalog code.')
            option = gr.File(label='UNSD CSV (optional)', file_types=['.csv'], type='filepath')
        else:
            option = gr.Radio([('Pearson', 'pearson'), ('Spearman', 'spearman'), ('Both', 'both')],
                              value='both', label='Correlation')
        button = gr.Button('Run analysis', variant='primary')
        status = gr.Markdown()
        gr.Markdown("""### First ten in each ranking
Select a row to see the indicator.""")
        headers, highlight_headers = table_headers(version)
        grid = gr.Dataframe(headers=headers, interactive=False)
        indicators = gr.State([])
        indicator = gr.Textbox(label='Selected indicator', interactive=False)
        gr.Markdown("""### Highlights by performance direction
Six roles from top 10 intersections. Improving: I-1 contributors, I-2 dependent contributors, I-3 isolated beneficiaries. Deteriorating: D-1 exposed targets, D-2 transmission bridges, D-3 deterioration relays. Context characterises each role without filtering it: years to target or to zero (SDGIndex), ambitiousness (IGES/JRC).""")
        groups = gr.Dataframe(headers=highlight_headers, interactive=False)
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
                ranked, highlighted, previews, paths, archive = results(folder, version)
                name = list_areas(version, kind)[code]
                return (f"**{name} ({code})** · {title} · {len(paths)} files generated.",
                        [r[:6] + r[7:] for r in ranked], [r[6] for r in ranked], '', highlighted,
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

