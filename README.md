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

Rank within performance direction, using all connected indicators. Rankings require positive values. Each ranking has at most 10 entries (SDGIndex: exact ties resolved by stable node ID; IGES/JRC: ties at the tenth position retained). Intersections are not refilled.

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
| I-1 · Contributors | Top Colab, excluding top R and top senders of trade-offs to deterioration |
| I-2 · Dependent contributors | Top R with φ ≥ 1: gains associated with losses elsewhere, passed forward |
| I-3 · Isolated beneficiaries | Top R with φ < 1: gains associated with losses elsewhere, not passed forward |
| D-1 · Exposed targets | Top Neglect, excluding top senders of synergy from deterioration, bridges and relays |
| D-2 · Transmission bridges | Top `bridge_flow` |
| D-3 · Deterioration relays | Top `relay_flow`, excluding bridges |

Context characterises roles but does not filter them. Every selected indicator is exported with its years to target (improving) or years to zero (deteriorating) in SDGIndex, or its semantic ambitiousness in IGES/JRC, so priorities can be set within each role (for example, a transmission bridge close to zero is more urgent than one deteriorating slowly). The previous filters selected near-achieved contributors and slowly deteriorating exposed indicators, and pointed in opposite directions in the two procedures. The isolation threshold φ < 1 is absolute because in dense networks almost every receiver also sends substantial synergy, so a relative cut-off would label strong spreaders as isolated.

“Dependent”, “bridge” and “relay” are exploratory network labels, not evidence of causal mechanisms. Role membership, all rank positions and every interface measure are exported (`Interface_measures`, `Highlights`). Icon borders mark the same six roles in all four PNGs.

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

Tests cover measure identity, indicator directionality, temporal reclassification boundaries, interface roles (including the worked example of the methodological article), and correlations against SciPy. The synthetic UNSD fixture supports offline IGES/JRC validation.

### Experimental network view

The existing complete network is retained alongside an additional **Two-step interface** view, with the same legends and an experimental-layout note. See [the layout documentation](docs/two-step-interface-layout.md) for its display score, positioning and interpretation.


### Performance terminology

The interfaces use **Improvement**, **Deterioration**, **Stable** and **Undetermined**. Improvement and deterioration refer to movement towards or away from the desired outcome, not whether a target is on track for 2030. Stable indicates negligible fitted change; undetermined indicates insufficient evidence. Existing internal direction codes (`forward`, `backward`, `stable`, `undetermined`) are retained for compatibility with saved analyses. This terminology update does not change calculations, rankings or classification criteria.
