"""Interface local do SDG Interlinkages. Execute com python app.py."""
import logging
from zipfile import ZIP_DEFLATED, ZipFile

import gradio as gr
from openpyxl import load_workbook

from ods.service import list_areas, run_analysis


def areas(version, scope):
    return [(f"{name} ({code})", code) for code, name in list_areas(version, scope).items()]


def results(folder):
    rankings, highlights, images = [], [], []
    files = sorted(path for path in folder.rglob("*") if path.is_file())
    for path in files:
        if path.suffix == ".png":
            images.append((str(path), path.stem))
        if not path.name.endswith("_interlinkages.xlsx"):
            continue
        method = path.parent.name if path.parent != folder else "pearson"
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            for sheet, metric in [("MaisColaboradoras", "Colab"), ("MaisNegligenciadas", "Neglect")]:
                rows = iter(book[sheet].values)
                headers = next(rows)
                for pos, values in enumerate(rows, 1):
                    if pos > 5:
                        break
                    row = dict(zip(headers, values))
                    rankings.append([method, metric, row.get("Ranking", pos),
                                     str(row.get("MetaODS", row.get("Meta"))),
                                     row.get(metric, row.get("Valor")),
                                     row.get("direcao_progresso", row.get("Direção")),
                                     row.get("IndicadorODS", row.get("Indicador"))])
            rows = iter(book["Destaques"].values)
            headers = next(rows)
            for values in rows:
                row = dict(zip(headers, values))
                target = row.get("MetaODS") or row.get("Indicador")
                if target:
                    highlights.append([method, row["Grupo"], str(target).split("::")[0], row["Escore"]])
        finally:
            book.close()
    archive = folder / "resultados.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(folder))
    return rankings, highlights, images, [str(p) for p in files], str(archive)


def tab(version, title):
    with gr.Tab(title):
        description = ("Indicadores da UNSD e relações previstas pelo IGES/JRC. "
                       "Use a coleta online ou carregue um CSV da UNSD." if version == "IGES_JRC" else
                       "Escores anuais do SDGIndex. Os dados de países e agregados são lidos das planilhas locais.")
        gr.Markdown(description)
        with gr.Row():
            scope = gr.Radio([("Região ou agregado", "regiao"), ("País", "pais")], value="regiao", label="Recorte")
            choices = areas(version, "regiao")
            area = gr.Dropdown(choices, value="1" if version == "IGES_JRC" else "World", label="Área")
        if version == "IGES_JRC":
            option = gr.File(label="CSV da UNSD (opcional)", file_types=[".csv"], type="filepath")
        else:
            option = gr.Radio([("Pearson", "pearson"), ("Spearman", "spearman"), ("Ambos", "ambos")],
                              value="ambos", label="Correlação")
        button = gr.Button("Executar análise", variant="primary")
        status = gr.Markdown()
        gr.Markdown("### Cinco primeiras de cada ranking\nSelecione uma linha para consultar o indicador.")
        headers = ["Método", "Ranking", "Posição", "Meta", "Escore", "Direção"]
        grid = gr.Dataframe(headers=headers, interactive=False)
        indicators = gr.State([])
        indicator = gr.Textbox(label="Indicador da linha selecionada", interactive=False)
        gr.Markdown("### Destaques por direção do progresso\nGrupos a–d com metas elegíveis, incluindo empates no corte.")
        groups = gr.Dataframe(headers=["Método", "Grupo", "Meta", "Escore"], interactive=False)
        gallery = gr.Gallery(label="Redes", columns=3, height="auto")
        bundle = gr.File(label="Baixar todos os resultados em ZIP")
        files = gr.File(label="Arquivos individuais", file_count="multiple")

        def change_scope(value):
            options = areas(version, value)
            return gr.Dropdown(choices=options, value=options[0][1])

        def calculate(kind, code, selection):
            try:
                kwargs = {"csv_path": selection} if version == "IGES_JRC" else {"method": selection}
                folder = run_analysis(version, kind, code, **kwargs)
                ranked, highlighted, previews, paths, archive = results(folder)
                name = list_areas(version, kind)[code]
                return (f"**{name} ({code})** · {title} · {len(paths)} arquivos gerados.",
                        [r[:6] for r in ranked], [r[6] for r in ranked], "", highlighted,
                        previews, archive, paths)
            except Exception as exc:
                logging.exception("Falha na análise %s/%s", version, code)
                raise gr.Error(str(exc)) from exc

        def show_indicator(values, event: gr.SelectData):
            index = event.index[0]
            return str(values[index] or "") if 0 <= index < len(values) else ""

        scope.change(change_scope, scope, area, queue=False)
        grid.select(show_indicator, indicators, indicator, queue=False)
        button.click(calculate, [scope, area, option],
                     [status, grid, indicators, indicator, groups, gallery, bundle, files],
                     concurrency_id="motor_ods", concurrency_limit=1)


def build_app():
    with gr.Blocks(title="SDG Interlinkages") as demo:
        gr.Markdown("# SDG Interlinkages\nRedes de colaboração e negligência entre metas dos ODS.")
        with gr.Tabs():
            tab("IGES_JRC", "IGES/JRC")
            tab("SDGIndex", "SDGIndex")
    return demo.queue()


if __name__ == "__main__":
    build_app().launch(inbrowser=True, share=False)
