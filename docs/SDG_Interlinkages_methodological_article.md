# Beyond Co-movement: Performance Direction and Transmission Roles in SDG Interlinkage Networks

Walter Antonio Desiderá Neto · Draft, November 2026

## Abstract

Synergies and trade-offs among Sustainable Development Goal (SDG) targets are often inferred from the sign of associations between normatively oriented indicators. This article argues that such networks also require the direction of observed performance for their interpretation. Two indicators that deteriorate together may be positively associated, but their co-movement does not represent a contribution to the 2030 Agenda. In trending series, association signs tend to separate improving from deteriorating targets; they do not identify which group is improving. The argument builds on an application to Brazil’s 2024 Voluntary National Review (VNR), which used the IGES tool and the JRC compilation and identified performance direction as a missing element in the interpretation of interlinkages (Desiderá Neto et al., 2025).

We propose a framework that incorporates performance direction into link classification, network metrics and role selection. In the resulting network, synergies connect targets moving in the same direction, while trade-offs cross between improving and deteriorating subsystems. Its potential contribution lies at this interface: transmission bridges are deteriorating targets that receive trade-offs from improving targets and pass deterioration on through synergies; isolated beneficiaries are improving targets associated with losses elsewhere that pass forward less synergy than they receive. These positions raise questions that centrality measures and target-by-target monitoring alone cannot answer.

Two procedures implement the framework: one combines IGES/JRC inventories with United Nations indicators, and the other uses SDG Index component scores. Tests for Brazil, Finland and Norway yield similar results. Independent surrogate series frequently pass nominal significance tests in levels. Bridge rankings track trend linearity and degree, and the three highest-ranked bridges in levels share no members with the three highest-ranked bridges in annual changes in any country. These results limit what can be inferred from the published national series. The analysis supports incorporating performance direction into the interpretation of links, but the estimated roles do not provide a reliable basis for prioritising targets in Voluntary National Reviews. Investigating those roles requires indicators with greater granularity and meaningful variation.

**Keywords:** Sustainable Development Goals; synergies; trade-offs; policy coherence; network analysis; transmission; monitoring and evaluation.

## 1 Introduction

The indivisibility of the 2030 Agenda presents a challenge for monitoring and public action. Progress is assessed target by target, yet the processes behind outcomes cross sectoral boundaries. An intervention may advance several objectives, encounter constraints originating elsewhere, or improve one outcome at the expense of another. Network analysis has become a common way to represent these interdependencies (Issa, Mezher and El Fadel, 2024; Chaniotakis et al., 2024).

Its relevance depends on what its links mean. Synergies matter because mutually reinforcing improvements multiply the benefits of public action; trade-offs matter because gains in one domain may involve losses in another. Most quantitative applications operationalise these concepts through the sign of correlations between indicators oriented so that higher values are better (Pradhan et al., 2017; Zhou and Moinuddin, 2017). Orientation makes scales normatively comparable. It does not establish whether the observed trajectories are improving or deteriorating.

This gap has two consequences, which structure the article.

1.  Without performance direction, links and rankings can be misinterpreted. A positive association between two deteriorating targets may be labelled a synergy, and a target associated with deterioration elsewhere may consequently be ranked as a leading contributor. Such rankings do not necessarily answer the policy question for which they are used.

2.  With performance direction, network analysis could make a distinct contribution. Classified edges separate an improving subsystem from a deteriorating one and identify the trade-off arcs that connect them. Two positions at this interface warrant particular attention: transmission bridges, which receive adverse associations from improving targets and pass deterioration on within the regressing subsystem; and isolated beneficiaries, whose improvement is associated with deterioration elsewhere and is passed on only to a limited extent.

This study builds on an application to Brazil’s 2024 VNR, documented in Ipea’s Technical Note Dinte 77 (Desiderá Neto et al., 2025). The note applied the IGES and JRC approaches and proposed two network metrics based on weighted degree. Examination of target progress identified a limitation of interpreting links without the direction of performance. This article develops that insight into an operational framework, specifies its potential diagnostic value and tests whether available national indicator series can support its estimation. Tests for Brazil, Finland and Norway indicate that the series examined cannot support that use.

The article is organised as follows. Section 2 reviews the Brazilian VNR case study and articulates its core methodological finding. Section 3 situates the framework within the broader literature and examines the empirical basis of literature-derived networks. Section 4 presents the analytical design and data-processing procedures. Section 5 defines the network metrics, two-step flows and target roles. Section 6 examines the policy relevance of the interface roles. Section 7 presents statistical diagnostic tests of the underlying indicator series. Section 8 outlines additional applications of the open-source pipeline, Section 9 addresses analytical limitations, and Section 10 concludes with policy recommendations.

## 2 Starting point: the Brazilian VNR exercise and its finding

### 2.1 The original application

Brazil's 2024 VNR replicated the IGES SDG Interlinkages Analysis and Visualisation Tool (Zhou and Moinuddin, 2017). The IGES relationships and their directions were kept unchanged. Indicator availability limited the network to 73 targets observed annually over 2010–2023, with gaps imputed by compound annual growth rates. Every assumed link was weighted and classified by its Pearson coefficient, regardless of strength, significance or the distribution of the series (Desiderá Neto et al., 2025).

The complete network was excessively dense, requiring filtering into separate synergy and trade-off subnetworks. The synergy subnetwork revealed two distinct clusters, with targets 10.1, 9.4, and 8.5 ostensibly bridging the transmission of positive effects between them. Standard interpretations suggested two agendas progressing well, joined by a few structural connectors, alongside a dense tangle of trade-offs that proved difficult to interpret. However, the trade-off subnetwork qualified this reading: the same targets, particularly 9.4, were also major receivers and senders of trade-offs. A role suggested by one subnetwork was contradicted by the other. Section 4.4 explains how these clusters arise.

That observation motivated two metrics built from weighted in- and out-degree in each subnetwork:

$$
\mathrm{SL.Out}_i = \mathrm{CGP.Out.S}_i - \mathrm{CGP.Out.T}_i
$$

$$
\mathrm{TL.In}_i = \mathrm{CGP.In.T}_i - \mathrm{CGP.In.S}_i
$$

Targets with positive SL.Out were classified as *transversal collaboration* ("helping without hindering"); targets with positive TL.In were classified as *transversal neglect* ("hindered without being helped"). A weighting factor based on each node's share of links was introduced to control for target centrality driven by uneven research coverage rather than genuine interdependence.

### 2.2 What the examination of progress revealed

When target-level progress data became available, the note examined what the categories could and could not show. The note reasoned through a hypothetical network in which 90% of targets were strongly synergistic with one another while one target held trade-offs with all of them. If the synergistic targets were regressing together while the isolated target advanced rapidly, the "transversal collaborators" would be dragging the system backwards. Their synergy would operate in the direction opposite to the one desired.

The reverse also held. A target with high TL.In but improving performance could not be described as neglected. It was more plausibly pursued through individualised strategies, indifferent to the rest of the plan, such that deterioration elsewhere contributed to its own progress. The note read this as a possible sign of concentrated misallocation of scarce resources (Desiderá Neto et al., 2025).

The note drew two conclusions. First, positive performance is not an intrinsic attribute of synergy: when links are classified by association sign alone, network positions cannot automatically be interpreted as contribution or neglect. Second, performance has three distinct dimensions: stage (distance to target), direction (approaching or moving away) and pace (rate of change). The note’s literature search found studies considering stage as a condition for transmitting synergies, but none examining how performance direction changes the meaning of synergy and trade-off. The issue had also been raised in conceptual typologies by Zhou and Moinuddin (2021) and Su, Krol and Hogeboom (2022), outside the IGES tool documentation (Section 3.2).

### 2.3 From diagnosis to framework

This was the note's central contribution. The IGES tool and the JRC compilation were the interlinkage approaches suggested to countries preparing VNRs, and neither incorporates the direction of target performance into the classification of interlinkages. By applying them in full, reporting openly what their metrics could and could not support, and identifying performance as the missing element, the note took the first step towards the framework presented here. The present framework carries that step through every stage of the analysis. The changes are summarised below; Sections 4 and 5 justify each one.

