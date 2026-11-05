# Validity and sensitivity of SDGIndex roles: Brazil, Finland and Norway

Results of `python scripts/validity_sdgindex.py ISO3 --replicates 200 --surrogates 200` (November 2026). The workbook is written to `output/validity/<ISO3>_validity.xlsx` (not versioned). Main specification: Pearson, levels, 2000–2025, p < 0.10. Each of the six roles (`improvement_sender`, `improvement_receiver`, `improvement_relay`, `deterioration_sender`, `deterioration_receiver`, `deterioration_relay`) selects its top 3 positive values with no exclusions and no backfilling (`ROLE_TOP = 3`); stability variants also report `--top-n 10`.

## 1. Surrogates: how much link density comes from persistence

Each of the 101 series is replaced by an independent Fourier phase-randomised surrogate, which keeps its power spectrum and autocorrelation but destroys synchrony. The table gives the share of the 3,079 tested cross-SDG pairs with p < 0.10 in Brazil.

| Basis | Observed | Surrogates, mean | Surrogates, 95th pct. | Excess |
|---|---|---|---|---|
| Levels | 71.4% | 48.4% | 49.8% | 23.0 pp |
| First differences | 13.8% | 10.1% | 10.9% | 3.7 pp |

With levels, independent series with the observed persistence pass the filter in about half of all pairs under raw FFT phase randomisation (and in 74.3% when linear trends are separated before phase randomisation of the residuals), against a nominal 10%. With first differences, surrogates return to the nominal level (10.1%–11.3%) and the observed excess is small (2.5–3.7 pp). The median series has 9 of its 25 annual changes equal to zero in Brazil (15 in Finland, 14 in Norway), which reflects carried values in the supplied scores and weakens tests on changes.

## 2. Null model: what degree and direction alone produce

The null model keeps every node's performance direction, its numbers of sent and received arcs and the multiset of weights, and rewires partners at random (directed double-edge swaps, no self-loops, no duplicates, no pairs within one SDG). Arcs between improving and deteriorating nodes take the type the classification rule gives. Interface and subsystem measures and the six roles (top 3 per role, no exclusions, no backfilling) are recomputed for each of 200 rewired networks.

| Role | BRA Jaccard | FIN Jaccard | NOR Jaccard | BRA p < 0.05 | FIN p < 0.05 | NOR p < 0.05 |
|---|---|---|---|---|---|---|
| Improvement sender | 0.30 | 0.14 | 0.18 | 0 | 0 | 0 |
| Improvement receiver | 0.32 | 0.25 | 0.19 | 1 (`7.1 cleanfuel`) | 1 (`9.c intuse`) | 0 |
| Improvement relay | 0.22 | 0.37 | 0.44 | 2 (`4.6 literacy`, `6.1 water`) | 2 (`15.1 cpta`, `17.1 govex`) | 3 (`12.4 nprod`, `13.2 co2gcp`, `14.5 cpma`) |
| Deterioration sender | 0.70 | 0.51 | 0.67 | 1 (`15.5 redlist`) | 1 (`15.5 redlist`) | 2 (`2.2 obesity`, `6.2 sanita`) |
| Deterioration receiver | 0.57 | 0.63 | 0.74 | 3 (`2.2 obesity`, `2.4 trophic`, `8.8 rights`) | 1 (`4.1 primary`) | 0 |
| Deterioration relay | 0.65 | 0.56 | 0.25 | 0 | 0 | 0 |

p is the share of rewired networks in which the member's role score is at least the observed one. Roles on the deteriorating side (`Deterioration sender`, `Deterioration receiver`, `Deterioration relay`) are largely reproduced by degree and direction (mean Jaccard 0.51 to 0.74 across the three countries, except Norway's `Deterioration relay` at 0.25), against 0.06 to 0.10 for two random choices of three among the deteriorating targets.

## 3. Sensitivity of role membership

Jaccard similarity of each role with the main specification (1 = identical membership).

### Cut-off of 10 per role (`--top-n 10`)

