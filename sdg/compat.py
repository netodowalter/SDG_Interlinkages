"""Normalize previous workbook inputs at the read boundary."""
import json
from pathlib import Path

SCHEMA = json.loads((Path(__file__).resolve().parent.parent / "docs" / "legacy-schema.json").read_text(encoding="utf-8"))


def legacy_name(value):
    if not isinstance(value, str):
        return value
    if value in SCHEMA:
        return SCHEMA[value]
    return ".".join("_".join(SCHEMA.get(part, part) for part in segment.split("_"))
                    for segment in value.split("."))


def normalize_source_workbook(book):
    """Accept earlier component-score workbooks and emit English headers."""
    if "Component_observations" in book.sheetnames:
        return book
    for sheet in book:
        sheet.title = legacy_name(sheet.title)
        for cell in sheet[1]:
            cell.value = legacy_name(cell.value)
    return book