| **Element**         | **NT Dinte 77 (2025)**                              | **Present framework**                                                                                                                |
|---------------------|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Link evidence       | IGES links, all retained regardless of significance | IGES/JRC evidence rules with p ≤ 0.10, or SDG Index associations with p \< 0.10 and temporal orientation                             |
| Series preparation  | One indicator per target, CAGR imputation           | Coverage-based series selection, bounded CAGR imputation, consolidation of shared series                                             |
| Link classification | Sign of the oriented correlation                    | Sign of the oriented correlation, then checked against both nodes' trajectories; weak discordant links excluded, others reclassified |
| Contribution metric | SL.Out = out-synergy − out-trade-off                | Colab, same formula, read only among improving nodes                                                                                 |
| Exposure metric     | TL.In = in-trade-off − in-synergy                   | Neglect = in-trade-off **+** in-synergy from deteriorating sources, read only among deteriorating nodes                              |
| Interface measures  | None                                                | Trade-off received and sent across the interface, synergy passed on, bridge and relay flows, forward ratio φ                         |
| Roles               | Two categories                                      | Six roles defined by performance direction, including the two interface roles                                                        |
| Context             | None                                                | Semantic ambitiousness (IGES/JRC) or conditional time to boundary (SDG Index), reported for every role                               |
| Coverage bias       | Link-share weighting factor                         | Same factor, IGES/JRC only, produced as a parallel weighted version with a rank comparison (Section 5.6)                             |

The change in the exposure metric is the clearest consequence of incorporating performance. TL.In *subtracted* incoming synergies on the assumption that any synergy is help. Neglect *adds* incoming synergies from deteriorating sources, because reinforcement from a deteriorating neighbour is a source of pressure, not support.

The link-share weighting factor is retained for the IGES/JRC procedure, where links come from literature inventories and coverage bias can arise. It is applied as a parallel version rather than a correction, so that positions that change markedly can be flagged (Section 5.6).

## 3 Position in the literature and evidential foundations

### 3.1 How synergies and trade-offs are usually operationalised

Reviews group methods for inferring SDG interlinkages into qualitative, literature-review and quantitative traditions (Chaniotakis et al., 2024). Qualitative scoring, such as the seven-point scale of Nilsson et al. (2017), captures context but lacks explicit criteria for each score. Literature compilations, such as the JRC inventory (Miola et al., 2019; Fronza et al., 2023), accumulate findings across studies but describe relationships that may not hold uniformly across settings. Quantitative studies correlate indicator series: Pradhan et al. (2017) define synergies and trade-offs from the sign of correlations between oriented indicators, and Kroll, Warchold and Pradhan (2019) examine how these classifications shift over time.

These approaches commonly treat a positive association between oriented indicators as mutual support. Yet a positive coefficient can also describe co-movement between deteriorating indicators. A change in the sign of an association over time is distinct from a change in whether the outcomes themselves are improving or deteriorating.

### 3.2 Recognition of the problem and additive approaches

This premise has been questioned. In a review of the effects of COVID-19 on the SDGs in Asia, the authors of the IGES tool distinguished four configurations according to whether a causal and an affected target are progressing or regressing: synergy, trade-off, “development drag” and “coupled deterioration” (Zhou and Moinuddin, 2021). Su, Krol and Hogeboom (2022) noted that indicators deteriorating together can be positively correlated and therefore labelled a synergy. In applying the IGES tool to Brazil, NT Dinte 77 identified the operational consequence of this ambiguity for interpreting collaboration and neglect (Desiderá Neto et al., 2025). The subsequent review by Sota and Venghaus (2026) reinforces the note’s diagnosis and documents the problem across quantitative studies.

Other studies combine performance and network measures as separate criteria. Issa and El Fadel (2026) combine urgency and influence scores, while Ah-Pine and Nasho Ah-Pine (2026) select indicators that are both underperforming and central. Yuan et al. (2026, Eq. 19 and Figs. 8–9) compare 11 goals across 19 Chinese urban agglomerations using six observation years between 2012 and 2022. They correlate goal rankings across agglomerations using scores averaged over the six years and repeat the spatial comparison for each year. They find 31 positive and 24 negative coefficients among 55 pairs in the averaged data, and an increase from 15 pairs classified as synergistic in 2012 to 17 in 2022. These results identify geographic covariation and changes in its pattern. A positive spatial coefficient can arise when places ranking high on one goal also rank high on another, even if both goals deteriorate over time in a given place. Their separate assessment of progress therefore answers a different question from whether a particular edge connects two improving targets.

Attention to indirect effects is also growing. Xiao, Liu and Ren (2023) extend direct synergies and trade-offs to indirect ones transmitted through intermediate targets, finding that synergies account for most of the total influence once indirect paths are counted. Without performance, however, a chain of synergies may be propagating deterioration. Causal orientation does not change this: Ding et al. (2026) orient links among goals with convergent cross mapping but classify them by the sign of correlation, reading a positive sign as joint improvement, and find that 82% of the relations are synergies. Reviews also point to directionality, causal mechanisms and transboundary effects as understudied (Khot, Warchold and Pradhan, 2026). Their "temporal dynamics" concerns whether an interaction changes over time (Kroll, Warchold and Pradhan, 2019), which differs from whether the linked targets are improving or deteriorating.

In their subsequent review, Sota and Venghaus (2026, Table 1 and the section on correlation analysis) distinguish four configurations of source and recipient performance, drawing on Zhou and Moinuddin (2021). Their review explains why reorienting an indicator cannot distinguish joint improvement from coupled deterioration, why a strength threshold leaves that ambiguity unresolved, and how duplicate indicators and interpolation complicate comparisons. They recommend tracing mechanisms and comparing methods on the same data. Building on the diagnosis in NT Dinte 77, this article carries the distinction through edge classification, weighted measures and two-step roles and tests whether the available series can support those roles.

Khot, Warchold and Pradhan (2026, Sections 4–5) find in a review of 272 articles that goal-level studies predominate, while interactions within goals, across borders and in low-income countries receive less attention. This bears directly on literature-derived networks: a high degree can partly reflect which targets and settings researchers have studied. The review maps methods and their co-occurrence and explicitly leaves their comparative effectiveness and robustness untested. It supplies a reason to examine coverage and mechanisms, while the empirical validity of the resulting network remains an open question.

### 3.3 The limits of centrality

Network applications typically rank targets by degree, betweenness, eigenvector or closeness centrality (Issa, Mezher and El Fadel, 2024). Weighted in- and out-degree are the most common because they are simple and separate sending from receiving. Issa, Mezher and El Fadel recommend composite indices to balance the distortions of single measures. Composite indices still treat all synergy weight as favourable. A target can be central because it accompanies widespread improvement, because its deterioration accompanies deterioration elsewhere, or because it sits where gains and losses meet. These positions call for different responses, and no combination of centralities distinguishes them without performance direction.

Decision-makers also value simplicity and direct applicability over methodological sophistication (Di Lucia, Slade and Khan, 2022). A framework that translates network positions into a small number of interpretable roles, each tied to a specific question, addresses that demand without hiding the underlying evidence.

### 3.4 Evidential basis of literature-derived networks

The IGES tool combines relationships drawn from a union of reference sources with country-specific indicator correlations (Zhou and Moinuddin, 2017). The JRC compilation records interaction types, directions, methods and contexts, including cases where direction cannot be established (Fronza et al., 2023). The literature supplies the existence and orientation of candidate relationships; local correlations supply their strength and sign. Correlations do not independently establish direction. Uneven research coverage may also make well-studied targets appear more connected (Desiderá Neto et al., 2025); the IGES/JRC procedure therefore also produces a link-share weighted version (Section 5.6). Inventories also omit links created by policy rather than by mechanisms studied in the literature (Section 8).

Comparing the two inventories shows how sensitive the network is to construction choices. The consolidated comparison contains 8,751 IGES records and 5,701 JRC records, with 3,133 matches: 35.80% of the former and 54.96% of the latter.

**Table 1.** Directional agreement among matched IGES and JRC records

| **Directional evidence**             | **Records** | **Share of matched records** | **Treatment in the network**                                                                  |
|--------------------------------------|-------------|------------------------------|-----------------------------------------------------------------------------------------------|
| Uncertain in the JRC evidence        | 1,286       | 41.05%                       | Both directions retained, unless IGES codes clear one-sided evidence in the reverse direction |
| Complete agreement                   | 1,171       | 37.38%                       | Retained as coded                                                                             |
| Partial agreement                    | 597         | 19.06%                       | Both directions retained                                                                      |
| Opposite unidirectional orientations | 79          | 2.52%                        | Both directions retained; conflicting evidence recorded                                       |
| Total                                | 3,133       | 100.00%                      |                                                                                               |

