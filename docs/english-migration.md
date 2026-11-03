# English migration

The Python package, Gradio controls, terminal messages, workbook filenames, worksheet titles, column names, categorical values, JSON metadata, CSV exports and PNG annotations use English. The primary Python package is `sdg`; `ods` retains the previous command entry point.

## Official terminology

The authoritative source is the English Global Indicator Framework after the 2026 refinement, published by the United Nations Statistics Division:

https://unstats.un.org/sdgs/indicators/Global-Indicator-Framework-after-2026-refinement-English.xlsx

The catalog contains 17 goal statements and 169 target statements. Indicator descriptions use the entries of this edition, while IGES and SDGIndex proxy descriptions retain the actual historical measure definitions. Language migration does not redefine series, observations, or the target association of a proxy.

The previous `ods_descricao.xlsx` mixed UN wording, Brazilian target adaptations and national explanatory notes. Its runtime replacement, `sdg_descriptions.xlsx`, contains the official English UN catalog and provenance. The earlier national adaptation material remains available in the pre-migration Git revision `5f7f9e711858fd65707d96620b2607f6a76aa6a2`.

## Schema and paths

`legacy-schema.json` records the former Portuguese names and their English equivalents. These legacy names occur there solely to document and support older inputs. The complete source and output schema uses the English names.

Directions are `forward`, `backward`, `stable`, and `undetermined`. Adverse actions are `retained`, `excluded`, and `reclassified`. The correlation coefficients, absolute weights, selection thresholds, and metric formulas are unchanged.

Output area folders use normalized English names, for example `country/Brazil` and `region/World`. Geographic codes remain the selection keys. The existing unique run suffix preserves prior executions.

## Reports

The `docs/` directory reserves space for new English methodological PDFs. The previous reports are superseded and have not been copied into this directory.
