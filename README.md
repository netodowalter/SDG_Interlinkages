# SDG Interlinkages

Explore directed networks of collaboration and neglect among Sustainable Development Goal (SDG) targets using IGES/JRC relationships and UNSD observations, or annual SDGIndex indicator scores.

The Gradio application and command-line interface use the same Python analysis service. Local SDGIndex inputs cover 169 countries and 14 regions or aggregates. Each execution exports workbooks, node and edge tables, and four network images.

## Windows application

Install Python 3.10 or later with the `py` launcher or `python` available on PATH. Download and extract the complete repository or clone it, then double-click `launch_app.bat` in the repository root.

The launcher creates or reuses `.venv`, installs `requirements-app.txt`, and opens the application in your browser. The first installation needs access to the Python package index. Keep the terminal open while using the app. If the browser does not open automatically, copy the local URL shown in the terminal. Press Ctrl+C to stop the server.

| Tab | Input | Correlation |
| --- | --- | --- |
| IGES/JRC | Select a UNSD region or country. Optionally upload a previously collected UNSD CSV for the selected area. | Pearson |
| SDGIndex | Select a region, aggregate, or country from the supplied annual-score workbooks. | Pearson, Spearman, or both |

Choose the scope and area, then select **Run analysis**. The application displays the first ten rows of each ranking and the four direction-based highlight groups when eligible targets exist. Click a ranking row to see its indicator. The gallery displays the complete network, synergies, trade-offs, and the experimental Two-step interface. All four PNGs use the same four highlight groups, smaller maximum icon sizes, collision-aware spacing, and a complete legend for link colors and icon borders. Disconnected components are laid out separately and packed with compact gaps; their displayed separation does not encode a statistical distance. Download individual files or the complete execution ZIP.

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

The figure layout uses forces and a fixed random seed. Labels show target numbers. Distinct SDGIndex indicators mapped to the same target retain distinct composite node IDs in the tables. In the complete network, groups a/c have white/gray borders and groups b/d have yellow/red borders. Synergies from backward-moving sources use translucent burgundy; trade-offs from those sources use translucent gray.

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

**SDGIndex: performance-time rankings (no semantic ambition).** For each connected indicator, use its latest finite score S and the existing 2000–2025 slope v (score points/year). Forward indicators have `years_to_target = max(0, 100-S)/v`; backward indicators have `years_to_zero = max(0, S)/abs(v)`. Scores already at the relevant boundary have zero remaining years. Stable/undetermined trends have no finite time and are excluded from time rankings. Times are conditional linear extrapolations, not forecasts, with no fixed deadline. Excel retains numeric precision and displays ordinary decimal years to three places; Gradio does likewise.

Rank within progress direction, using all connected indicators. Colab/Neglect and receipt/sending rankings require positive weights or metric values. Each ranking has at most 10 entries; exact ties are resolved by stable node ID. Intersections are not refilled:

| Group | Intersection and exclusions |
|---|---|
| a · Collaborators with short target times | Top 10 forward Colab ∩ 10 shortest target times, excluding the top 10 receivers in group b |
| b · Dependent collaborators | Top 10 forward Colab ∩ top 10 forward recipients of total weighted trade-offs from backward sources |
| c · Resilient neglected indicators | Top 10 backward Neglect ∩ 10 longest times to zero, excluding the top 10 backward synergy senders in group d |
| d · Propagating neglected indicators | Top 10 backward Neglect ∩ top 10 backward synergy senders, irrespective of time to zero |

“Dependent” is an exploratory network label, not evidence of a causal mechanism. Group membership, input scores/slopes, times, all six rank positions, and weighted receipts/sending are exported. The complete network highlights the four groups; the synergy and trade-off views retain those same category borders for highlighted nodes present in each view.

**IGES/JRC:** retain the current semantic-ambition criteria (>0.6 for group a; <0.6 for group c), direction filters, receiver/sender exclusions, and intersections. Only widen the ranking cutoffs from five to ten, retaining ties at the tenth position. No SDGIndex performance-time criterion is applied to IGES/JRC.

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

Tests cover measure identity, indicator directionality, temporal reclassification boundaries, highlight rules, and correlations against SciPy. The synthetic UNSD fixture supports offline IGES/JRC validation.

### Experimental network view

The existing complete network is retained alongside an additional **Two-step interface** view, with the same legends and an experimental-layout note. See [the layout documentation](docs/two-step-interface-layout.md) for its display score, positioning and interpretation.