*Note:* Complete agreement denotes the same single direction or bidirectionality in both inventories; partial agreement denotes a single direction in one and bidirectionality in the other. Percentages are rounded independently. Counts refer to relationship records, not unique unordered target pairs. The consolidated comparison permits verification of totals but does not independently reproduce the matching of the underlying inventories. Source: Zhou and Moinuddin (2017); Fronza et al. (2023).

These differences are not an error rate. An unmatched relationship may reflect scope, coverage or coding, and the JRC compilation is not an exhaustive standard. What the comparison does establish is that a credible framework must state how each category of directional evidence becomes an arc. The last column of Table 1 makes this explicit, so that alternative rules can be tested in replication.

Each direction of a pair is evaluated separately. Clear JRC evidence for a direction (single-sided or double-sided) always retains it. A direction is rejected when the pair is absent from both inventories; when it appears in only one inventory and that inventory codes the reverse direction as one-sided; or when IGES codes the reverse direction as one-sided clear and JRC codes the reverse direction as single-sided or the pair as unclear. All other directions are retained, and every arc records the evidence from both sources. In practice, unresolved disagreement is represented by two arcs rather than settled by choosing one source.

## 4 Analytical design

### 4.1 Two procedures for building the network

**IGES/JRC procedure.** Candidate target relationships come from the IGES inventory, assessed against JRC evidence on direction (Table 1). Observations are collected from the UNSD SDG database by geographic code (M49), for a country or region. For each target, the series with the greatest number of distinct original numeric years during 2000–2025 is selected, with ties broken by IGES order. Eligible gaps are filled by series-specific compound annual growth rates computed from positive endpoint pairs, with bounds applied to generated values. Series shared by several targets enter the calculations through one representative target, so identical observations are not counted as independent evidence of interdependence. Eligible pairs receive Pearson coefficients and are retained at p ≤ 0.10.

**SDG Index procedure.** The SDG Index (Sachs et al., 2026) is distinct from the official UN framework. It combines indicators from several sources on a normalised 0–100 scale, where 100 is an operational benchmark rather than full attainment of a UN target. The procedure uses annual component scores rather than goal or overall scores, for 169 countries and 14 regions or aggregates. An editorial mapping links 101 components to SDG targets. Pairs within the same goal or target are excluded before testing. Retained pairs need at least eight matched observations, a nonzero coefficient (Pearson, Spearman or both) and nominal p \< 0.10. Benjamini–Hochberg q-values are kept for sensitivity analysis.

In the SDG Index procedure, orientation is exploratory. A direction is supported when both a lagged association and a conditional association, controlling for the recipient's previous value, reach p \< 0.10. A single arc is kept when only one direction is supported. Two arcs are kept when both directions are supported or neither can be distinguished, and the two situations are recorded separately.

### 4.2 Performance direction

Improvement means movement towards the desired outcome; deterioration means movement away from it. Neither term says whether a target has been achieved or is on track for 2030. Following the three dimensions identified in Section 2.2, the framework uses **direction** to classify links, and uses **stage** and **pace** as context reported for every role (Section 5.4). This separation is consistent with the UN progress assessment, which evaluates change against target requirements (United Nations, 2026a, 2026b), but the framework does not reproduce its categories.

For each series, a linear trend is fitted over the analytical period and its slope multiplied by the desired direction *d*: +1 when an increase is favourable, −1 when a decrease is favourable. SDG Index scores already ascend normatively, so *d* = +1.

$$
x_i(t) = \alpha_i + \beta_i t + \varepsilon_i(t), \qquad \beta_i^{*} = d_i \beta_i, \qquad d_i \in \{-1, +1\}
$$

Positive and negative adjusted slopes indicate improvement and deterioration. A numerically negligible fitted change is classified as stable, and fewer than three distinct years as undetermined. The trend R² measures how closely observations follow the fitted trajectory; it says nothing about the causal validity of any relationship.

### 4.3 Classifying links with performance

Initial link types come from the sign of the oriented association. Each retained link is then checked against the trajectories of its two nodes. A link is *discordant* when its initial type conflicts with those trajectories: for example, a positive oriented association between an improving and a deteriorating node.

Let *m* be the smaller of the two trend R² values and \|r\| the absolute association. A discordant link is excluded if *m* \< 0.10, or if *m* \< 0.20 and \|r\| \< 0.40. Weak trends cannot carry a reclassification, and weak associations cannot withstand one. Other discordant links between nodes with defined directions are reclassified to match the trajectories. The original coefficient and initial type are preserved in an *Adverse cases* record; link weights use \|r\|. Links involving stable or undetermined nodes keep their initial type.

**Table 2.** Retained links by the trajectories of their nodes

| **Source**    | **Recipient** | **Type**  | **Interpretation (hypothesis)**                                                         |
|---------------|---------------|-----------|-----------------------------------------------------------------------------------------|
| Improving     | Improving     | Synergy   | Reinforcement of improvement                                                            |
| Deteriorating | Deteriorating | Synergy   | Reinforcement of deterioration                                                          |
| Improving     | Deteriorating | Trade-off | The source's gains are associated with the recipient's losses                           |
| Deteriorating | Improving     | Trade-off | The recipient's gains are associated with, and may be sustained by, the source's losses |

*Note:* Interpretations are hypotheses about relationships, not estimated causal effects. Arcs keep their literature-based or temporal evidential status. The four rows correspond to the configurations of Zhou and Moinuddin (2021): synergy, coupled deterioration, trade-off and development drag.

The last two rows describe opposite situations. In the third, the improving node is the source and the cost falls downstream. In the fourth, the improving node is the recipient, and its improvement may depend on deterioration upstream. This is the configuration NT Dinte 77 identified as possible concentrated misallocation. Keeping the two rows distinct is what allows the interface roles of Section 5.

### 4.4 What the network adds beyond co-movement

Reclassification makes one property hold by construction. Among nodes with defined directions, synergies connect nodes moving in the same direction and trade-offs connect nodes moving in opposite directions. The classified network therefore splits into two synergy subsystems, one improving and one deteriorating, joined only by trade-off arcs (Figure 1, Section 5).

In practice, the sign of the oriented association already produces most of this split. In Brazil's SDG Index network, 98.5% of the links that the sign alone classifies as synergies connect indicators moving in the same direction, and 99.1% of the trade-offs connect indicators moving in opposite directions; the 42 discordant links, out of 3,347, all fail the trend-fit criteria and are excluded. This is to be expected when trending series are correlated in levels. It also explains a recurrent feature of synergy networks built with the IGES approach, including the two clusters observed in the Brazilian VNR exercise (Section 2.1): synergy subnetworks tend to split into an improving and a deteriorating cluster.

The IGES classification thus already separates the two groups, and the clusters themselves were an early sign that performance was at work in the network. What the classification does not do is say which cluster is which, so reinforcement of deterioration is read as collaboration. The contribution of performance direction therefore lies less in reclassifying links than in giving them their meaning and in locating the interface between the two clusters.

This changes the interpretation of the clusters and their connections. In a sign-based synergy network, targets linked to both clusters may appear to bridge two agendas that are progressing. Force-directed layouts can reinforce this impression. Once performance is considered and discordant links are treated under the rules above, synergies remain within each defined performance group and trade-offs connect them. Apparent synergy bridges across groups therefore depend on discordant links or nodes without a defined direction. The interface becomes a place to investigate possible adverse transmission, rather than a connection to strengthen automatically.

Whether produced by the data or completed by reclassification, this split is not a finding in itself. A concentration of synergies within groups of the same direction cannot be offered as evidence that those groups are causal systems. The information the network adds over a simple list of improving and deteriorating targets lies elsewhere:

- **which** pairs are linked at all, as established by literature evidence or statistical filters;

- **the orientation** of each link, from literature or temporal tests;

- **the strength** of each link;

- **the structure of the interface**: which nodes receive the trade-off arcs that cross between subsystems, and what they do with them.

The last item is where network analysis could add to target-by-target monitoring. A list of deteriorating targets cannot show which targets may absorb the costs of gains elsewhere and pass them on. A list of improving targets cannot show which gains may be associated with losses elsewhere while little synergy is passed forward. These interpretations require independent investigation of the underlying relationships.

