"""Interface compartilhada pelo terminal e por um futuro callback do Gradio."""
import csv
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from openpyxl import Workbook, load_workbook

from .engine import ods_interlinkages as iges
from .render import render_networks

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
METHODS = ("IGES_JRC", "SDGIndex")
SCOPES = ("regiao", "pais")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def list_areas(version, scope):
    """Retorna código estável → nome; consulta somente os catálogos locais."""
    if version not in METHODS or scope not in SCOPES:
        raise ValueError("Modalidade ou tipo de área inválido.")
    if version == "IGES_JRC":
        from .engine.modulos.coleta import regioes_continentais
        tree = read_json(DATA / "areas.json")
        areas = iges.countries_from_tree(tree) if scope == "pais" else regioes_continentais(tree)
        return {str(code): row["nome"] for code, row in areas.items()}
    country = scope == "pais"
    records = read_json(DATA / "SDGIndex" / ("countries.json" if country else "catalog.json"))
    return {r["code" if country else "region"]: r["title"] for r in records}


def export_csv(path, records, required):
    columns = list(dict.fromkeys([*required, *(k for row in records for k in row)]))
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)


def sdg_run(folder, code, title, scope, method):
    from sdgindex_country import analyze
    base = DATA / "SDGIndex"
    if scope == "pais":
        record = next(r for r in read_json(base / "countries.json") if r["code"] == code)
        source = base / "countries" / Path(record["url"]).name
    else:
        source = base / "regions" / f"Regiao_{code}.xlsx"
    prefix = f"{code}_{method}"
    folder.mkdir()
    full = folder / f"{prefix}_full.xlsx"
    result = analyze(source, base / "mapping.json", method, code, title, full,
                     scope="country" if scope == "pais" else "region")
    graph = result["network"]
    export_csv(folder / f"{prefix}_nodes.csv", graph["nodes"], ["id", "target", "indicator"])
    export_csv(folder / f"{prefix}_network.csv", graph["edges"], ["source", "target", "interaction", "weight"])
    book = load_workbook(full, read_only=True, data_only=True)
    summary = Workbook(write_only=True)
    try:
        for name, metric in [("MaisColaboradoras", "colab"), ("MaisNegligenciadas", "neglect")]:
            tab = summary.create_sheet(name)
            tab.append(["Meta", "Indicador", "Valor", "Direção", "Ambição"])
            for n in sorted(graph["nodes"], key=lambda n: -n[metric]):
                tab.append([n["target"], n["indicator"], n[metric], n["direction"], n["ambition"]])
        for name in ["Destaques", "Diagnostico_dependencia", "Casos adversos"]:
            tab = summary.create_sheet(name)
            for row in book[name].values:
                tab.append(row)
        summary.save(folder / f"{prefix}_interlinkages.xlsx")
    finally:
        book.close()
    render_networks(folder, prefix, title, graph, result["highlights"], DATA / "icons")


def iges_run(folder, code, title, csv_path, work, modules):
    region = {"codigo": int(code), "nome": title}
    source = csv_path or iges.download_csv(modules[0], region, work / "api.csv")
    pipeline_work = work / "processamento"
    pipeline_work.mkdir()
    produced = iges.run_pipeline(modules, pipeline_work, region, source, work / "result")
    shutil.copytree(produced, folder, dirs_exist_ok=True)
    full = next(folder.glob("*_full.xlsx"))
    ranking = modules[4]
    metrics, assessments, series, descriptions = ranking.read_source(full)
    names = ranking.load_descriptions(iges.BASES / "ods_descricao.xlsx")
    details, _ = ranking.prepare_details(metrics, assessments, series, descriptions, *names)
    from progresso import workbook_edges, highlight_groups
    edges = workbook_edges(full)
    graph = dict(nodes=[dict(id=t, target=t, direction=details[t][5], colab=v["Colab"],
                             neglect=v["Neglect"]) for t, v in metrics.items()],
                 edges=[dict(source=str(e["MetaA"]), target=str(e["MetaB"]),
                             weight=abs(float(e["weight"])), interaction=e["interaction"]) for e in edges])
    render_networks(folder, full.stem.removesuffix("_full"), title, graph,
                    highlight_groups(metrics, details, edges), DATA / "icons")


def run_analysis(version, scope, code, *, method=None, csv_path=None, output_dir=None):
    """Executa sem input(). Retorna Path da execução completa. Pode ser usado em fila."""
    areas = list_areas(version, scope)
    code = str(code)
    if code not in areas:
        raise ValueError(f"Código inválido para {version}/{scope}: {code}")
    if method not in (None, "pearson", "spearman", "ambos"):
        raise ValueError("Método de correlação desconhecido.")
    if version == "IGES_JRC" and method not in (None, "pearson"):
        raise ValueError("IGES/JRC usa Pearson.")
    if csv_path is not None and version != "IGES_JRC":
        raise ValueError("O CSV da UNSD aplica-se apenas ao IGES/JRC.")
    root = Path(output_dir or ROOT / "output").resolve()
    for branch in METHODS:
        (root / branch).mkdir(parents=True, exist_ok=True)
    parent = root / version / scope / code
    parent.mkdir(parents=True, exist_ok=True)
    destination = parent / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:12])
    with tempfile.TemporaryDirectory(dir=parent, prefix=".tmp-") as tmp:
        work = Path(tmp)
        ready = work / "entrega"
        ready.mkdir()
        modules = iges.load_modules(work)
        if version == "IGES_JRC":
            iges_run(ready, code, areas[code], Path(csv_path) if csv_path else None, work, modules)
        else:
            methods = ("pearson", "spearman") if method in (None, "ambos") else (method,)
            for selected in methods:
                sdg_run(ready / selected, code, areas[code], scope, selected)
        ready.rename(destination)
    return destination
