# SDG Interlinkages

Explore directed networks of collaboration and neglect among Sustainable Development Goal (SDG) targets using IGES/JRC relationships and UNSD observations, or annual SDGIndex indicator scores.

## Status (November 2026)

Development of the package has stopped. The statistical tests reported in Section 7 of the methodological article ([`docs/SDG_Interlinkages_methodological_article.md`](docs/SDG_Interlinkages_methodological_article.md)) were run for Brazil, Finland and Norway with SDG Index normalised scores, SDR raw values, UN series and the IGES/JRC procedure. They show that correlations between the published national annual series cannot support valid inference about interlinkages, and that network analysis built on them cannot identify the roles: in levels, independent surrogate series pass the significance filter in 24% to 50% of pairs and roles follow each indicator's direction, degree and trend linearity; in annual changes, what remains is small and indistinguishable from artefacts of filling, carried values and bounded scales. Finland and Norway, among the countries with the best-rated statistical systems, show the same pattern.

The performance-based reading of synergies and trade-offs remains a conceptual requirement for any interlinkage analysis. The package is kept as an open, documented implementation for verification and replication of these results, not as a tool for prioritising targets. Test scripts and results: [`docs/validity_sdgindex.md`](docs/validity_sdgindex.md) and the section [Validity tests](#validity-tests) below. Open items are in [`TODO.md`](TODO.md).

## Overview

The Gradio application and command-line interface use the same Python analysis service. Local SDGIndex inputs cover 169 countries and 14 regions or aggregates. Each execution exports workbooks, node and edge tables, and four network images; IGES/JRC runs add a link-share weighted workbook and four weighted images (`_pond`).

## Windows application

Install Python 3.10 or later with the `py` launcher or `python` available on PATH. Download and extract the complete repository or clone it, then double-click `launch_app.bat` in the repository root.

The launcher creates or reuses `.venv`, installs `requirements-app.txt`, and opens the application in your browser. The first installation needs access to the Python package index. Keep the terminal open while using the app. If the browser does not open automatically, copy the local URL shown in the terminal. Press Ctrl+C to stop the server.

| Tab | Input | Correlation |
| --- | --- | --- |
| IGES/JRC | Select a UNSD region or country. Optionally upload a previously collected UNSD CSV for the selected area. | Pearson |
| SDGIndex | Select a region, aggregate, or country from the supplied annual-score workbooks. | Pearson, Spearman, or both |

Choose the scope and area, then select **Run analysis**. The application displays the first ten rows of each ranking and the six interface roles when eligible targets exist. Click a ranking row to see its indicator. The gallery displays the complete network, synergies, trade-offs, and the experimental Two-step interface. All four PNGs use the same six role borders, smaller maximum icon sizes, collision-aware spacing, and a complete legend for link colors and icon borders. Disconnected components are laid out separately and packed with compact gaps; their displayed separation does not encode a statistical distance. Download individual files or the complete execution ZIP.

IGES/JRC tables show semantic **Ambitiousness**; SDGIndex tables show performance times in years. The IGES/JRC region selector additionally includes the UNSD catalog codes for OECD (198) and World Bank income groups (910, 911, 912, 914). Verification returned no observations for these aggregate codes, so listing them does not guarantee a runnable network. See [aggregate availability and comparability](docs/iges-comparison-regions.md). BRICS groups have no code in the verified UNSD catalog.

The two tabs share a calculation queue. Choosing **Both** produces separate results for each method. Completed runs remain in `output/`; Gradio also keeps temporary copies of files served to the browser.

## Linux and macOS application

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-app.txt
python app.py
```

## Command line

On Windows, double-click `launch.bat` to open the interactive terminal menu. It asks for the dataset, region/country scope, and area, in that order. SDGIndex runs both correlation methods by default.

With your virtual environment active, examples include:

```bash
python -m sdg --version IGES_JRC --scope country --area 76
python -m sdg --version IGES_JRC --scope region --area 1
python -m sdg --version IGES_JRC --scope country --area 76 --csv brazil_collection.csv
python -m sdg --version SDGIndex --scope country --area BRA --method pearson
python -m sdg --version SDGIndex --scope region --area World --method both
```

Use `--output PATH` to choose another results root. Pass the same options to `launch.bat` on Windows. Terminal-only installations need `requirements.txt`.

Use `python -m sdg` for terminal commands and `sdg.service` for Python integrations. The previous option names remain accepted as aliases and produce English outputs.

## Results

The area directory uses its name rather than its geographic code. Names are normalized to portable ASCII filenames. Each run receives a UTC timestamp and unique suffix.

```text
output/IGES_JRC/country/Brazil/<run>/
output/IGES_JRC/region/World/<run>/
output/SDGIndex/country/Brazil/<run>/pearson/
output/SDGIndex/region/World/<run>/spearman/
```

The numeric/ISO code remains the selection identifier and is recorded in the underlying data. Existing execution directories are preserved. The `.gitignore` excludes generated results while tracking the two top-level output placeholders.

| File | Contents |
| --- | --- |
| `*_full.xlsx` | Source observations, calculations, metrics, highlights, and method-specific audit evidence |
| `*_interlinkages.xlsx` | Rankings, highlights, diagnostics, and adverse cases |
| `*_network.csv` | Directed edges, final interaction types, and weights |
| `*_nodes.csv` | Nodes, target identities, and attributes |
| `*_full.png` | Complete network |
| `*_synergy.png` | Synergy network |
| `*_trade-off.png` | Trade-off network |
| `*_two_step_interface.png` | Two-step interface view (experimental layout) |
| `*_interlinkages_pond.xlsx` | IGES/JRC only: link-share weighted rankings, roles, interface measures and the `Weighting` comparison sheet |
| `*_full_pond.png`, `*_synergy_pond.png`, `*_trade-off_pond.png`, `*_two_step_interface_pond.png` | IGES/JRC only: the four views drawn from the weighted measures |

The figure layout uses forces and a fixed random seed. Labels show target numbers. Distinct SDGIndex indicators mapped to the same target retain distinct composite node IDs in the tables. Icon borders mark the six roles: I-1 white, I-2 yellow, I-3 blue, D-1 gray, D-2 red, D-3 orange. Synergies from backward-moving sources use translucent burgundy; trade-offs from those sources use translucent gray.

## Analytical procedure

### IGES/JRC

The local area catalog uses UNSD M49 codes and the continental tree. Collection queries the UNSD API by indicator in paginated batches. A saved CSV in the flattened API format can be reused offline for its matching geographic code.

The pipeline selects series, fills eligible gaps using series-specific CAGR rules, consolidates shared measures, and resolves the desired direction for the actual indicator series. It computes Pearson correlations for eligible series pairs and applies the directed IGES/JRC evidence rules. Temporal classification precedes degree calculations and rankings.

Series selection uses the greatest number of distinct original numeric years during 2000–2025, breaking ties by IGES order. CAGR uses positive endpoint pairs, or a constant zero for two zero endpoints. Bounds apply to generated values. Shared API series/dimensions/units enter calculations through one representative target and are documented in `Target_representation`.

### SDGIndex

The supplied workbooks contain annual observations for 169 countries and 14 regions/aggregates. The editorial mapping associates 101 component indicators with SDG targets. The analysis reads `Component_observations` and correlates annual score levels over 2000–2025. It excludes all pairs within the same SDG or target before tests and degree calculations.

Pairs require at least eight matched observations, a nonzero coefficient, and nominal p < 0.10. Lagged and conditional tests provide exploratory orientation. Pairs without a uniquely supported direction receive two arcs with their direction evidence recorded. Benjamini–Hochberg q-values are available for sensitivity analysis.

### Temporal classification and metrics

The desired direction and local linear slope determine whether each node moves forward, backward, is stable, or has undetermined direction. An initially discordant relationship is excluded if either time R² is below 0.1, or if either time R² is below 0.2 and the absolute association coefficient is below 0.4. Other discordant pairs with defined directions change interaction type. Original coefficients are preserved; weights use their absolute value. `Adverse cases` records excluded and reclassified arcs.

- **Colab** equals outgoing weighted synergies minus outgoing weighted trade-offs.
- **Neglect** equals incoming weighted trade-offs plus incoming weighted synergies from backward-moving sources.

**SDGIndex: performance-time rankings (no semantic ambition).** For each connected indicator, use its latest finite score S and the existing 2000–2025 slope v (score points/year). Forward indicators have `years_to_target = max(0, 100-S)/v`; deteriorating indicators have `years_to_zero = max(0, S)/abs(v)`. Scores already at the relevant boundary have zero remaining years. Stable/undetermined trends have no finite time and are excluded from time rankings. Times are conditional linear extrapolations, not forecasts, with no fixed deadline. Excel retains numeric precision and displays ordinary decimal years to three places; Gradio does likewise.

Rank within performance direction, using all connected indicators. Rankings require positive values. Each role lists at most three indicators, the three highest values of its own score, selected independently, so an indicator can hold more than one role (SDGIndex: exact ties resolved by stable node ID; IGES/JRC: ties at third place retained). The top 10 is used only for the two exclusion rankings below (top senders of trade-offs to deterioration, C, and top senders of synergy from deterioration, B). Intersections are not refilled.

After performance-based classification, synergies link indicators moving in the same direction and trade-offs link indicators moving in opposite directions. The six roles in `sdg/engine/modules/roles.py` separate what reaches each indicator across that interface from what it passes on:

| Measure | Defined for | Meaning |
|---|---|---|
| R: `tradeoff_received_from_backward` | improving | trade-off weight received from deteriorating sources |
| `forward_synergy_sent` | improving | synergy weight passed to improving indicators |
| φ: `forward_ratio` | improving | `forward_synergy_sent / R` |
| `tradeoff_sent_to_backward` | improving | trade-off weight sent to deteriorating indicators (cost downstream) |
| T⁺: `tradeoff_received_from_forward` | deteriorating | trade-off weight received from improving sources |
| S⁻: `synergy_received_from_backward` | deteriorating | synergy weight received from deteriorating sources |
| `synergy_sent_to_backward` | deteriorating | synergy weight passed to deteriorating indicators |
| `bridge_flow` | deteriorating | T⁺ × `synergy_sent_to_backward` = all two-step paths improving → k → deteriorating |
| `relay_flow` | deteriorating | S⁻ × `synergy_sent_to_backward` |

Links involving stable or undetermined indicators do not enter these measures.

| Role | Selection |
|---|---|
| I-1 · Contributors | Three highest Colab among improving indicators, excluding the top 10 senders of trade-offs to deterioration (C) |
| I-2 · Dependent contributors | Three highest R among improving indicators with φ ≥ 1: gains associated with losses elsewhere, passed forward |
| I-3 · Isolated beneficiaries | Three highest R among improving indicators with φ < 1: gains associated with losses elsewhere, not passed forward |
| D-1 · Exposed targets | Three highest Neglect among deteriorating indicators, excluding the top 10 senders of synergy from deterioration (B) |
| D-2 · Transmission bridges | Three highest `bridge_flow` |
| D-3 · Deterioration relays | Three highest `relay_flow` |

Context characterises roles but does not filter them. Every selected indicator is exported with its years to target (improving) or years to zero (deteriorating) in SDGIndex, or its semantic ambitiousness in IGES/JRC, so priorities can be set within each role (for example, a transmission bridge close to zero is more urgent than one deteriorating slowly). The isolation threshold φ < 1 is absolute because in dense networks almost every receiver also sends substantial synergy, so a relative cut-off would label strong spreaders as isolated.

“Dependent”, “bridge” and “relay” are exploratory network labels, not evidence of causal mechanisms. Role membership, all rank positions and every interface measure are exported (`Interface_measures`, `Highlights`). Icon borders mark the same six roles in all four PNGs.

### Link-share weighted version (IGES/JRC)

Every IGES/JRC run also writes a weighted version, with its own workbook and figures ending in `_pond`. It applies the factor of NT Dinte 77 (eq. 1): P_i = L_i / Σ L_j, the target's share of the arcs it sends (P_out) or receives (P_in) in the final network. Sent measures (Colab, synergy and trade-off sent) are divided by the sent share, received measures (Neglect, trade-off and synergy received) by the received share, and bridge and relay flows by both; φ is unchanged. Roles, node sizes and Two-step positions are recomputed from the weighted measures.

Shares are reported relative to the mean (P_i × number of targets), so a target with the mean number of links keeps its unweighted value; rankings are identical to dividing by P_i itself.

Literature-derived networks can connect well-studied targets more often. The weighted version reduces the advantage of many links over strong ones. It is a check, not a correction: the `Weighting` sheet compares original and weighted ranks for Colab and Neglect, and flags targets in the top 10 of Colab that enter the top 10 of weighted Neglect, the most serious discrepancy identified by the NT. SDGIndex has no weighted version, because its links are estimated from data for every eligible pair rather than recorded by the literature.

These associations and their exploratory orientations do not establish causality. Nominal p-values do not correct for autocorrelation. Supplied normalized series may contain carried/interpolated observations. These methodological conventions are preserved in the English migration.

## Official terminology and documentation

`data/un_sdg_catalogue.json` stores the official English wording of all 17 goals, 169 targets, and indicator entries in the UNSD 2026-refinement framework, with its source URL. `sdg_descriptions.xlsx` provides the runtime reference table. SDGIndex component descriptions and IGES proxy descriptions retain the definitions of their actual measures.

[Official UN Sustainable Development Goals](https://sdgs.un.org/goals) · [UNSD global indicator framework](https://unstats.un.org/sdgs/indicators/indicators-list/)

The `docs/` directory is reserved for revised methodological PDFs and supporting documentation. See its README and the English migration notes for schema changes and provenance.

## Python integration and structure

```python
from sdg.service import list_areas, run_analysis

countries = list_areas("SDGIndex", "country")
folder = run_analysis("SDGIndex", "country", "BRA", method="pearson")
print(countries["BRA"], folder)
```

`output_dir` sets the writable results root. For IGES/JRC, `csv_path` supplies an existing collection. The service returns the results folder after all requested methods and exports finish.

| Path | Purpose |
| --- | --- |
| `app.py` | Gradio tabs, area selection, result display, and ZIP downloads |
| `sdg/service.py` | Shared area catalog and analysis orchestration |
| `sdg/engine/modules/` | Collection, preparation, correlations, directionality, trends, and rankings |
| `sdg/engine/bases/` | IGES/JRC rules and supporting reference tables |
| `sdg/render.py` | PNG network export |
| `data/SDGIndex/` | Country/region workbooks and indicator-to-target mapping |
| `data/icons/` | English SDG icons |
| `tests/` | Regression tests and synthetic verification data |

## Tests

```bash
python -m unittest discover -s tests
```

Tests cover measure identity, indicator directionality, temporal reclassification boundaries, interface roles (including a synthetic worked example), and correlations against SciPy. The synthetic UNSD fixture supports offline IGES/JRC validation.

## Validity tests

The scripts below reproduce Section 7 of the methodological article (ISO3 = BRA, FIN, NOR; UNSD area = 76, 246, 578; `database_2026_sdg_index.xlsx` is the SDR 2026 database; UNSD CSVs from `download_unsd.bat`). Results go to `output/validity/` (not versioned) and are summarised in [`docs/validity_sdgindex.md`](docs/validity_sdgindex.md).

| Script | Test |
| --- | --- |
| `scripts/validity_sdgindex.py ISO3 [--top-n N]` | SDG Index normalised scores: surrogates, degree- and direction-preserving null model, role stability across coefficient, window, basis and selection rule |
| `scripts/raw_sdgindex.py DATABASE ISO3` | SDR raw values with completeness rule and CAGR filling; three progress-direction options |
| `scripts/raw_detrended.py DATABASE ISO3` | SDR raw values in levels, annual changes and trend residuals |
| `scripts/unsd_undirected.py CSV --end 2023 --drop-natures M E G` | UN series reported by the country, read without link direction |
| `scripts/validity_iges.py CSV AREA` | IGES/JRC procedure in levels and annual changes |
| `scripts/iges_nofilter.py CSV AREA` | IGES/JRC with and without the significance filter |
| `scripts/unsd_coverage.py CSV` | UN targets covered with and without the normative-direction table |
| `scripts/figure1_brazil.py` | Figure 1 of the article (Brazil's bridge and isolated beneficiary) |

### Experimental network view

The existing complete network is retained alongside an additional **Two-step interface** view, with the same legends and an experimental-layout note. See [the layout documentation](docs/two-step-interface-layout.md) for its display score, positioning and interpretation.


### Performance terminology

The interfaces use **Improvement**, **Deterioration**, **Stable** and **Undetermined**. Improvement and deterioration refer to movement towards or away from the desired outcome, not whether a target is on track for 2030. Stable indicates negligible fitted change; undetermined indicates insufficient evidence. Existing internal direction codes (`forward`, `backward`, `stable`, `undetermined`) are retained for compatibility with saved analyses. This terminology update does not change calculations, rankings or classification criteria.