## 5 Metrics and network roles

### 5.1 Contribution and exposure

With links classified by performance, each metric is read only within the performance group where its meaning is unambiguous. Let *w(i,j)* be the weight of the arc from *i* to *j*, and let *I* and *D* denote the improving and deteriorating subsystems.

**Collaboration** keeps the form of the SL.Out metric of NT Dinte 77 but is read only among improving nodes, where outgoing synergies reach other improving nodes and outgoing trade-offs reach deteriorating ones:

$$
\mathrm{Colab}(i) = \sum_{j:\,\text{synergy}} w(i,j) - \sum_{j:\,\text{trade-off}} w(i,j), \qquad i \in I
$$

**Neglect** replaces TL.In and is read only among deteriorating nodes. Incoming trade-offs come from improving sources; incoming synergies from deteriorating sources are added, not subtracted:

$$
\mathrm{Neglect}(k) = \sum_{i:\,\text{trade-off}} w(i,k) + \sum_{j \in D:\,\text{synergy}} w(j,k), \qquad k \in D
$$

Neither name implies intent. "Neglect" denotes a concentration of adverse incoming relationships, not deliberate institutional neglect or insufficient spending. Neither metric estimates the marginal return to an intervention.

### 5.2 Interface measures

Aggregate scores hide where adverse pressure comes from. Neglect mixes pressure from the improving subsystem (trade-offs) with pressure from within the deteriorating one (synergies). The framework therefore separates the components that describe traffic across the interface:

| **Measure** | **Defined for** | **Meaning**                                                                                |
|-------------|-----------------|--------------------------------------------------------------------------------------------|
| T⁺(k)       | k ∈ D           | Incoming trade-off weight from improving sources: the cost of others' gains arriving at k  |
| S⁻(k)       | k ∈ D           | Incoming synergy weight from deteriorating sources                                         |
| B(k)        | k ∈ D           | Outgoing synergy weight to deteriorating nodes: what k passes on                           |
| R(i)        | i ∈ I           | Incoming trade-off weight from deteriorating sources: gains associated with others' losses |
| Sₒ(i)       | i ∈ I           | Outgoing synergy weight to improving nodes: what i passes forward                          |
| C(i)        | i ∈ I           | Outgoing trade-off weight to deteriorating nodes: the cost of i's gains downstream         |

Only links between nodes with defined directions enter these measures; links from stable or undetermined nodes do not.

Two-step flows follow directly. The total weight of all paths that enter a deteriorating node *k* as a trade-off from an improving node and leave as a synergy to a deteriorating node is the product of the two sums:

$$
\mathrm{Bridge}(k) = \sum_{i \in I} \sum_{j \in D} w(i,k)\,w(k,j) = T^{+}(k) \times B(k)
$$

The analogous flow within the deteriorating subsystem, Relay(k) = S⁻(k) × B(k), describes deterioration received from and passed to other deteriorating nodes. For improving nodes, the forward ratio φ(i) = Sₒ(i) / R(i) indicates how much of what a node gains from others' losses is matched by synergies it passes on. A value of zero means nothing is passed forward; the framework treats φ \< 1, passing forward less than is received, as isolation.

### 5.3 Six roles

Each role is selected by its own score within the relevant performance group and lists only the three highest-ranked nodes with positive values. Roles are selected independently, so a node can hold more than one: a target can be both a contributor and a dependent contributor, or both a transmission bridge and a deterioration relay. The order within each list indicates relative priority for investigation, with the first-ranked case taking precedence over the third. A cut-off of three produces a concise list of priorities. Lower-ranked cases are not brought in to fill a role.

| **Role**                      | **Group**     | **Selection**                           | **Question it raises**                                                                |
|-------------------------------|---------------|-----------------------------------------|---------------------------------------------------------------------------------------|
| **I-1 Contributor**           | Improving     | Three highest Colab, not top C          | How can these beneficial interactions be sustained or extended?                       |
| **I-2 Dependent contributor** | Improving     | Three highest R among nodes with φ ≥ 1  | Do the gains that this node spreads depend on losses elsewhere?                       |
| **I-3 Isolated beneficiary**  | Improving     | Three highest R among nodes with φ \< 1 | Is this improvement sustained by deterioration elsewhere and kept rather than shared? |
| **D-1 Exposed target**        | Deteriorating | Three highest Neglect, not top B        | Where does the pressure come from, and can it be contained?                           |
| **D-2 Transmission bridge**   | Deteriorating | Three highest Bridge(k)                 | Does the cost of others' gains enter the deteriorating subsystem here and spread?     |
| **D-3 Deterioration relay**   | Deteriorating | Three highest Relay(k)                  | Is deterioration reproduced here and passed on?                                       |

A node that holds two roles answers two questions at once. A contributor that is also a dependent contributor spreads gains that rest in part on losses elsewhere; a bridge that is also a relay is where the cost of others' gains enters the deteriorating subsystem and where deterioration is reproduced. I-2 and I-3 cannot coincide, since they split receivers by φ. Two exclusions remain, because they concern rankings that are not roles. Contributors exclude the top senders of costs (C): a target whose gains are associated with losses downstream is the origin of what bridges propagate, and should not be labelled a contributor without qualification. Exposed targets exclude the top senders of deterioration (B), which pass pressure on rather than only receive it. The roles are not a ranking of the intrinsic worth of targets, and not every relevant target falls into one. They separate questions that a single centrality measure would conflate, while the full network stays available for scrutiny.

### 5.4 Context: characterising roles

Direction alone does not capture what a target demands. Context therefore characterises every role, using a measure suited to each procedure; it does not determine membership.

In the IGES/JRC procedure, the context is **semantic ambitiousness**: the strength of the commitment expressed in a target's wording (Mustajoki et al., 2022). A commitment to eradicate a deprivation is more demanding than one to reduce it, whatever the setting. Within a role, high ambitiousness marks improvement on a demanding commitment, and low ambitiousness marks deterioration despite a modest one. Semantic ambitiousness differs from relative ambitiousness (distance to target) and absolute ambitiousness (effort required), and the target-level coding is distinct from the goal-level aggregates reported by Mustajoki et al.

In the SDG Index procedure, the common scale allows a measure of **stage and pace** together. Using the latest score *S* and the fitted slope:

$$
T_{100} = \frac{\max(0,\,100 - S)}{\beta}, \;\; \beta > 0
$$

$$
T_{0} = \frac{\max(0,\,S)}{|\beta|}, \;\; \beta < 0
$$

Every selected node is reported with its T₁₀₀ or T₀. These times rank urgency within each role: a transmission bridge close to the lower boundary is more urgent than one deteriorating slowly. These are conditional extrapolations at the fitted pace, not forecasts. A long T₀ means slow deterioration relative to the remaining score, not demonstrated resilience to shocks.

### 5.5 The interface roles as the main contribution

Two roles carry the contribution that only a network can make, and they mirror each other across the interface (Figure 1).

![Figure 1 · interface roles between the improving and deteriorating subsystems, illustrated with Brazil](figures/figure1_interface_roles.png)

**Figure 1.** After classification, synergies remain within each defined performance group and trade-offs cross between them. A transmission bridge receives a trade-off and passes on synergy; an isolated beneficiary passes forward less synergy than the trade-off weight it receives. Illustration with Brazil's SDG Index network (normalised scores, 2000–2025, Pearson correlation in levels, p < 0.10). Panel A: 2.2 obesity, the second-ranked transmission bridge, receives trade-offs from gains in drinking water, sanitation and internet use and passes deterioration on to labour rights, administrative proceedings and perceived corruption. Panel B: 8.5 unemployment, the first-ranked isolated beneficiary, receives trade-offs from emissions and pollution embodied in imports and passes forward less than half of that weight (φ = 0.42). Only the strongest arcs of each kind are shown. The links are those the procedure estimates; Section 7 shows that such links cannot be taken as evidence of transmission.

A **transmission bridge** (D-2) is a deteriorating target that receives trade-offs from improving targets and passes deterioration on through synergies. It is where the cost of gains elsewhere enters the deteriorating subsystem and spreads. Selecting it by Bridge(k), rather than by total Neglect, matters: a node can receive little pressure overall yet be the main point of entry and propagation. Conversely, a node with high Neglect may receive and pass on deterioration entirely within the deteriorating subsystem, which makes it a relay, not a bridge.