| Variant | Country | Improvement sender | Improvement receiver | Improvement relay | Deterioration sender | Deterioration receiver | Deterioration relay |
|---|---|---|---|---|---|---|---|
| Spearman | Brazil | 0.43 | 0.25 | 0.18 | 0.67 | 0.67 | 0.82 |
|  | Finland | 0.54 | 0.33 | 0.54 | 0.67 | 0.67 | 0.67 |
|  | Norway | 0.18 | 0.18 | 0.54 | 0.82 | 1.00 | 0.67 |
| Window 2010–2025 | Brazil | 0.25 | 0.18 | 0.25 | 0.25 | 0.82 | 0.33 |
|  | Finland | 0.33 | 0.33 | 0.67 | 0.67 | 0.43 | 0.54 |
|  | Norway | 0.43 | 0.18 | 0.54 | 0.67 | 0.82 | 0.67 |
| Window 2015–2025 | Brazil | 0.18 | 0.00 | 0.33 | 0.25 | 0.43 | 0.33 |
|  | Finland | 0.25 | 0.18 | 0.33 | 0.43 | 0.33 | 0.33 |
|  | Norway | 0.18 | 0.33 | 0.43 | 0.33 | 0.43 | 0.33 |
| First differences | Brazil | 0.05 | 0.11 | 0.33 | 0.54 | 0.18 | 0.25 |
|  | Finland | 0.11 | 0.18 | 0.33 | 0.67 | 0.25 | 0.25 |
|  | Norway | 0.05 | 0.05 | 0.25 | 0.25 | 0.43 | 0.54 |
| BH q < 0.10 | Brazil | 0.82 | 0.82 | 0.82 | 1.00 | 1.00 | 1.00 |
|  | Finland | 1.00 | 0.82 | 1.00 | 0.82 | 0.67 | 0.82 |
|  | Norway | 0.67 | 0.82 | 1.00 | 0.82 | 1.00 | 0.82 |

### Cut-off of 3 per role (`--top-n 3`, main role specification)

| Variant | Country | Improvement sender | Improvement receiver | Improvement relay | Deterioration sender | Deterioration receiver | Deterioration relay |
|---|---|---|---|---|---|---|---|
| Spearman | Brazil | 0.00 | 0.20 | 0.20 | 0.50 | 0.20 | 1.00 |
|  | Finland | 0.20 | 0.20 | 0.00 | 0.50 | 1.00 | 0.20 |
|  | Norway | 0.20 | 0.00 | 0.20 | 1.00 | 0.50 | 0.50 |
| Window 2010–2025 | Brazil | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.50 |
|  | Finland | 0.50 | 0.00 | 0.20 | 0.50 | 0.20 | 0.50 |
|  | Norway | 0.00 | 0.00 | 0.50 | 0.20 | 0.50 | 0.20 |
| Window 2015–2025 | Brazil | 0.20 | 0.00 | 0.20 | 0.20 | 0.20 | 0.50 |
|  | Finland | 0.00 | 0.00 | 0.00 | 0.50 | 0.20 | 0.20 |
|  | Norway | 0.00 | 0.20 | 0.20 | 0.50 | 0.50 | 0.20 |
| First differences | Brazil | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 | 0.20 |
|  | Finland | 0.20 | 0.00 | 0.20 | 0.20 | 0.00 | 0.00 |
|  | Norway | 0.00 | 0.00 | 0.20 | 0.20 | 1.00 | 0.00 |
| BH q < 0.10 | Brazil | 0.50 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
|  | Finland | 0.50 | 1.00 | 1.00 | 0.50 | 1.00 | 0.50 |
|  | Norway | 0.50 | 0.50 | 0.50 | 1.00 | 0.50 | 0.50 |

With the cut-off of 3, between levels and annual changes, `Improvement receiver` has Jaccard 0 in all three countries, `Improvement sender` and `Deterioration receiver` have Jaccard 0 in Brazil, and `Deterioration relay` has Jaccard 0 in Finland and Norway.

## 4. Surrogates across the four specifications (Section 7.2)

**Surrogates (% of cross-SDG pairs with p < 0.10, observed / surrogates).**

| Source | BRA levels | FIN levels | NOR levels | BRA changes | FIN changes | NOR changes |
|---|---|---|---|---|---|---|
| SDG Index, normalised scores | 71 / 48 | 52 / 37 | 54 / 40 | 14 / 10 | 11 / 10 | 11 / 10 |
| SDG Index, raw values | 80 / 50 | 62 / 43 | 55 / 45 | 20 / 10 | 15 / 10 | 19 / 10 |
| UN series, 2010–2023, country-reported | 43 / 27 | 35 / 24 | 40 / 27 | 14 / 10 | 11 / 10 | 15 / 10 |
| IGES/JRC procedure | 67 / 50 | 65 / 44 | 61 / 45 | 22 / 10 | 16 / 10 | 19 / 10 |
