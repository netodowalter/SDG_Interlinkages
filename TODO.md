# TODO

Open items for the SDG Interlinkages package and the methodological article (`docs/SDG_Interlinkages_methodological_article.md`). The framework is experimental and preliminary.

## Methodological validity (priority)

These tests address the objections a reviewer is most likely to raise. None of them depends on longer series.

- [ ] **Null model for roles.** Rewire links at random while keeping each node's performance direction and its numbers of sent and received links; recompute bridge and relay flows and role membership. Report whether observed bridges exceed the null distribution. Answers the circularity objection: after reclassification, synergy ≈ "same direction" and trade-off ≈ "opposite directions", so roles might only reflect trend strength and degree.
- [ ] **Associations of changes, not levels.** Add an option to correlate first differences (or detrended series) instead of levels. Trending series correlate strongly regardless of any relationship (spurious regression); the Brazil SDG Index network already links about half of all possible pairs (3,305 arcs, 81 indicators).
- [ ] **Stability of roles.** Compare membership across trend windows (e.g. 2000–2025 vs the last decade), Pearson vs Spearman, and comparable countries.
- [ ] **Validation against known cases.** Check whether documented trade-offs (e.g. agricultural expansion vs deforestation in Brazil) appear as bridges or dependent contributors.
- [ ] **Predictive test.** Check whether bridges identified in one period anticipate deterioration of downstream targets in the next.

## Sensitivity outputs

- [ ] Benjamini–Hochberg q-values as the active selection criterion (option).
- [ ] Alternative ranking cut-offs (top 5, top 15).
- [ ] Isolation threshold: strict zero forward synergy vs φ < 1.
- [ ] Context applied as a filter (previous rule) vs characterisation (current rule).
- [ ] Alternative rules for uncertain JRC directions (Table 1 of the article).

## Visualisation

- [ ] **Two-step positions for improving nodes.** Currently placed by trade-off received from deterioration × synergy passed forward; an isolated beneficiary (low forward synergy) would therefore be pushed away from the centre although it is an interface role. Option: place improving nodes by trade-off received only, so I-2 and I-3 both sit at the interface.
- [ ] Optional marker for urgency within roles (e.g. bridges with fewer than 15 years to zero).

## Runs and data

- [ ] Run IGES/JRC with real UNSD data (requires internet) and inspect the weighted `_pond` outputs; so far tested only on the synthetic fixture.
- [ ] Rerun the Brazil application with the IGES/JRC procedure for 2010–2023 to compare directly with the NT Dinte 77 categories.

## Article

- [ ] Archive the release used in the article on Zenodo and cite its DOI; give the application a persistent address.
- [ ] Verify bibliographic details and add DOIs for references added from memory: Pradhan et al. (2017), Kroll, Warchold and Pradhan (2019), Miola et al. (2019), Nilsson et al. (2017), Issa, Mezher and El Fadel (2024), Di Lucia, Slade and Khan (2022).
- [ ] Update Sections 6–8 with the null-model and change-based results once available.
- [ ] Convert LaTeX equation blocks to Word equations in the `.docx` before submission.