An **isolated beneficiary** (I-3) is an improving target that receives trade-offs from deteriorating targets and passes forward less synergy than it receives (φ \< 1). Its improvement is associated with losses elsewhere and largely stays where it is. This is the configuration that NT Dinte 77 interpreted as individualised strategies and possible concentrated misallocation. It differs from a dependent contributor (I-2), which also gains from others' losses but passes forward at least as much as it receives (φ ≥ 1). Isolation is defined by the balance at the node rather than by rank, because in dense networks almost every receiver also sends substantial synergy.

The two roles define the most specific policy questions in the framework. At a bridge, the question is whether interrupting the transmission would prevent wider deterioration without sacrificing the upstream gains. At an isolated beneficiary, the question is whether the gains could be maintained with fewer losses elsewhere, or redistributed so that they reach other targets.

The repository computes all six roles and exports every interface measure, rank and context value, so membership can be audited and alternative cut-offs tested. Its Two-step interface view places improving nodes on one side and deteriorating nodes on the other, and moves towards the centre those with the largest two-step flows across the interface, so the interface roles can be read at a glance. Each role has its own border colour; a node with more than one role is drawn with nested borders, one per role, in the order of the table above. Force-directed layouts, by contrast, pull the two subsystems together whenever a target has strong links on both sides.

### 5.6 Link-share weighted version (IGES/JRC)

In literature-derived networks, a target can rank highly because many studies record its links rather than because those links are strong. NT Dinte 77 proposed a factor to flag this: each target's share of the links it sends or receives.

$$
P_i = \frac{L_i}{\sum_{j=1}^{n} L_j}
$$

The IGES/JRC procedure always produces a weighted version alongside the original, with its own workbook and figures. Sent measures (Colab, synergy and trade-off sent) are divided by the sent share, received measures (Neglect, trade-off and synergy received) by the received share, and bridge and relay flows by both; φ is unchanged. Roles, node sizes and Two-step positions are recomputed from the weighted measures. Shares are expressed relative to the mean (Pᵢ × n), so a target with the mean number of links keeps its value; this rescaling does not change any ranking.

The weighted version is a check, not a substitute. A comparison sheet reports original and weighted ranks for Colab and Neglect and flags the discrepancy the NT considered most serious: a target among the top contributors that enters the top of weighted Neglect. Roles that hold in both versions are stronger candidates for investigation. The SDG Index procedure has no weighted version: its links are estimated from data for every eligible pair, so literature coverage does not determine them.

## 6 Why the roles would matter: the policy rationale

If interface roles could be estimated validly, they would change the unit of attention. A target would matter not only because its performance is poor or its connections numerous, but because of the role its connections suggest. An improving target would deserve scrutiny if its gains coexisted with losses elsewhere; a deteriorating target would deserve attention beyond its own sector if it sat where deterioration enters or spreads. This would reverse the usual policy reading of network bridges. In a sign-based synergy network, a bridge between clusters is a point to strengthen. In a performance-based network, what links the improving and deteriorating subsystems are trade-offs, and the aim would be to interrupt the transmission while preserving the gains. Policy can create or redirect such links deliberately: a programme rule can tie family farming to school meals, as in Brazil, and a link that sustains an undesired bridge could in principle be redirected in the same way.

**At a transmission bridge**, an investigation would have to establish whether the incoming trade-off and the outgoing synergy belong to the same mechanism. Temporal ordering, sectoral evidence, institutional arrangements and alternative explanations would be examined together. A two-step path is not a transmission chain: its links may reflect distinct mechanisms, common trends or separate responses to external conditions. If a mechanism were supported, adjustment would aim to buffer the bridge, for instance by mitigating the displaced cost, so that upstream gains no longer spread losses downstream.

**At an isolated beneficiary**, the central question would be what sustains the improvement. Evidence might reveal dependence on resource concentration, displaced costs or another adverse process, or an association generated by a shared contextual change with no direct dependence. These possibilities call for different responses. Where dependence were supported, the aim would be to keep the gains with fewer losses elsewhere, or to connect the target to others so that its gains are shared.

**At a dependent contributor**, the trade-off would be sharper, because the node's gains also benefit other improving targets. Policy would have to weigh the losses upstream against the improvements the node spreads downstream.

No policy intervention should follow mechanically from network centrality. A diagnostic workflow would use network positions to identify candidates for investigation, examine possible mechanisms with domain-specific evidence, design policy responses and evaluate their effects. Its usefulness depends on whether the estimated links provide a credible basis for investigation. Section 7 tests this prerequisite using currently available SDG data.

## 7 Statistical tests

We examine whether correlations between published national indicator series can support the links needed to estimate the roles defined in Section 5. The same diagnostics are applied to four data specifications in Brazil, Finland and Norway.

### 7.1 Data and designs

Finland and Norway were chosen because their national statistical systems are among the best rated by the World Bank's Statistical Performance Index (Dang et al., 2023), which the SDG Index reports under target 17.18. Norway has the highest score in the value used by the 2026 edition (94.1 in 2024, first of 187 countries). Finland was among the five highest every year from 2016 to 2023, first in 2020, and over 2016–2024 shares with Sweden the highest mean score. Brazil ranks 54th in 2024. The comparison tests whether the Brazilian pattern also occurs in countries with highly rated statistical systems. The national index measures statistical capacity broadly and does not certify the quality of any particular series. Four specifications were examined in each country:

- **SDG Index, normalised scores.** The 101 indicator scores supplied by the Sustainable Development Report for each country, 2000–2025, as used by the SDG Index procedure (Section 4.1).
- **SDG Index, raw values.** The raw indicator values of the SDR 2026 database. Only indicators with at most six missing years in 2000–2025, and no run of more than three, were kept: 50 of the 101 for Brazil, 52 for Finland and 51 for Norway. Gaps were filled with the IGES/JRC compound-growth rule, and the normative sign of each indicator was taken from the SDR codebook.
- **UN series.** One aggregate series per target from the UN SDG Global Database, 2010–2023, under the same completeness rule, keeping only observations reported by the country (excluding modelled, estimated and global-monitoring values). Ordinal and binary series were excluded. Normative directions were assigned to the series without an official one: first to those used for Brazil, then to 38 further series, mostly donor flows, waste, vaccination and occupational injuries, whose intended direction is unambiguous. The result covers 34 targets for Brazil and 33 each for Finland and Norway.
- **IGES/JRC procedure.** The package's IGES/JRC procedure run unchanged on UNSD data for each country: inventory pairs, compound-growth filling, Pearson correlation, p < 0.10, classification by normative direction and performance.

Each network was built twice: with correlations between levels, as in the national time-series applications discussed above, and with correlations between year-on-year changes, which reduce the influence of smooth trends. Two tests were applied to every network. Phase-shuffled surrogates replace each series by an independent series with the same power spectrum and autocorrelation (Ding et al., 2026); the share of pairs that pass the significance filter among surrogates is the share produced by persistence alone, with no relationship between targets. A null model rewires the network at random while keeping each node's performance direction, its numbers of sent and received links and the weights; roles that reappear in the rewired networks owe nothing to who is linked to whom. Role stability was also compared across correlation coefficients, time windows and selection rules. The null model used the cut-off of three per role adopted in Section 5; the stability tests used a cut-off of ten, which is more favourable to stability.

### 7.2 Persistence produces most of the links

**Table 3.** Share of cross-SDG pairs with p < 0.10: observed and among independent surrogates (mean of 100–200 replicates).

| Source | Country | Indicators or targets | Levels: observed | Levels: surrogates | Changes: observed | Changes: surrogates |
| --- | --- | --- | --- | --- | --- | --- |
| SDG Index, normalised scores | Brazil | 101 | 71% | 48% | 14% | 10% |
|  | Finland | 101 | 52% | 37% | 11% | 10% |
|  | Norway | 101 | 54% | 40% | 11% | 10% |
| SDG Index, raw values | Brazil | 50 | 80% | 50% | 20% | 10% |
|  | Finland | 52 | 62% | 43% | 15% | 10% |
|  | Norway | 51 | 55% | 45% | 19% | 10% |
| UN series, 2010–2023 | Brazil | 34 | 43% | 27% | 14% | 10% |
|  | Finland | 33 | 35% | 24% | 11% | 10% |
|  | Norway | 33 | 40% | 27% | 15% | 10% |
| IGES/JRC procedure | Brazil | 76 | 67% | 50% | 22% | 10% |
|  | Finland | 61 | 65% | 44% | 16% | 10% |
|  | Norway | 60 | 61% | 45% | 19% | 10% |

