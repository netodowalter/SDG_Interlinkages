# Validity and sensitivity of SDGIndex roles: Brazil

Results of `python scripts/validity_sdgindex.py BRA --replicates 500 --surrogates 200` (branch `validity-tests`, November 2026). The workbook is written to `output/validity/BRA_validity.xlsx` (not versioned). Main specification: Pearson, levels, 2000–2025, p < 0.10, top 10, φ < 1.

## 1. Surrogates: how much link density comes from persistence

Each of the 101 series is replaced by an independent Fourier phase-randomised surrogate, which keeps its power spectrum and autocorrelation but destroys synchrony. The table gives the share of the 3,079 tested cross-SDG pairs with p < 0.10.

| Basis | Observed | Surrogates, mean | Surrogates, 95th pct. | Excess |
|---|---|---|---|---|
| Levels | 71.4% | 48.4% | 49.8% | 23.0 pp |
| First differences | 13.8% | 10.1% | 10.9% | 3.7 pp |

With levels, independent series with the observed persistence pass the filter in about half of all pairs, against a nominal 10%. About two thirds of the observed density is therefore what persistence and trends alone would produce. The observed share still exceeds every surrogate replicate (p ≈ 0.005), so co-movement adds something beyond persistence. With first differences, surrogates return to the nominal level and the observed excess is small (3.7 pp). The median series has 9 of its 25 annual changes equal to zero, which reflects carried values in the supplied scores and weakens tests on changes.

## 2. Null model: what degree and direction alone produce

The null model keeps every node's performance direction, its numbers of sent and received arcs and the multiset of weights, and rewires partners at random (directed double-edge swaps, no self-loops, no duplicates, no pairs within one SDG). Arcs between improving and deteriorating nodes take the type the classification rule gives. Colab, Neglect, interface measures and roles are recomputed for each of 500 rewired networks.

Mixing plateaus at about 31% of arcs moved, from 10 to 300 swaps per arc: at 51% density the degree sequence alone fixes about 70% of the arcs.

| Role | Observed | Null, mean size | Mean Jaccard with null | Members with p < 0.05 |
|---|---|---|---|---|
| I-1 Contributors | 6 | 5.7 | 0.22 | 2 (5.5 parl, 7.1 elecac) |
| I-2 Dependent contributors | 10 | 10.0 | 0.33 | 3 (1.2 lmicpov, 11.1 pipedwat, 7.1 cleanfuel) |
| I-3 Isolated beneficiaries | 0 | 0.0 | — | — |
| D-1 Exposed | 3 | 2.4 | 0.51 | 0 |
| D-2 Transmission bridges | 10 | 10.0 | 0.68 | 0 |
| D-3 Deterioration relays | 1 | 1.5 | 0.11 | 0 |

p is the share of rewired networks in which the member's role score is at least the observed one. Transmission bridges are largely reproduced by degree and direction: no bridge has a bridge flow above the null, and 7 of the 10 keep the bridge role in more than 60% of rewired networks (15.5 redlist in all of them). On the improving side, roles depend more on who is linked to whom, and five members exceed the null.

## 3. Sensitivity of role membership

Jaccard similarity of each role with the main specification (1 = identical membership).

| Variant | Arcs | I-1 | I-2 | D-1 | D-2 | D-3 |
|---|---|---|---|---|---|---|
| Spearman | 3,241 | 0.14 | 0.25 | 0.60 | 0.82 | 0 |
| First differences | 662 | 0.08 | 0.08 | 0 | 0.25 | 0 |
| Window 2010–2025 | 2,776 | 0.11 | 0.18 | 0.33 | 0.43 | 0 |
| Window 2015–2025 | 2,129 | 0 | 0 | 0 | 0.33 | 0 |
| BH q < 0.10 | 3,174 | 1 | 0.82 | 0.33 | 0.82 | 0.50 |
| Top 5 | 3,305 | 0.29 | 0.50 | 0 | 0.50 | 0 |
| Top 15 | 3,305 | 0.57 | 0.67 | 0.25 | 0.67 | 0 |
| Isolation φ = 0 | 3,305 | 1 | 1 | 1 | 1 | 1 |

Main specification: 3,305 arcs. I-3 is empty in all variants except first differences, so the isolation rule does not change any result. The BH selection barely changes the network, because almost all valid pairs are significant. Bridges are the most stable role across specifications. Those same bridges are the role the null model reproduces best, so their stability reflects degree and direction more than specific partners. Improving-side roles and relays change with the window, the coefficient and the basis.

In every variant, every surviving synergy between two nodes with a defined direction links nodes moving in the same direction. With levels, no discordant link is reclassified: all 42 are excluded. With first differences, 224 are reclassified, so co-movement in annual changes often disagrees with the direction of the long-run trend.

## 4. Raw indicator values (SDR 2026 database)

`python scripts/raw_sdgindex.py database_2026_sdg_index.xlsx BRA` (200 rewirings, 100 surrogates per basis). The script uses the sheet "All Raw Data" instead of the package's normalised scores. Indicators are kept only with at most 6 missing years in 2000–2025 and no run of more than 3. Gaps are filled by the IGES/JRC CAGR rule: 3 interpolated and 62 extrapolated values, none left empty. The original interaction is sign(r) × the normative signs of both indicators (Codebook: Optimum > Lower Bound gives +1). Orientation, the discordance rule and roles follow the main procedure. Three progress-direction options are compared: first vs last observation, linear trend of the filled raw series, and linear trend of the normalised score.

**Coverage.** 50 of the 101 indicators pass the completeness rule. Dropped indicators include three of the ten bridges of the main specification (8.8 rights, 16.5 cpi, 16.6 admin) and two of its three exposed targets (2.2 stunting, 2.2 wasting); in the normalised scores these series are largely carried values.

**Network.** 912 of 1,137 cross-SDG pairs (80%) pass p < 0.10; density 0.58–0.61, higher than in the main specification (0.51).

| | Endpoints | Raw trend | Score trend |
|---|---|---|---|
| Improving / deteriorating / other | 34 / 14 / 1 | 35 / 13 / 0 | 32 / 13 / 3 |
| Arcs | 1,365 | 1,370 | 1,372 |
| Reclassified / excluded arcs | 11 / 11 | 0 / 6 | 0 / 4 |

The three options agree on 45 of 50 directions. The five disagreements are flat or bounded series: 3.1 matmort and 3.3 tb (time R² ≤ 0.01), and 10.1 palma, 5.1 edat and 6.4 freshwat, whose normalised score is constant at a bound (stable in the score option).

**Roles.** Membership is almost identical across the three options; transmission bridges are the same ten in all three. Against the main specification restricted to the indicators kept here, bridges have Jaccard 0.70 and the exposed target 1.0. The new bridges in place of the dropped ones are 12.4 pollimp, 12.4 pollprod and 13.2 ghgimport.

**Surrogates.** Levels: 80.2% observed vs 50.5% for surrogates (excess 29.7 pp). First differences: 20.0% vs 10.3% (excess 9.6 pp), more than with the normalised scores (3.7 pp), which have many carried values.

**Null model.** Bridges are reproduced by degree and direction even more closely than in the main specification (mean Jaccard with the null 0.87; no bridge above the null). Dependent contributors: 4 to 6 members above the null at p < 0.05, depending on the option; contributors: 3.
