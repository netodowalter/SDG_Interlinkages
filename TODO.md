# TODO

Open items for the SDG Interlinkages package and the methodological article (`docs/SDG_Interlinkages_methodological_article.md`). The framework is experimental and preliminary.

Items in the first section can be done with the data already in the package and should be completed before the article is submitted; their results then enter the article (Sections 6 and 7). Items that depend on longer series or on other kinds of evidence are stated as limitations in Section 9 of the article and listed at the end of this file.

## Before submission: doable with current data

### Validity of roles

- [ ] **Null model.** Rewire links at random while keeping each node's performance direction and its numbers of sent and received links; recompute bridge and relay flows and role membership. Report whether observed bridges exceed the null distribution. Addresses the objection that, after reclassification, synergy ≈ "same direction" and trade-off ≈ "opposite directions", so roles might only reflect trend strength and degree.
- [ ] **Associations of changes, SDG Index.** Add an option to correlate first differences (or detrended scores) instead of levels. Trending series correlate strongly regardless of any relationship; the Brazil SDG Index network already links about half of all possible pairs (3,305 arcs, 81 indicators). About 25 annual changes per indicator are available.
- [ ] **Stability across windows, SDG Index.** Compare roles for 2000–2025 and 2010–2025.
- [ ] **Pooled panels, SDG Index.** Pool comparable countries (income group, BRICS) to gain power for orientation tests, as an alternative to longer national series.

### Sensitivity outputs

- [ ] Benjamini–Hochberg q-values as the active selection criterion (option).
- [ ] Pearson vs Spearman role membership (SDG Index).
- [ ] Alternative ranking cut-offs (top 5, top 15).
- [ ] Isolation threshold: strict zero forward synergy vs φ < 1.
- [ ] Alternative rules for uncertain JRC directions (Table 1 of the article).
- [ ] Alternative reclassification thresholds for discordant links, and exclusion of all discordant links.

### Comparisons (article Section 8)

- [ ] **Two procedures, same country.** Run IGES/JRC and SDG Index for the same country and tabulate links, directions and roles supported by one procedure but not the other.
- [ ] **Recurrences across countries.** Batch-run the SDG Index procedure for all 169 countries and 14 aggregates; tabulate how often each indicator takes each role, overall and by income group or BRICS.

### Runs

- [ ] Run IGES/JRC with real UNSD data (requires internet only) and inspect the weighted `_pond` outputs; so far tested only on the synthetic fixture.
- [ ] Run the Brazil IGES/JRC network for 2010–2023 with the VNR 2024 indicators to compare directly with the NT Dinte 77 categories.
- [ ] **Two synergy clusters.** On that network, check whether the two synergy clusters of NT Dinte 77 (Figure 5) coincide with the improving and deteriorating groups, and report the share of sign-classified synergies linking same-direction targets (98.5% in the Brazil SDG Index network; article Section 4.4). Check the performance direction of the apparent synergy bridges (10.1, 9.4, 8.5): under performance-based classification they should be stable or undetermined, or rest on discordant links (article Section 4.4). Repeat for other IGES/JRC countries.

### Visualisation

- [ ] **Two-step positions for improving nodes.** Currently placed by trade-off received from deterioration × synergy passed forward; an isolated beneficiary (low forward synergy) would be pushed away from the centre although it is an interface role. Option: place improving nodes by trade-off received only, so I-2 and I-3 both sit at the interface.
- [ ] Optional marker for urgency within roles (e.g. bridges with fewer than 15 years to zero).

### Article

- [ ] Report the results of the items above in Sections 6–7.
- [ ] Archive the release used in the article on Zenodo and cite its DOI; give the application a persistent address.
- [ ] Verify bibliographic details and add DOIs for Pradhan et al. (2017), Miola et al. (2019), Nilsson et al. (2017), Issa, Mezher and El Fadel (2024), Di Lucia, Slade and Khan (2022).
- [ ] Convert LaTeX equation blocks to Word equations in the `.docx` before submission.
- [ ] **Read Zhou and Moinuddin (2021)** (book chapter, Elsevier, doi 10.1016/B978-0-323-85512-9.00018-8), cited in Section 3.2 and Table 2 from its reproduction in Sota and Venghaus (2026). Check whether the typology goes beyond a conceptual table, confirm the row labels (development drag, coupled deterioration), and complete the reference (book title, editors, pages).
- [ ] **Check Feng et al. (2023)**, "Assessing progress and interactions toward SDG 11 indicators based on geospatial big data at prefecture-level cities" (cited by Khot et al. 2026), the only other title found that joins progress and interactions; cite in Section 3.2 if relevant.

## To consider

Ideas worth evaluating; not committed.

- [ ] **Transfer entropy for link orientation** (Warchold and Pradhan, 2025, recommended by Khot et al. 2026) as an alternative to lagged and conditional tests in the SDG Index procedure.

- [ ] **Progress direction less sensitive to the trend window**, borrowing from the UNSD Technical Note for Progress Assessment (SDG Report 2026):
    - a stagnation band (e.g. |annual rate in the desired direction| < 0.5%) classified as stable, so small slopes that flip sign with the period do not decide links and roles;
    - a 2015–latest window aligned with the Agenda and the UNSD convention, as an alternative or complement to 2000–2025;
    - requiring the same direction in both windows, otherwise undetermined;
    - the annual rate estimated by log-linear regression on all points rather than from the two endpoints (UNSD's endpoint CAGR is fragile to atypical first or last values); absolute change for series that are already rates or contain zeros or negatives.
  The UNSD distance-to-2030-target ratio needs numeric targets per series and measures sufficiency of pace rather than direction; if used, it belongs with context, not with link classification.
- [ ] **Check normative directions against the UNSD annex**, which lists "Increasing"/"Decreasing" for each series used in the global assessment; flag divergences from `indicator_directionality.xlsx`.

## Later: needs more or other data (stated as limitations in Section 9 of the article)

- [ ] **Associations of changes, IGES/JRC.** Requires series with fewer gaps: within CAGR-imputed stretches, year-on-year changes are constant by construction.
- [ ] **Autocorrelation corrections** (effective sample size, block bootstrap). Feasible now, but at current lengths they remove most significance; meaningful with longer series.
- [ ] **Predictive test.** Whether bridges identified in one period anticipate deterioration downstream in the next; splitting ~26 annual points leaves about 13 per period.
- [ ] **Validation against documented cases** (e.g. agricultural expansion vs deforestation in Brazil). Requires sectoral evidence, not more indicator series.
- [ ] **Mechanisms.** Requires policy, budget and, ideally, subnational data.

## Research agenda

- [ ] **Data-supported links absent from the inventories.** In the IGES/JRC procedure, flag (or retain in a variant) pairs with strong, significant associations that neither inventory records, as candidates for policy-created links; compare with the SDG Index procedure, which keeps such pairs by design.
- [ ] **Transmission between countries.** Design a way to overlay national networks and investigate whether performance in one country is associated with trade-offs in another, for instance through trade. Starting points: SDG Index spillover indicators (in Brazil, scarce water consumption embodied in imports is a transmission bridge) combined with bilateral data such as trade flows.