In levels, series with no relationship to one another pass the filter in 24% to 50% of pairs, against a nominal 10%. Across specifications, surrogate pass rates are roughly one-half to four-fifths as large as the observed rates. This comparison quantifies the scale of the persistence problem without identifying which individual links are spurious. Finland and Norway have lower observed shares than Brazil, but their surrogates still pass the filter in 24% to 45% of pairs. Tightening the threshold does not remove the problem. For Brazil's SDG Index scores, independent surrogates pass p < 0.01 in 26% of pairs and p < 0.001 in 14%, roughly 140 times the nominal rate. Spearman's coefficient behaves like Pearson's (47.5% of surrogate pairs pass p < 0.10), because two monotonic series are always ranked alike. The problem lies in a significance test that treats annual observations of trending series as independent, not in the linearity of the coefficient or in the level of the threshold.

In changes, surrogates return to the nominal rate, and what remains is co-movement: 4 to 12 percentage points above chance in Brazil, and no more in Finland and Norway (1 to 9 points). This excess does not establish how many retained pairs reflect substantive relationships. The largest excess, in the IGES/JRC procedure, may partly reflect the filling rule: interpolation over common intervals can induce similar patterns of annual change.

### 7.3 Roles follow degree and direction

In the SDG Index network, the degree sequence alone fixes about 70% of the arcs in Brazil and about 60% in Finland and Norway: at densities of 0.51, 0.37 and 0.38, no rewiring moves more than 31% to 40% of them. The number of links of each indicator correlates with the linearity of its own trend (Spearman 0.63 between degree and time R² in Brazil, 0.84 in Finland and 0.76 in Norway), and in all three countries the three transmission bridges are among the ten deteriorating indicators with the most linear trends. In the rewired networks, the bridges reappear far more often than chance would allow. Mean Jaccard similarity with the observed set is 0.43 (Brazil), 0.44 (Finland) and 0.28 (Norway) with normalised scores, 0.41, 0.42 and 0.58 with raw values, and 0.59, 0.55 and 0.53 in the IGES/JRC procedure, against 0.06 to 0.10 for two random choices of three among the deteriorating targets (0.13 to 0.30 in the smaller raw-value networks). Only two of the 27 bridges, one in Finland's raw-value network and one in Norway's IGES/JRC network, have a bridge flow above the null distribution. In these data, bridge status largely reflects deterioration, a strong linear trend and high degree. Some contributors and dependent contributors exceed the null, but they change with the window, the coefficient and the basis.

**Table 4.** Similarity of role membership with the main specification (SDG Index, normalised scores; cut-off of ten per role; Jaccard, 1 = identical).

| Variant | Country | Contributors | Dependent contributors | Isolated beneficiaries | Exposed | Bridges | Relays |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Spearman instead of Pearson | Brazil | 0.33 | 0.25 | 0.33 | 0.82 | 0.82 | 0.82 |
|  | Finland | 0.18 | 0.33 | 0.33 | 0.54 | 0.67 | 0.67 |
|  | Norway | 0.43 | 0.18 | 0 | 0.80 | 0.82 | 0.67 |
| Window 2010–2025 | Brazil | 0.11 | 0.18 | 0 | 0.18 | 0.43 | 0.43 |
|  | Finland | 0.18 | 0.33 | 0.33 | 0.43 | 0.67 | 0.54 |
|  | Norway | 0.11 | 0.18 | 0.20 | 0.27 | 0.82 | 0.82 |
| Window 2015–2025 | Brazil | 0 | 0 | 0.25 | 0.18 | 0.33 | 0.33 |
|  | Finland | 0.05 | 0.05 | 0.20 | 0.33 | 0.43 | 0.33 |
|  | Norway | 0.11 | 0.33 | 0.33 | 0.15 | 0.33 | 0.33 |
| Changes instead of levels | Brazil | 0.25 | 0.11 | 0.11 | 0.33 | 0.25 | 0.25 |
|  | Finland | 0.33 | 0.25 | 0.18 | 0.33 | 0.18 | 0.25 |
|  | Norway | 0.33 | 0.05 | 0 | 0.29 | 0.54 | 0.54 |
| BH q < 0.10 | Brazil | 0.82 | 0.82 | 0.33 | 0.82 | 0.82 | 1 |
|  | Finland | 0.82 | 0.67 | 0.75 | 0.82 | 1 | 0.82 |
|  | Norway | 0.82 | 0.82 | 0.25 | 0.89 | 0.82 | 0.82 |

Roles on the deteriorating side, bridges above all, are more stable across specifications than those on the improving side in a pattern consistent with their dependence on direction and degree, which change little between specifications. With the cut-off of three, similarity falls further: between levels and changes it is zero for bridges in all three countries. When trend is removed, the order of the bridges changes as well: in Brazil, between levels and changes, the rank correlation of bridge flow among the raw-value bridges is 0.20, not significant. The Benjamini–Hochberg correction changes almost nothing, because nearly every pair is already highly significant in levels.

### 7.4 Properties of the indicators

Several properties of the indicators, rather than of the method, account for these results, and they weigh most on the SDG Index.

- **Carried values.** In the normalised SDG Index scores, the median series has 9 of its 25 annual changes equal to zero in Brazil, 15 in Finland and 14 in Norway: missing years are filled with the previous value. These steps add trend to levels and remove information from changes.
- **Bounds.** Normalised scores are capped at 0 and 100. Indicators that reach a bound become constant, so their direction depends on the measure chosen rather than on the country's performance: inequality (Palma ratio), educational attainment and freshwater withdrawal are improving by their raw values and stable by their scores.
- **Coverage.** About half of the SDG Index indicators do not meet a completeness rule of at most six missing years in 2000–2025 with no run of more than three, in Finland and Norway as in Brazil. In Brazil, the excluded include three of the ten bridges and two of the three exposed targets of the main specification with a cut-off of ten, whose normalised series consist largely of carried values. In the UN database, only 38 to 39 targets per country have an aggregate series reported by the country over 2010–2023, in Brazil as in Finland and Norway, and only 33 or 34 have one whose intended direction is unambiguous.
- **Linearised and modelled series.** The national Red List Index is the global index weighted by each species' share of range in the country, linearly interpolated between assessments and extrapolated beyond them. It ranks at or near the top of trade-off degree in every source for Brazil, and is a bridge in Norway's raw-value network and an exposed target in Finland's. Child stunting in the UN database is a modelled estimate rising almost linearly (time R² 0.95) and takes the same position when the Red List is removed. Such series are close to straight lines by construction and correlate with any other trending series.
- **Steps, scores and flows.** What remains after excluding modelled values includes series that change once and stay flat, ordinal scores, and official development assistance received, which fluctuates without trend and measures the country's performance poorly. These series dominate the networks of annual changes.

### 7.5 Significance, direction and inventories

The IGES tool accepts any correlation coefficient, whatever its significance (Zhou and Moinuddin, 2017). Removing the filter in the package's IGES/JRC procedure for Brazil adds 627 arcs (from 1,486 to 2,113), with a median |r| of 0.17 against 0.71 among the significant ones; 372 of them become trade-offs. In Finland and Norway it adds 447 and 521 arcs, with median |r| of 0.19 and 0.18 against 0.62 and 0.69, of which 224 and 246 become trade-offs. The signs of these additional estimates provide insufficient evidence for classifying the underlying associations. Bridges change little (Jaccard 1 in Brazil and Finland, 0.5 in Norway), because the strong links, which pass the filter easily, determine them. Omitting a significance filter is methodologically unjustified, and applying one is insufficient to establish validity: the links that pass are the ones Section 7.2 shows to be largely persistence.

The orientation of links presents further difficulties. Lagged and conditional tests orient in a single direction fewer than half of the significant pairs in the raw-value networks (49% in Brazil and Finland, 47% in Norway), and those tests rest on the same trending series. Without direction, the framework loses the distinction between origin and destination that gives bridges and contributors their meaning. Read without direction, ranking pairs by the trade-off degree of each end and the strength of the tie, the networks single out targets that the directed roles leave out, either because the lagged tests mark them as origins of cost or because they split their trade-offs between received and sent; and the highest-ranked pairs are nearly tied in levels. Inventories do not solve the problem either. They restrict which pairs are examined, but the IGES/JRC networks show the same persistence and the same dependence of roles on degree and direction.

