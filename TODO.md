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
- [ ] Verify bibliographic details and add DOIs for Pradhan et al. (2017), Kroll, Warchold and Pradhan (2019), Miola et al. (2019), Nilsson et al. (2017), Issa, Mezher and El Fadel (2024), Di Lucia, Slade and Khan (2022).
- [ ] Convert LaTeX equation blocks to Word equations in the `.docx` before submission.
- [ ] **Policy-created interlinkages (argument to add).** Literature-based inventories such as IGES and JRC record links that studies have found or experts expect. Some links, however, are created by policy decisions, not by any mechanism the literature would predict. In Brazil, the National School Feeding Programme (PNAE) requires part of its federal funds to be spent on family farming, which ties family farming to school meals and, through them, to child nutrition. A filter that keeps only links with an apparent logic or a scientific study (e.g. that more family farming reduces child malnutrition) removes this synergy from the network and discards the information a high, significant correlation between the indicators could carry. The same example shows that policy can also reverse undesired bridges, by deliberately creating or redirecting a link. Points for the article: Sections 3.3 and 8 (two sources of evidence) and Section 7 (interrupting transmission); verify the legal basis and current share before citing.

## Later: needs more or other data (stated as limitations in Section 9 of the article)

- [ ] **Associations of changes, IGES/JRC.** Requires series with fewer gaps: within CAGR-imputed stretches, year-on-year changes are constant by construction.
- [ ] **Autocorrelation corrections** (effective sample size, block bootstrap). Feasible now, but at current lengths they remove most significance; meaningful with longer series.
- [ ] **Predictive test.** Whether bridges identified in one period anticipate deterioration downstream in the next; splitting ~26 annual points leaves about 13 per period.
- [ ] **Validation against documented cases** (e.g. agricultural expansion vs deforestation in Brazil). Requires sectoral evidence, not more indicator series.
- [ ] **Mechanisms.** Requires policy, budget and, ideally, subnational data.

## Research agenda

- [ ] **Data-supported links absent from the inventories.** In the IGES/JRC procedure, flag (or retain in a variant) pairs with strong, significant associations that neither inventory records, as candidates for policy-created links; compare with the SDG Index procedure, which keeps such pairs by design.
- [ ] **Policy-intended interlinkages from the PPA 2024–2027 (future study).** The PPA 2024–2027 required those formulating each programme to state which SDG targets it contributes to. Mapping each programme's central target to the targets its formulators indicated yields a list of policy intentions: a network of links that policy *thought* it would create. A classification of every technical programme by SDG (all components, justification, objective and expected result) has already been produced with BERT language models (ods-brasil-bahia). Planned: cross these intended links with the IGES/JRC (literature) and SDG Index (data) networks and with the six roles, for example:
    - intended synergies that appear in the data as trade-offs, or not at all;
    - transmission bridges and exposed targets that no programme claims to address;
    - strong data-supported links absent from the literature that match programme intentions (policy-created links, see the PNAE example above).
  Purpose: inform hypotheses to be considered in drafting the PPA 2028–2031.
- [ ] **Transmission between countries.** Design a way to overlay national networks and investigate whether performance in one country is associated with trade-offs in another, for instance through trade. Starting points: SDG Index spillover indicators (in Brazil, scarce water consumption embodied in imports is a transmission bridge) combined with bilateral data such as trade flows.
