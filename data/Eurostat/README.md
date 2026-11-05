# Eurostat test inputs (branch `europe_test`)

Test of the SDGIndex procedure with the EU SDG indicator set published by Eurostat, which has longer
and less carried-over national series than the SDR scores. Countries: Finland (best-rated statistical
system, as in Section 7 of the article) and Bulgaria (lowest GDP per capita in the EU; 59 indicators
pass the completeness rule in 2005–2024, against 61 for Finland).

| Path | Contents |
| --- | --- |
| `csv/` | the 113 SDMX-CSV downloads of the EU SDG indicator set |
| `selection.json` | headline series per dataset (dimension filter), desired direction, editorial target; excluded datasets and why |
| `mapping_eurostat.json` | indicator → target and goal, in the format of `data/SDGIndex/mapping.json` |
| `countries/FIN_Finland.xlsx`, `countries/BGR_Bulgaria.xlsx` | `Component_observations` in the package format, plus `Raw_values`, `Coverage` and `README` |

Window 2005–2024 (20 years). Indicators are kept with at most 6 missing years and no run of more than 3
(the rule of `scripts/raw_sdgindex.py`); gaps are filled with the IGES/JRC CAGR rule. Scores are min-max
over all Eurostat observations of each series, oriented so that 100 is best. The transform is linear and
never clips, so correlations and trend directions are those of the raw values with the normative sign.

```
python scripts/eurostat_prepare.py                      # rebuild mapping and country workbooks
python scripts/eurostat_run.py FIN BGR                  # package procedure, Pearson and Spearman; ZIP per run
python scripts/eurostat_validity.py FIN --top-n 3       # Section 7 tests (null model always cut-off 3)
python scripts/eurostat_validity.py FIN --top-n 10
```

The package code is unchanged: the runners point the service and `scripts/validity_sdgindex.py` to these
files and set the window. Window variants of the tests start in 2010 and 2015. Surrogates are also run on
residuals from a linear trend.

## Variant: one indicator per target

`countries_one_per_target/` keeps, for each target, only the indicator with the largest variance of its 0–100
score in the window, chosen per country (43 indicators for Finland, 41 for Bulgaria; 17 SDGs in both). The
`Coverage` sheet records the variance of every kept series and which indicator displaced each dropped one.

```
python scripts/eurostat_prepare.py --one-per-target
python scripts/eurostat_run.py FIN BGR --inputs countries_one_per_target
python scripts/eurostat_validity.py FIN --inputs countries_one_per_target --top-n 3
python scripts/eurostat_validity.py FIN --inputs countries_one_per_target --top-n 10
```