### 7.6 What the tests allow

Across Brazil, Finland and Norway, correlations between the published national series examined here provide insufficient evidence to infer interlinkages or assign policy roles. In levels, trends and persistence can generate many links even under independence. In annual changes, the modest excess over the surrogate pass rate is difficult to distinguish from effects of filling, carried values and bounded scales at the level of an individual pair. The result recurs across literature-restricted and data-driven specifications. The two bridge flows exceeding the rewiring benchmark merit separate investigation, but that test alone cannot establish a transmission mechanism.

The literature addresses different parts of this problem. Sota and Venghaus (2026) reinforce the diagnosis reported in NT Dinte 77 (Desiderá Neto et al., 2025) by documenting the risk of treating coupled deterioration as beneficial across a wider literature. Khot, Warchold and Pradhan (2026) identify the need for stronger evidence on direction and mechanisms. Yuan et al. (2026) use geographic variation, so their coefficients do not rely on correlating two trending national series. Spatial ranks, however, do not establish the direction of transmission between targets. None of the three studies demonstrates a procedure that recovers reliable directed roles from short, persistent national indicator series. The distinction between improving and deteriorating targets therefore remains necessary even where the data are inadequate to estimate the roles.

## 8 Other uses of the open implementation

The implementation remains useful beyond the roles, above all as an instrument of verification.

**An open, end-to-end pipeline.** A single run collects observations from the official UNSD SDG API (or reads the SDG Index workbooks), selects and completes series, estimates associations, applies the evidence and reclassification rules, selects roles and exports workbooks and figures. It is available as a browser application and from the command line. Every intermediate decision is recorded: the evidence behind each arc, excluded and reclassified links, and every interface measure. The IGES tool, by contrast, is offered as a visualisation whose processing steps, expert-consultation procedures and intended use in decision-making are not documented to the same degree (Desiderá Neto et al., 2025). Openness allows the procedure to be replicated, scrutinised and changed.

**Two sources of evidence and two ways of defining direction.** The IGES/JRC procedure takes the existence and orientation of links from literature inventories; the SDG Index procedure estimates both from data, with direction inferred from temporal tests. Applied to the same country, the two procedures allow the same tests to be run on literature-restricted and data-driven networks, as in Section 7, and expose links or directions supported by one source and not the other.

**Policy-created links.** Literature inventories record links that studies have found or experts expect. Some interlinkages, however, are created by policy decisions rather than by mechanisms the literature would predict. In Brazil, the National School Feeding Programme (PNAE) has required since 2009 that at least 30% of the federal funds it transfers be spent on food bought directly from family farming, a share raised to 45% from 2026 (Brasil, 2009, art. 14; Brasil, 2025). The rule ties family farming to school meals and, through them, to child nutrition. A filter that keeps only links supported by an apparent mechanism or a scientific study, such as evidence that more family farming reduces child malnutrition, would remove this synergy from the network and discard the information that a strong, significant association between the indicators could carry. Data-based networks keep such links; with indicators able to support inference, comparing them with literature-based ones could reveal interlinkages created by policy.

**Policy-intended links.** Brazil's Pluriannual Plan (PPA) 2024–2027 required those formulating each programme to state which SDG targets it contributes to. Mapping each programme's central target to the targets its formulators indicated yields a network of the links that policy expects to create. All technical programmes have been classified by SDG, from their components, justification, objectives and expected results, using a BERT-based SDG classification model (ods-brasil-bahia). These intended links do not depend on correlations between indicator series. They can be compared with the literature inventories now and, once indicators with more granularity and variance are available, with the associations those indicators show. The aim is to inform hypotheses to be considered in drafting the PPA 2028–2031.

**Other countries and regions.** The same procedures and tests run for 169 countries and 14 regions or aggregates in the SDG Index, and for UNSD countries and regions in the IGES/JRC procedure. Section 7 applies the tests to Finland and Norway, where the broad pattern recurs; applied to other countries, they can show how general those results are. The indicator properties behind them, carried values, bounds, interpolation and modelling, are features of the global databases rather than of one country.

**Transmission between countries.** Overlaying national networks could in principle help investigate whether performance in one country is associated with trade-offs in another, for instance through trade. Such a design would face the limits shown in Section 7 and would require bilateral data with more variance than national annual series.

## 9 Limitations

The tests reported in Section 7 are subject to several limitations.

- **Three countries.** The tests were run for Brazil, Finland and Norway. Other countries may differ, although the properties that drive the results are features of the global databases, and Finland and Norway are among the countries with the best-rated statistical systems.

- **Choices in the tests.** The completeness rules, the selection of one series per target, the exclusion of modelled, ordinal and binary series, and the normative directions assigned to UN series without an official one, first for Brazil's series and then for 38 further series, are choices; others are possible. The null model used a cut-off of three per role, as in Section 5, and the stability tests a cut-off of ten.

- **Power of the null model.** In dense networks the degree sequence leaves little room for rewiring, so the null model cannot move most arcs. This limits its power to separate structure from degree, and is itself part of the finding: at these densities there is little structure left to separate.

- **Corrections not applied.** Significance was not corrected for autocorrelation, and no predictive test was run. At current lengths, corrections remove most significance, and splitting the series for prediction leaves too few observations; both would weaken the remaining associations further.

These limitations delimit the inference rather than establish that other countries or alternative data would necessarily yield the same results. Across the three countries examined, they do not provide a basis for treating the resulting correlation networks as reliable evidence of interlinkages.

## 10 Conclusion

The commitment to leave no one behind expresses the 2030 Agenda’s aspiration to global synergy: progress should be shared rather than achieved by some at the expense of others.

The prestige of actors from developed countries has, in the author’s interpretation, contributed to a permissive attitude towards serious methodological weaknesses, allowing tools that lack validity for inferring interlinkages or prioritising targets to be recommended to countries under United Nations guidance. This methodological concern also points to a broader political argument: the Agenda does not place the gap between developed and developing countries at the centre of its objectives and thereby risks incorporating the trade-off of unequal development into its own premises.

The IGES tool justifies the use of correlation by applying it to the sign and strength of relationships assumed to exist on the basis of the literature (Zhou and Moinuddin, 2017). When a coefficient is not distinguishable from zero, its observed sign alone is insufficient evidence of the direction of the underlying association. Adding a significance filter does not settle the problem: the tests in all three countries indicate that correlations in these series are strongly affected by trends and persistence.

The JRC initiative is commendable for recording interaction types, directions, methods and contexts, including cases in which direction cannot be established. Yet the differences between its compilation and the relationships presumed by the IGES tool, despite both drawing on the literature, show how the scope and choices of a review shape its results (Section 3.4).

The High-Level Political Forum should withdraw this indication from the toolkit offered to countries preparing VNRs. A tool that can induce erroneous interpretations is especially problematic when interlinkage analysis is intended to guide prioritisation and accelerate progress towards the goals.

The negative finding is itself useful: the tests identify a limitation of the available series and point to the need to identify, develop and collect indicators with greater granularity and meaningful variation. Such data would still require appropriate research designs and independent investigation of causal mechanisms.

The methodological finding also bears on a political question that cannot be reduced to an indicator or a network role. The Agenda aspires to leave no one behind, yet the reduction of the gap between developed and developing countries does not have the status of a guiding objective across the Agenda. In the author’s interpretation, this permits the trade-off of unequal development to persist. If past exploitation is condemned only as a historical moral wrong while the inequalities it produced continue to be enjoyed through unequal access to resources and well-being, present arrangements remain implicated in that past. The humanist promise of a global agenda must confront this contradiction if systemic synergy is to be more than an appeal.

## Data and code availability

The implementation, operational inputs, regression tests and methodological documentation are available at [github.com/netodowalter/SDG_Interlinkages](https://github.com/netodowalter/SDG_Interlinkages). The same Python service runs a Gradio application, a command-line interface and a Python API. Each run exports full and summary workbooks, node and edge tables, an *Adverse cases* record of excluded and reclassified links, an Interface_measures sheet with every role measure, rank and context value, and network images, including the Two-step interface view. IGES/JRC runs also export the link-share weighted workbook and figures, identified by the suffix \_pond. Replication should record the repository revision, data release, geographic coverage, analysis period and analytical settings.

## Appendix: Operational criteria

| **Element**        | **IGES/JRC procedure**                                                                               | **SDG Index procedure**                                                  |
|--------------------|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Analytical period  | 2000–2025                                                                                            | 2000–2025                                                                |
| Series selection   | Most distinct original numeric years; ties by IGES order                                             | Component scores as supplied                                             |
| Gap filling        | CAGR from positive endpoint pairs (constant zero for two zero endpoints); bounds on generated values | None (supplied series may contain carried or interpolated values)        |
| Shared series      | One representative target                                                                            | Distinct indicators mapped to one target keep distinct node IDs          |
| Pair exclusions    | —                                                                                                    | Same goal or same target                                                 |
| Association        | Pearson, p ≤ 0.10                                                                                    | Pearson and/or Spearman, ≥ 8 matched observations, nonzero r, p \< 0.10  |
| Orientation        | IGES/JRC evidence rules, each direction evaluated separately (Section 3.4)                           | Lagged and conditional tests, both p \< 0.10; otherwise two arcs         |
| Trend              | Linear, ≥ 3 distinct years; negligible change = stable                                               | Same                                                                     |
| Reclassification   | Exclude discordant link if min R² \< 0.10, or min R² \< 0.20 and \|r\| \< 0.40; otherwise reclassify | Same                                                                     |
| Rankings           | Top 10 positive values within direction, exact ties at position 10 included                          | Top 10 positive values within direction, ties resolved by stable node ID |
| Interface measures | Links between nodes with defined directions only                                                     | Same                                                                     |
| Isolation          | φ \< 1 among top receivers R                                                                         | Same                                                                     |
| Context            | Semantic ambitiousness, reported for every role                                                      | Years to target or to zero, reported for every role                      |
| Role overlap       | Roles are selected independently; a node may hold more than one role (Section 5.3).                  | Same                                                                     |

Intersections are not refilled with lower-ranked cases. Conditional times are in decimal years; a score at the relevant boundary has zero remaining time, and stable or undetermined trajectories have none. Benjamini–Hochberg q-values are computed but are not the active selection criterion.

## References

Ah-Pine, J., & Nasho Ah-Pine, E. (2026). A consistent and integrated network analysis framework for decoding interlinkages between sustainable development indicators at the global scale. *European Journal of Operational Research*, 335, 661–673.

Brasil. (2009). *Lei nº 11.947, de 16 de junho de 2009*. Dispõe sobre o atendimento da alimentação escolar e do Programa Dinheiro Direto na Escola aos alunos da educação básica. Diário Oficial da União.

Brasil. (2025). *Lei nº 15.226, de 30 de setembro de 2025*. Altera a Lei nº 11.947, de 16 de junho de 2009. Diário Oficial da União. https://legis.senado.leg.br/norma/41512463

Chaniotakis, E. et al. (2024). Scoping SDG interlinkages and methods to infer them. *International Journal of Sustainable Development*, 27(5), 1–54.

Dang, H.-A. H., Pullinger, J., Serajuddin, U., & Stacy, B. (2023). Statistical performance indicators and index—a new tool to measure country statistical capacity. *Scientific Data*, 10, 146. https://doi.org/10.1038/s41597-023-01971-0

Desiderá Neto, W. A., Pereira, J. V. S., Zardo, L. M. M., & Franco, S. (2025). *A rede de interações entre as metas dos Objetivos de Desenvolvimento Sustentável (ODS) no Brasil: uma discussão metodológica sobre sinergias e conflitos na Agenda 2030*. Nota Técnica Dinte 77. Ipea. https://doi.org/10.38116/ntdinte77-port

Di Lucia, L., Slade, R., & Khan, J. (2022). Decision-making fitness of methods to understand Sustainable Development Goal interactions. *Nature Sustainability*, 5(2), 131–138.

Ding, Y., Chen, X., Shuai, C., Wang, C., Xu, Z., & Zhao, B. (2026). Understanding the global interdependencies of SDGs via causal network analysis. *Sustainable Production and Consumption*, 67, 13–26. https://doi.org/10.1016/j.spc.2026.05.010

Fronza, V., Barbero Vignola, G., Borchardt, S., Valentini, S., Buscaglia, D., Maroni, M., & Marelli, L. (2023). *Uncovering SDG Interlinkages: interconnection at the core of the 2030 Agenda*. EUR 31666 EN, JRC134248. Publications Office of the European Union. https://doi.org/10.2760/711960

Issa, L., & El Fadel, M. (2026). Prioritization of the Sustainable Development Goals: Developing and testing a novel framework under varying geographic scales. *Sustainable Development*, 34, 2251–2278. https://doi.org/10.1002/sd.70424

Issa, L., Mezher, T., & El Fadel, M. (2024). Can network analysis ascertain SDGs interlinkages towards evidence-based policy planning? A systematic critical assessment. *Environmental Impact Assessment Review*, 104, 107295.

Khot, U. A., Warchold, A., & Pradhan, P. (2026). Existing gaps in understanding Sustainable Development Goals interactions: Insights from a systematic review. *Environmental Impact Assessment Review*, 118, 108274. https://doi.org/10.1016/j.eiar.2025.108274

Kroll, C., Warchold, A., & Pradhan, P. (2019). Sustainable Development Goals (SDGs): Are we successful in turning trade-offs into synergies? *Palgrave Communications*, 5, 140.

Miola, A. et al. (2019). *Interlinkages and policy coherence for the Sustainable Development Goals implementation: an operational method to identify trade-offs and co-benefits in a systemic way*. Publications Office of the European Union.

Mustajoki, J. et al. (2022). Ambitiousness of Sustainable Development Goal (SDG) targets: classification and implications for policy making. *Discover Sustainability*, 3, 36. https://doi.org/10.1007/s43621-022-00104-8

Nilsson, M. et al. (2017). A framework for understanding Sustainable Development Goal interactions. In A.-S. Stevance (Ed.), *A guide to SDG interactions: from science to implementation*. International Council for Science.

Pradhan, P., Costa, L., Rybski, D., Lucht, W., & Kropp, J. P. (2017). A systematic study of Sustainable Development Goal (SDG) interactions. *Earth's Future*, 5(11), 1169–1179.

Sachs, J. D., Lafortune, G., Fuller, G., & Iablonovski, G. (2026). *Implementing Sustainable Development: 2030 and Beyond. Sustainable Development Report 2026*. SDSN and Dublin University Press. https://doi.org/10.82163/225

Sota, R., & Venghaus, S. (2026). Talking past each other: A review of the quantitative study of interlinkages between the sustainable development goals. *Energy, Sustainability and Society*, 16, 14. https://doi.org/10.1186/s13705-026-00572-0

Su, H., Krol, M. S., & Hogeboom, R. J. (2022). The role of context in identifying linkages between SDG 2 (food) and SDG 6 (water). *Sustainability Science*, 17(4), 1605–1618. https://doi.org/10.1007/s11625-022-01158-3

United Nations. (2026a). *The Sustainable Development Goals Report 2026*. UN DESA. https://unstats.un.org/sdgs/report/2026/

United Nations. (2026b). *The Sustainable Development Goals Report 2026: Technical Note for Progress Assessment*. United Nations Statistics Division.

Xiao, H., Liu, Y., & Ren, J. (2023). Synergies and trade-offs across sustainable development goals: A novel method incorporating indirect interactions analysis. *Sustainable Development*, 31, 1135–1148. https://doi.org/10.1002/sd.2446

Yuan, Z., Gao, X., Liu, X., Feng, Y., & Zhang, L. (2026). Progress, trade-offs, and synergies of sustainable development goals in China's urban agglomerations. *Humanities and Social Sciences Communications*, 13, 1680. https://doi.org/10.1057/s41599-026-07960-z

Zhou, X., & Moinuddin, M. (2017). *Sustainable Development Goals interlinkages and network analysis: A practical tool for SDG integration and policy coherence*. IGES Research Report RR1602. Institute for Global Environmental Strategies. https://www.iges.or.jp/en/pub/sustainable-development-goals-interlinkages/en

Zhou, X., & Moinuddin, M. (2021). Impacts and implications of the COVID-19 crisis and its recovery for achieving sustainable development goals in Asia: A review from an SDG interlinkage perspective. Book chapter, Elsevier. https://doi.org/10.1016/B978-0-323-85512-9.00018-8
