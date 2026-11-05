# Beyond Co-movement: Performance Direction and Transmission Roles in SDG Interlinkage Networks

Walter Antonio Desiderá Neto · Draft, November 2026

## Abstract

Synergies and trade-offs among Sustainable Development Goal (SDG) targets are usually inferred from the sign of associations between normatively oriented indicators. This article argues that such networks cannot be interpreted without the direction of observed performance. Two indicators that deteriorate together are positively associated, yet their reinforcement is not a contribution to the 2030 Agenda. The sign of association already separates improving from deteriorating targets, which is why synergy networks tend to form two clusters; what it cannot show is which cluster is which. The argument builds on an application to Brazil's 2024 Voluntary National Review, which used the approaches then available, the IGES tool and the JRC compilation, and, on examining target progress, raised the point that neither considers the direction of performance when classifying interlinkages (Desiderá Neto et al., 2025).

We propose a framework in which performance direction enters link classification, node metrics and role selection. Once links are classified this way, synergies connect targets moving in the same direction, and trade-offs become the only links crossing between an improving and a deteriorating subsystem. The contribution of network analysis would then lie at this interface. It could identify transmission bridges, deteriorating targets that receive trade-offs from improving targets and pass deterioration on through synergies, and isolated beneficiaries, improving targets that gain through trade-offs from deteriorating targets while passing forward less synergy than they receive. Neither role is visible to centrality measures or to target-by-target monitoring.

The framework is implemented in an open repository with two procedures: literature-based IGES/JRC relationships with United Nations indicators, and annual SDG Index indicator scores. Statistical tests for Brazil, and for Finland and Norway, whose national statistical systems are among the best rated by the Statistical Performance Index, with SDG Index scores and raw values, UN series and the IGES/JRC procedure, show that persistence and trends produce most of the links, that roles follow each indicator's direction and the linearity of its trend, and that what remains once trend is removed is small and indistinguishable from artefacts of filling, carried values and bounded scales. With the indicators as currently published, correlation between national series cannot support valid inference about interlinkages, and network analysis built on it cannot identify roles. Tools without that validity should not be recommended to countries for their Voluntary National Reviews, and other indicators, with more granularity and variance, are needed.

**Keywords:** Sustainable Development Goals; synergies; trade-offs; policy coherence; network analysis; transmission; monitoring and evaluation.

## 1 Introduction

The indivisibility of the 2030 Agenda is a problem for both monitoring and public action. Progress is assessed target by target, yet the processes behind outcomes cross sectoral boundaries. An intervention may advance several objectives, meet constraints originating elsewhere, or improve one outcome at the expense of another. Network analysis has become a common way to represent these interdependencies (Issa, Mezher and El Fadel, 2024; Chaniotakis et al., 2024).

Its relevance depends on what its links mean. Synergies matter because mutually reinforcing improvements multiply the benefits of public action; trade-offs matter because gains in one domain may involve losses in another. Most quantitative applications operationalise these concepts through the sign of correlations between indicators oriented so that higher values are better (Pradhan et al., 2017; Zhou and Moinuddin, 2017). Orientation makes scales normatively comparable. It does not establish whether the observed trajectories are improving or deteriorating.

This gap has two consequences, which structure the article.

1. **Without performance direction, the network cannot be operationalised meaningfully, nor can its links be properly read.** A positive association between two deteriorating targets is labelled a synergy, and a target that drags its neighbours backwards is ranked as a leading contributor. Rankings built on such links answer a question nobody asked.
2. **With performance direction, network analysis would gain a contribution of its own.** Classified links separate an improving subsystem from a deteriorating one and expose the trade-off arcs that connect them. Two roles at this interface would matter most for policy: **transmission bridges**, which carry the cost of others' gains into the deteriorating subsystem and propagate it, and **isolated beneficiaries**, whose improvement is associated with others' deterioration and is not passed on.

The argument builds on an application to Brazil's 2024 Voluntary National Review (VNR), documented in Ipea's Technical Note Dinte 77 (Desiderá Neto et al., 2025). The note applied the approaches recommended to countries at the time, the IGES tool and the JRC compilation, and proposed two network categories based on weighted degree. When target progress could be examined, it raised a point that neither the IGES tool nor the JRC compilation incorporates: the meaning of synergy and trade-off depends on whether the targets involved are improving or deteriorating. This article develops that finding into an operational framework, shows where its added value would lie, and tests whether the indicators currently available can support it. They cannot.

Section 2 reconstructs the VNR exercise and the finding that motivates this article. Section 3 positions the framework within the literature and examines the evidential basis of literature-derived networks. Section 4 sets out the analytical design. Section 5 defines the metrics and roles, with emphasis on the interface roles. Section 6 sets out why the roles would matter for policy. Section 7 reports the statistical tests. Section 8 discusses other uses of the open implementation and Section 9 the limits of the tests. Section 10 concludes.

## 2 Starting point: the Brazilian VNR exercise and its finding

### 2.1 The original application

Brazil's 2024 VNR replicated the IGES SDG Interlinkages Analysis and Visualisation Tool (Zhou and Moinuddin, 2017). The IGES relationships and their directions were kept unchanged. Indicator availability limited the network to 73 targets observed annually over 2010–2023, with gaps imputed by compound annual growth rates. Every assumed link was weighted and classified by its Pearson coefficient, regardless of strength, significance or the distribution of the series (Desiderá Neto et al., 2025).

The complete network was too dense to read, so it was filtered into separate synergy and trade-off subnetworks. The synergy subnetwork showed two clusters, with targets 10.1, 9.4 and 8.5 apparently bridging the transmission of positive effects between them. Read in the usual way, the picture suggested two agendas progressing well, joined by a few targets whose role was to connect them, alongside a dense tangle of trade-offs that was hard to interpret. The trade-off subnetwork qualified that reading: the same targets, particularly 9.4, were also major receivers and senders of trade-offs. A role suggested by one subnetwork could be contradicted by the other. Section 4.4 suggests why such clusters arise.

That observation motivated two metrics built from weighted in- and out-degree in each subnetwork:

```latex
\mathrm{SL.Out}_i = \mathrm{CGP.Out.S}_i - \mathrm{CGP.Out.T}_i, \qquad \mathrm{TL.In}_i = \mathrm{CGP.In.T}_i - \mathrm{CGP.In.S}_i
```

Targets with positive SL.Out were labelled *transversal collaboration* ("helping without hindering"); targets with positive TL.In were labelled *transversal neglect* ("hindered without being helped"). A weighting factor based on each node's share of links was added, to flag targets whose centrality might reflect uneven research coverage rather than interdependence.

### 2.2 What the examination of progress revealed

When target-level progress data became available, the note examined what the categories could and could not show. The note reasoned through a hypothetical network in which 90% of targets were strongly synergistic with one another while one target held trade-offs with all of them. If the synergistic targets were regressing together while the isolated target advanced rapidly, the "transversal collaborators" would be dragging the system backwards. Their synergy would operate in the direction opposite to the one desired.

The reverse also held. A target with high TL.In but improving performance could not be described as neglected. It was more plausibly pursued through individualised strategies, indifferent to the rest of the plan, such that deterioration elsewhere contributed to its own progress. The note read this as a possible sign of concentrated misallocation of scarce resources (Desiderá Neto et al., 2025).

The note drew two conclusions. First, positive performance is not an intrinsic attribute of synergy: with links classified by the sign of association alone, as in the available methods, network positions cannot be read as contribution or neglect. Second, performance has three dimensions that must be kept apart: **stage** (distance to the target), **direction** (approaching or moving away) and **pace** (speed of change). Its literature search found studies that consider the stage of achievement as a limit on a target's capacity to transmit synergies. It found none that examined how the *direction* of performance changes the meaning of synergy and trade-off. The point had been made as a conceptual typology by the authors of the IGES tool (Zhou and Moinuddin, 2021) and by Su, Krol and Hogeboom (2022), in publications outside the tool's documentation (Section 3.2).

### 2.3 From diagnosis to framework

This was the note's central contribution. The IGES tool and the JRC compilation were the interlinkage approaches suggested to countries preparing VNRs, and neither incorporates the direction of target performance into the classification of interlinkages. By applying them in full, reporting openly what their metrics could and could not support, and identifying performance as the missing element, the note took the first step towards the framework presented here. The present framework carries that step through every stage of the analysis. The changes are summarised below; Sections 4 and 5 justify each one.

| Element | NT Dinte 77 (2025) | Present framework |
| --- | --- | --- |
| Link evidence | IGES links, all retained regardless of significance | IGES/JRC evidence rules with p ≤ 0.10, or SDG Index associations with p < 0.10 and temporal orientation |
| Series preparation | One indicator per target, CAGR imputation | Coverage-based series selection, bounded CAGR imputation, consolidation of shared series |
| Link classification | Sign of the oriented correlation | Sign of the oriented correlation, then checked against both nodes' trajectories; weak discordant links excluded, others reclassified |
| Contribution metric | SL.Out = out-synergy − out-trade-off | Colab, same formula, read only among improving nodes |
| Exposure metric | TL.In = in-trade-off − in-synergy | Neglect = in-trade-off **+** in-synergy from deteriorating sources, read only among deteriorating nodes |
| Interface measures | None | Trade-off received and sent across the interface, synergy passed on, bridge and relay flows, forward ratio φ |
| Roles | Two categories | Six roles defined by performance direction, including the two interface roles |
| Context | None | Semantic ambitiousness (IGES/JRC) or conditional time to boundary (SDG Index), reported for every role |
| Coverage bias | Link-share weighting factor | Same factor, IGES/JRC only, produced as a parallel weighted version with a rank comparison (Section 5.6) |

The change in the exposure metric is the clearest consequence of incorporating performance. TL.In *subtracted* incoming synergies on the assumption that any synergy is help. Neglect *adds* incoming synergies from deteriorating sources, because reinforcement from a deteriorating neighbour is a source of pressure, not support.

The link-share weighting factor is retained for the IGES/JRC procedure, where links come from literature inventories and coverage bias can arise. It is applied as a parallel version rather than a correction, so that positions that change markedly can be flagged (Section 5.6).

## 3 Position in the literature and evidential foundations

### 3.1 How synergies and trade-offs are usually operationalised

Reviews group methods for inferring SDG interlinkages into qualitative, literature-review and quantitative traditions (Chaniotakis et al., 2024). Qualitative scoring, such as the seven-point scale of Nilsson et al. (2017), captures context but lacks explicit criteria for each score. Literature compilations, such as the JRC inventory (Miola et al., 2019; Fronza et al., 2023), accumulate findings across studies but describe relationships that may not hold uniformly across settings. Quantitative studies correlate indicator series: Pradhan et al. (2017) define synergies and trade-offs from the sign of correlations between oriented indicators, and Kroll, Warchold and Pradhan (2019) examine how these classifications shift over time.

These approaches share a premise: once indicators are oriented so that higher is better, a positive association means mutual support. This premise holds only when both indicators improve. When both deteriorate, the same coefficient describes reinforcement of deterioration. Studies that follow classifications over time ask whether a relationship changes sign, not whether the outcomes it links are moving towards or away from their targets.

### 3.2 Recognition of the problem and additive approaches

The premise has been questioned. In a review of the effects of the COVID-19 crisis on the SDGs in Asia, the authors of the IGES tool distinguished four configurations according to whether a causal and an affected target are progressing or regressing: synergy, trade-off, "development drag" and "coupled deterioration" (Zhou and Moinuddin, 2021). Su, Krol and Hogeboom (2022) noted that two deteriorating indicators produce a positive coefficient and are therefore labelled a synergy. A recent review of quantitative interlinkage studies treats this as a widespread fallacy, recommends moving beyond the synergy–trade-off labels, and concludes that a research gap remains in operationalising such enhanced interpretations (Sota and Venghaus, 2026). NT Dinte 77 reached the same point independently, by applying the IGES tool, whose procedure does not incorporate performance.

Other studies combine performance and networks additively. Issa and El Fadel (2026) add an urgency score, built from normalised achievement, a world benchmark and the trend, to an influence score derived from centrality and from links classified by sign and normative direction. Ah-Pine and Ah-Pine (2026) select indicators that are both underperforming, by level, and central in a cross-sectional network. Yuan et al. (2026) report the progress of goals alongside a correlation-based classification of their interactions. In all three, performance enters as a separate criterion and the meaning of links stays sign-based, so a target that deteriorates within a deteriorating cluster scores as both urgent and positively influential: a lever to stimulate.

Attention to indirect effects is also growing. Xiao, Liu and Ren (2023) extend direct synergies and trade-offs to indirect ones transmitted through intermediate targets, finding that synergies account for most of the total influence once indirect paths are counted. Without performance, however, a chain of synergies may be propagating deterioration. Causal orientation does not change this: Ding et al. (2026) orient links among goals with convergent cross mapping but classify them by the sign of correlation, reading a positive sign as joint improvement, and find that 82% of the relations are synergies. Reviews also point to directionality, causal mechanisms and transboundary effects as understudied (Khot, Warchold and Pradhan, 2026). Their "temporal dynamics" concerns whether an interaction changes over time (Kroll, Warchold and Pradhan, 2019), which differs from whether the linked targets are improving or deteriorating.

This article responds to the gap identified by Sota and Venghaus. It keeps the synergy and trade-off labels as descriptions of the form of an association, qualifies them by the trajectories of the linked targets, and carries that qualification through link classification, metrics, two-step transmission measures and role selection, in an open implementation.

### 3.3 The limits of centrality

Network applications typically rank targets by degree, betweenness, eigenvector or closeness centrality (Issa, Mezher and El Fadel, 2024). Weighted in- and out-degree are the most common because they are simple and separate sending from receiving. Issa, Mezher and El Fadel recommend composite indices to balance the distortions of single measures. Composite indices still treat all synergy weight as favourable. A target can be central because it accompanies widespread improvement, because its deterioration accompanies deterioration elsewhere, or because it sits where gains and losses meet. These positions call for different responses, and no combination of centralities distinguishes them without performance direction.

Decision-makers also value simplicity and direct applicability over methodological sophistication (Di Lucia, Slade and Khan, 2022). A framework that translates network positions into a small number of interpretable roles, each tied to a specific question, addresses that demand without hiding the underlying evidence.

### 3.4 Evidential basis of literature-derived networks

The IGES tool combines relationships drawn from a union of reference sources with country-specific indicator correlations (Zhou and Moinuddin, 2017). The JRC compilation records interaction types, directions, methods and contexts, including cases where direction cannot be established (Fronza et al., 2023). The literature supplies the existence and orientation of candidate relationships; local correlations supply their strength. Correlations do not independently establish direction. Uneven research coverage may also make well-studied targets appear more connected (Desiderá Neto et al., 2025); the IGES/JRC procedure therefore also produces a link-share weighted version (Section 5.6). Inventories also omit links created by policy rather than by mechanisms studied in the literature (Section 8).

Comparing the two inventories shows how sensitive the network is to construction choices. The consolidated comparison contains 8,751 IGES records and 5,701 JRC records, with 3,133 matches: 35.80% of the former and 54.96% of the latter.

**Table 1.** Directional agreement among matched IGES and JRC records

| Directional evidence | Records | Share of matched records | Treatment in the network |
| --- | --- | --- | --- |
| Uncertain in the JRC evidence | 1,286 | 41.05% | Both directions retained, unless IGES codes clear one-sided evidence in the reverse direction |
| Complete agreement | 1,171 | 37.38% | Retained as coded |
| Partial agreement | 597 | 19.06% | Both directions retained |
| Opposite unidirectional orientations | 79 | 2.52% | Both directions retained; conflicting evidence recorded |
| Total | 3,133 | 100.00% |  |

*Note:* Complete agreement denotes the same single direction or bidirectionality in both inventories; partial agreement denotes a single direction in one and bidirectionality in the other. Percentages are rounded independently. Counts refer to relationship records, not unique unordered target pairs. The consolidated comparison permits verification of totals but does not independently reproduce the matching of the underlying inventories. Source: Zhou and Moinuddin (2017); Fronza et al. (2023).

These differences are not an error rate. An unmatched relationship may reflect scope, coverage or coding, and the JRC compilation is not an exhaustive standard. What the comparison does establish is that a credible framework must state how each category of directional evidence becomes an arc. The last column of Table 1 makes this explicit, so that alternative rules can be tested in replication.

Each direction of a pair is evaluated separately. Clear JRC evidence for a direction (single-sided or double-sided) always retains it. A direction is rejected when the pair is absent from both inventories; when it appears in only one inventory and that inventory codes the reverse direction as one-sided; or when IGES codes the reverse direction as one-sided clear and JRC codes the reverse direction as single-sided or the pair as unclear. All other directions are retained, and every arc records the evidence from both sources. In practice, unresolved disagreement is represented by two arcs rather than settled by choosing one source.

## 4 Analytical design

### 4.1 Two procedures for building the network

**IGES/JRC procedure.** Candidate target relationships come from the IGES inventory, assessed against JRC evidence on direction (Table 1). Observations are collected from the UNSD SDG database by geographic code (M49), for a country or region. For each target, the series with the greatest number of distinct original numeric years during 2000–2025 is selected, with ties broken by IGES order. Eligible gaps are filled by series-specific compound annual growth rates computed from positive endpoint pairs, with bounds applied to generated values. Series shared by several targets enter the calculations through one representative target, so identical observations are not counted as independent evidence of interdependence. Eligible pairs receive Pearson coefficients and are retained at p ≤ 0.10.

**SDG Index procedure.** The SDG Index (Sachs et al., 2026) is distinct from the official UN framework. It combines indicators from several sources on a normalised 0–100 scale, where 100 is an operational benchmark rather than full attainment of a UN target. The procedure uses annual component scores rather than goal or overall scores, for 169 countries and 14 regions or aggregates. An editorial mapping links 101 components to SDG targets. Pairs within the same goal or target are excluded before testing. Retained pairs need at least eight matched observations, a nonzero coefficient (Pearson, Spearman or both) and nominal p < 0.10. Benjamini–Hochberg q-values are kept for sensitivity analysis.

In the SDG Index procedure, orientation is exploratory. A direction is supported when both a lagged association and a conditional association, controlling for the recipient's previous value, reach p < 0.10. A single arc is kept when only one direction is supported. Two arcs are kept when both directions are supported or neither can be distinguished, and the two situations are recorded separately.

### 4.2 Performance direction

Improvement means movement towards the desired outcome; deterioration means movement away from it. Neither term says whether a target has been achieved or is on track for 2030. Following the three dimensions identified in Section 2.2, the framework uses **direction** to classify links, and uses **stage** and **pace** as context reported for every role (Section 5.4). This separation is consistent with the UN progress assessment, which evaluates change against target requirements (United Nations, 2026a, 2026b), but the framework does not reproduce its categories.

For each series, a linear trend is fitted over the analytical period and its slope multiplied by the desired direction *d*: +1 when an increase is favourable, −1 when a decrease is favourable. SDG Index scores already ascend normatively, so *d* = +1.

```latex
x_i(t) = \alpha_i + \beta_i t + \varepsilon_i(t), \qquad \beta_i^{*} = d_i \beta_i, \qquad d_i \in \{-1, +1\}
```

Positive and negative adjusted slopes indicate improvement and deterioration. A numerically negligible fitted change is classified as stable, and fewer than three distinct years as undetermined. The trend R² measures how closely observations follow the fitted trajectory; it says nothing about the causal validity of any relationship.

### 4.3 Classifying links with performance

Initial link types come from the sign of the oriented association. Each retained link is then checked against the trajectories of its two nodes. A link is *discordant* when its initial type conflicts with those trajectories: for example, a positive oriented association between an improving and a deteriorating node.

Let *m* be the smaller of the two trend R² values and |r| the absolute association. A discordant link is excluded if *m* < 0.10, or if *m* < 0.20 and |r| < 0.40. Weak trends cannot carry a reclassification, and weak associations cannot withstand one. Other discordant links between nodes with defined directions are reclassified to match the trajectories. The original coefficient and initial type are preserved in an *Adverse cases* record; link weights use |r|. Links involving stable or undetermined nodes keep their initial type.

**Table 2.** Retained links by the trajectories of their nodes

| Source | Recipient | Type | Interpretation (hypothesis) |
| --- | --- | --- | --- |
| Improving | Improving | Synergy | Reinforcement of improvement |
| Deteriorating | Deteriorating | Synergy | Reinforcement of deterioration |
| Improving | Deteriorating | Trade-off | The source's gains are associated with the recipient's losses |
| Deteriorating | Improving | Trade-off | The recipient's gains are associated with, and may be sustained by, the source's losses |

*Note:* Interpretations are hypotheses about relationships, not estimated causal effects. Arcs keep their literature-based or temporal evidential status. The four rows correspond to the configurations of Zhou and Moinuddin (2021): synergy, coupled deterioration, trade-off and development drag.

The last two rows describe opposite situations. In the third, the improving node is the source and the cost falls downstream. In the fourth, the improving node is the recipient, and its improvement may depend on deterioration upstream. This is the configuration NT Dinte 77 identified as possible concentrated misallocation. Keeping the two rows distinct is what allows the interface roles of Section 5.

### 4.4 What the network adds beyond co-movement

Reclassification makes one property hold by construction. Among nodes with defined directions, synergies connect nodes moving in the same direction and trade-offs connect nodes moving in opposite directions. The classified network therefore splits into two synergy subsystems, one improving and one deteriorating, joined only by trade-off arcs (Figure 1, Section 5).

In practice, the sign of the oriented association already produces most of this split. In Brazil's SDG Index network, 98.5% of the links that the sign alone classifies as synergies connect indicators moving in the same direction, and 99.1% of the trade-offs connect indicators moving in opposite directions; the 42 discordant links, out of 3,347, all fail the trend-fit criteria and are excluded. This is to be expected when trending series are correlated in levels. It also explains a recurrent feature of synergy networks built with the IGES approach, including the two clusters observed in the Brazilian VNR exercise (Section 2.1): synergy subnetworks tend to split into an improving and a deteriorating cluster.

The IGES classification thus already separates the two groups, and the clusters themselves were an early sign that performance was at work in the network. What the classification does not do is say which cluster is which, so reinforcement of deterioration is read as collaboration. The contribution of performance direction therefore lies less in reclassifying links than in giving them their meaning and in locating the interface between the two clusters.

This changes the reading of the clusters and of what connects them. In a sign-based synergy network, a few targets with strong links to both clusters appear to bridge two agendas that are progressing, which suggests that the task is to strengthen communication between them. Force-directed layouts reinforce this impression: when a target has strong links on both sides, they pull the two clusters together, and the separation produced by the sign becomes hard to see. Once performance is considered, the clusters are an improving and a deteriorating subsystem, and synergies do not cross between them. The two subsystems communicate only through trade-offs, which is also why trade-off networks are always dense and tangled: they consist of the links between the two groups. Apparent synergy bridges between clusters must therefore rest on links discordant with the trajectories or on targets without a defined direction. The connection between the clusters is not something to stimulate. It is where unwanted transmission passes, and where it should be interrupted.

Whether produced by the data or completed by reclassification, this split is not a finding in itself. A concentration of synergies within groups of the same direction cannot be offered as evidence that those groups are causal systems. The information the network adds over a simple list of improving and deteriorating targets lies elsewhere:

- **which** pairs are linked at all, as established by literature evidence or statistical filters;
- **the orientation** of each link, from literature or temporal tests;
- **the strength** of each link;
- **the structure of the interface**: which nodes receive the trade-off arcs that cross between subsystems, and what they do with them.

The last item is where network analysis contributes something that target-by-target monitoring cannot. A list of deteriorating targets does not show which of them absorb the cost of gains elsewhere and pass it on. A list of improving targets does not show which of them improve at the expense of others while sending nothing forward.

## 5 Metrics and network roles

### 5.1 Contribution and exposure

With links classified by performance, each metric is read only within the performance group where its meaning is unambiguous. Let *w(i,j)* be the weight of the arc from *i* to *j*, and let *I* and *D* denote the improving and deteriorating subsystems.

**Collaboration** keeps the form of the SL.Out metric of NT Dinte 77 but is read only among improving nodes, where outgoing synergies reach other improving nodes and outgoing trade-offs reach deteriorating ones:

```latex
\mathrm{Colab}(i) = \sum_{j:\,\text{synergy}} w(i,j) - \sum_{j:\,\text{trade-off}} w(i,j), \qquad i \in I
```

**Neglect** replaces TL.In and is read only among deteriorating nodes. Incoming trade-offs come from improving sources; incoming synergies from deteriorating sources are added, not subtracted:

```latex
\mathrm{Neglect}(k) = \sum_{i:\,\text{trade-off}} w(i,k) + \sum_{j \in D:\,\text{synergy}} w(j,k), \qquad k \in D
```

Neither name implies intent. "Neglect" denotes a concentration of adverse incoming relationships, not deliberate institutional neglect or insufficient spending. Neither metric estimates the marginal return to an intervention.

### 5.2 Interface measures

Aggregate scores hide where adverse pressure comes from. Neglect mixes pressure from the improving subsystem (trade-offs) with pressure from within the deteriorating one (synergies). The framework therefore separates the components that describe traffic across the interface:

| Measure | Defined for | Meaning |
| --- | --- | --- |
| T⁺(k) | k ∈ D | Incoming trade-off weight from improving sources: the cost of others' gains arriving at k |
| S⁻(k) | k ∈ D | Incoming synergy weight from deteriorating sources |
| B(k) | k ∈ D | Outgoing synergy weight to deteriorating nodes: what k passes on |
| R(i) | i ∈ I | Incoming trade-off weight from deteriorating sources: gains associated with others' losses |
| Sₒ(i) | i ∈ I | Outgoing synergy weight to improving nodes: what i passes forward |
| C(i) | i ∈ I | Outgoing trade-off weight to deteriorating nodes: the cost of i's gains downstream |

Only links between nodes with defined directions enter these measures; links from stable or undetermined nodes do not.

Two-step flows follow directly. The total weight of all paths that enter a deteriorating node *k* as a trade-off from an improving node and leave as a synergy to a deteriorating node is the product of the two sums:

```latex
\mathrm{Bridge}(k) = \sum_{i \in I} \sum_{j \in D} w(i,k)\,w(k,j) = T^{+}(k) \times B(k)
```

The analogous flow within the deteriorating subsystem, Relay(k) = S⁻(k) × B(k), describes deterioration received from and passed to other deteriorating nodes. For improving nodes, the forward ratio φ(i) = Sₒ(i) / R(i) indicates how much of what a node gains from others' losses is matched by synergies it passes on. A value of zero means nothing is passed forward; the framework treats φ < 1, passing forward less than is received, as isolation.

### 5.3 Six roles

Each role is selected by its own score within the relevant performance group and lists only the three highest-ranked nodes with positive values. Roles are selected independently, so a node can hold more than one: a target can be both a contributor and a dependent contributor, or both a transmission bridge and a deterioration relay. The order within each list carries the information that matters for investigation, the first more than the third, and a cut-off of three keeps the lists short enough to read as priorities. Lower-ranked cases are not brought in to fill a role.

| Role | Group | Selection | Question it raises |
| --- | --- | --- | --- |
| **I-1 Contributor** | Improving | Three highest Colab, not top C | How can these beneficial interactions be sustained or extended? |
| **I-2 Dependent contributor** | Improving | Three highest R among nodes with φ ≥ 1 | Do the gains that this node spreads depend on losses elsewhere? |
| **I-3 Isolated beneficiary** | Improving | Three highest R among nodes with φ < 1 | Is this improvement sustained by deterioration elsewhere and kept rather than shared? |
| **D-1 Exposed target** | Deteriorating | Three highest Neglect, not top B | Where does the pressure come from, and can it be contained? |
| **D-2 Transmission bridge** | Deteriorating | Three highest Bridge(k) | Does the cost of others' gains enter the deteriorating subsystem here and spread? |
| **D-3 Deterioration relay** | Deteriorating | Three highest Relay(k) | Is deterioration reproduced here and passed on? |

A node that holds two roles answers two questions at once. A contributor that is also a dependent contributor spreads gains that rest in part on losses elsewhere; a bridge that is also a relay is where the cost of others' gains enters the deteriorating subsystem and where deterioration is reproduced. I-2 and I-3 cannot coincide, since they split receivers by φ. Two exclusions remain, because they concern rankings that are not roles. Contributors exclude the top senders of costs (C): a target whose gains are associated with losses downstream is the origin of what bridges propagate, and should not be labelled a contributor without qualification. Exposed targets exclude the top senders of deterioration (B), which pass pressure on rather than only receive it. The roles are not a ranking of the intrinsic worth of targets, and not every relevant target falls into one. They separate questions that a single centrality measure would conflate, while the full network stays available for scrutiny.

### 5.4 Context: characterising roles

Direction alone does not capture what a target demands. Context therefore characterises every role, using a measure suited to each procedure; it does not determine membership.

In the IGES/JRC procedure, the context is **semantic ambitiousness**: the strength of the commitment expressed in a target's wording (Mustajoki et al., 2022). A commitment to eradicate a deprivation is more demanding than one to reduce it, whatever the setting. Within a role, high ambitiousness marks improvement on a demanding commitment, and low ambitiousness marks deterioration despite a modest one. Semantic ambitiousness differs from relative ambitiousness (distance to target) and absolute ambitiousness (effort required), and the target-level coding is distinct from the goal-level aggregates reported by Mustajoki et al.

In the SDG Index procedure, the common scale allows a measure of **stage and pace** together. Using the latest score *S* and the fitted slope:

```latex
T_{100} = \frac{\max(0,\,100 - S)}{\beta}, \;\; \beta > 0; \qquad T_{0} = \frac{\max(0,\,S)}{|\beta|}, \;\; \beta < 0
```

Every selected node is reported with its T₁₀₀ or T₀. These times rank urgency within each role: a transmission bridge close to the lower boundary is more urgent than one deteriorating slowly. These are conditional extrapolations at the fitted pace, not forecasts. A long T₀ means slow deterioration relative to the remaining score, not demonstrated resilience to shocks.

### 5.5 The interface roles as the main contribution

Two roles carry the contribution that only a network can make, and they mirror each other across the interface (Figure 1).

![Figure 1 · interface roles between the improving and deteriorating subsystems](figures/figure1_interface_roles.png)

**Figure 1.** After classification, synergies stay within each subsystem and trade-offs cross between them. A transmission bridge receives the cost of gains upstream and spreads it; an isolated beneficiary receives gains associated with losses elsewhere and passes nothing on.

A **transmission bridge** (D-2) is a deteriorating target that receives trade-offs from improving targets and passes deterioration on through synergies. It is where the cost of gains elsewhere enters the deteriorating subsystem and spreads. Selecting it by Bridge(k), rather than by total Neglect, matters: a node can receive little pressure overall yet be the main point of entry and propagation. Conversely, a node with high Neglect may receive and pass on deterioration entirely within the deteriorating subsystem, which makes it a relay, not a bridge.

An **isolated beneficiary** (I-3) is an improving target that receives trade-offs from deteriorating targets and passes forward less synergy than it receives (φ < 1). Its improvement is associated with losses elsewhere and largely stays where it is. This is the configuration that NT Dinte 77 interpreted as individualised strategies and possible concentrated misallocation. It differs from a dependent contributor (I-2), which also gains from others' losses but passes forward at least as much as it receives (φ ≥ 1). Isolation is defined by the balance at the node rather than by rank, because in dense networks almost every receiver also sends substantial synergy.

The two roles define the most specific policy questions in the framework. At a bridge, the question is whether interrupting the transmission would prevent wider deterioration without sacrificing the upstream gains. At an isolated beneficiary, the question is whether the gains could be maintained with fewer losses elsewhere, or redistributed so that they reach other targets.

The repository computes all six roles and exports every interface measure, rank and context value, so membership can be audited and alternative cut-offs tested. Its Two-step interface view places improving nodes on one side and deteriorating nodes on the other, and moves towards the centre those with the largest two-step flows across the interface, so the interface roles can be read at a glance. Each role has its own border colour; a node with more than one role is drawn with nested borders, one per role, in the order of the table above. Force-directed layouts, by contrast, pull the two subsystems together whenever a target has strong links on both sides.

### 5.6 Link-share weighted version (IGES/JRC)

In literature-derived networks, a target can rank highly because many studies record its links rather than because those links are strong. NT Dinte 77 proposed a factor to flag this: each target's share of the links it sends or receives.

```latex
P_i = \frac{L_i}{\sum_{j=1}^{n} L_j}
```

The IGES/JRC procedure always produces a weighted version alongside the original, with its own workbook and figures. Sent measures (Colab, synergy and trade-off sent) are divided by the sent share, received measures (Neglect, trade-off and synergy received) by the received share, and bridge and relay flows by both; φ is unchanged. Roles, node sizes and Two-step positions are recomputed from the weighted measures. Shares are expressed relative to the mean (Pᵢ × n), so a target with the mean number of links keeps its value; this rescaling does not change any ranking.

The weighted version is a check, not a substitute. A comparison sheet reports original and weighted ranks for Colab and Neglect and flags the discrepancy the NT considered most serious: a target among the top contributors that enters the top of weighted Neglect. Roles that hold in both versions are stronger candidates for investigation. The SDG Index procedure has no weighted version: its links are estimated from data for every eligible pair, so literature coverage does not determine them.

## 6 Why the roles would matter: the policy rationale

If interface roles could be estimated validly, they would change the unit of attention. A target would matter not only because its performance is poor or its connections numerous, but because of the role its connections suggest. An improving target would deserve scrutiny if its gains coexisted with losses elsewhere; a deteriorating target would deserve attention beyond its own sector if it sat where deterioration enters or spreads. This would reverse the usual policy reading of network bridges. In a sign-based synergy network, a bridge between clusters is a point to strengthen. In a performance-based network, what links the improving and deteriorating subsystems are trade-offs, and the aim would be to interrupt the transmission while preserving the gains. Policy can create or redirect such links deliberately: a programme rule can tie family farming to school meals, as in Brazil, and a link that sustains an undesired bridge could in principle be redirected in the same way.

**At a transmission bridge**, an investigation would have to establish whether the incoming trade-off and the outgoing synergy belong to the same mechanism. Temporal ordering, sectoral evidence, institutional arrangements and alternative explanations would be examined together. A two-step path is not a transmission chain: its links may reflect distinct mechanisms, common trends or separate responses to external conditions. If a mechanism were supported, adjustment would aim to buffer the bridge, for instance by mitigating the displaced cost, so that upstream gains no longer spread losses downstream.

**At an isolated beneficiary**, the central question would be what sustains the improvement. Evidence might reveal dependence on resource concentration, displaced costs or another adverse process, or an association generated by a shared contextual change with no direct dependence. These possibilities call for different responses. Where dependence were supported, the aim would be to keep the gains with fewer losses elsewhere, or to connect the target to others so that its gains are shared.

**At a dependent contributor**, the trade-off would be sharper, because the node's gains also benefit other improving targets. Policy would have to weigh the losses upstream against the improvements the node spreads downstream.

No intervention would follow automatically from a node's position. The sequence the roles presuppose is: network analysis identifies configurations; substantive inquiry examines mechanisms; intervention design formulates feasible adjustments; evaluation tests their effects. The first step carries the weight of the others. It requires that the links and roles reflect relationships between targets rather than properties of the series used to measure them. Section 7 tests whether that requirement can be met with the indicators currently available.

## 7 Statistical tests

The roles of Section 5 are only as good as the links they are built on. This section asks whether correlations between national indicator series, as they are published today, can support those links. It applies the framework to Brazil with four sources and two procedures, repeats the analysis for Finland and Norway, and subjects every network to the same tests. The concern throughout is the SDG Index, whose normalised indicator scores are the most complete national series available and the easiest to misread as measurements of change.

### 7.1 Data and designs

Finland and Norway were chosen because their national statistical systems are among the best rated by the World Bank's Statistical Performance Index (Dang et al., 2023), which the SDG Index reports under target 17.18. Norway has the highest score in the value used by the 2026 edition (94.1 in 2024, first of 187 countries). Finland was among the five highest every year from 2016 to 2023, first in 2020, and over 2016–2024 shares with Sweden the highest mean score. Brazil ranks 54th in 2024. If the results for Brazil reflected the weakness of one statistical system, they should not hold for these two countries. Four sources were used for each country:

- **SDG Index, normalised scores.** The 101 indicator scores supplied by the Sustainable Development Report for each country, 2000–2025, as used by the SDG Index procedure (Section 4.1).
- **SDG Index, raw values.** The raw indicator values of the SDR 2026 database. Only indicators with at most six missing years in 2000–2025, and no run of more than three, were kept: 50 of the 101 for Brazil, 52 for Finland and 51 for Norway. Gaps were filled with the IGES/JRC compound-growth rule, and the normative sign of each indicator was taken from the SDR codebook.
- **UN series.** One aggregate series per target from the UN SDG Global Database, 2010–2023, under the same completeness rule, keeping only observations reported by the country (excluding modelled, estimated and global-monitoring values). Ordinal and binary series were excluded. Normative directions were assigned to the series without an official one: first to those used for Brazil, then to 38 further series, mostly donor flows, waste, vaccination and occupational injuries, whose intended direction is unambiguous. The result covers 34 targets for Brazil and 33 each for Finland and Norway.
- **IGES/JRC procedure.** The package's IGES/JRC procedure run unchanged on UNSD data for each country: inventory pairs, compound-growth filling, Pearson correlation, p < 0.10, classification by normative direction and performance.

Each network was built twice: with correlations between levels, as in all procedures discussed in Section 3, and with correlations between year-on-year changes, which remove the common trend. Two tests were applied to every network. Phase-shuffled surrogates replace each series by an independent series with the same power spectrum and autocorrelation (Ding et al., 2026); the share of pairs that pass the significance filter among surrogates is the share produced by persistence alone, with no relationship between targets. A null model rewires the network at random while keeping each node's performance direction, its numbers of sent and received links and the weights; roles that reappear in the rewired networks owe nothing to who is linked to whom. Role stability was also compared across correlation coefficients, time windows and selection rules. The null model used the cut-off of three per role adopted in Section 5; the stability tests used a cut-off of ten, which is more favourable to stability.

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

In levels, series with no relationship to one another pass the filter in 24% to 50% of pairs, against a nominal 10%. Between half and four fifths of the observed links are therefore what the persistence of the series alone would produce. Finland and Norway have lower observed shares than Brazil, but their surrogates still pass the filter in 24% to 45% of pairs. Tightening the threshold does not remove the problem. For Brazil's SDG Index scores, independent surrogates pass p < 0.01 in 26% of pairs and p < 0.001 in 14%, roughly 140 times the nominal rate. Spearman's coefficient behaves like Pearson's (47.5% of surrogate pairs pass p < 0.10), because two monotonic series are always ranked alike. The problem lies in a significance test that treats annual observations of trending series as independent, not in the linearity of the coefficient or in the level of the threshold.

In changes, surrogates return to the nominal rate, and what remains is co-movement: 4 to 12 percentage points above chance in Brazil, and no more in Finland and Norway (1 to 9 points). At most a few dozen genuine associations are mixed among the hundreds that pass, with no way of telling which they are. The largest excess, in the IGES/JRC procedure, is partly produced by its own filling rule: within a stretch filled at a constant compound rate, annual changes are almost constant, and two filled stretches covering the same years correlate by construction.

### 7.3 Roles follow degree and direction

In the SDG Index network, the degree sequence alone fixes about 70% of the arcs in Brazil and about 60% in Finland and Norway: at densities of 0.51, 0.37 and 0.38, no rewiring moves more than 31% to 40% of them. The number of links of each indicator correlates with the linearity of its own trend (Spearman 0.63 between degree and time R² in Brazil, 0.84 in Finland and 0.76 in Norway), and in all three countries the three transmission bridges are among the ten deteriorating indicators with the most linear trends. In the rewired networks, the bridges reappear far more often than chance would allow. Mean Jaccard similarity with the observed set is 0.43 (Brazil), 0.44 (Finland) and 0.28 (Norway) with normalised scores, 0.41, 0.42 and 0.58 with raw values, and 0.59, 0.55 and 0.53 in the IGES/JRC procedure, against 0.06 to 0.10 for two random choices of three among the deteriorating targets (0.13 to 0.30 in the smaller raw-value networks). Only two of the 27 bridges, one in Finland's raw-value network and one in Norway's IGES/JRC network, have a bridge flow above the null distribution. A bridge, in these data, is a deteriorating indicator with a strong linear trend and many links. Some contributors and dependent contributors exceed the null, but they change with the window, the coefficient and the basis.

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

Roles on the deteriorating side, bridges above all, are more stable across specifications than those on the improving side only because they track direction and degree, which change little between specifications. With the cut-off of three, similarity falls further: between levels and changes it is zero for bridges in all three countries. When trend is removed, the order of the bridges changes as well: in Brazil, between levels and changes, the rank correlation of bridge flow among the raw-value bridges is 0.20, not significant. The Benjamini–Hochberg correction changes almost nothing, because nearly every pair is already highly significant in levels.

### 7.4 Properties of the indicators

Several properties of the indicators, rather than of the method, account for these results, and they weigh most on the SDG Index.

- **Carried values.** In the normalised SDG Index scores, the median series has 9 of its 25 annual changes equal to zero in Brazil, 15 in Finland and 14 in Norway: missing years are filled with the previous value. These steps add trend to levels and remove information from changes.
- **Bounds.** Normalised scores are capped at 0 and 100. Indicators that reach a bound become constant, so their direction depends on the measure chosen rather than on the country's performance: inequality (Palma ratio), educational attainment and freshwater withdrawal are improving by their raw values and stable by their scores.
- **Coverage.** About half of the SDG Index indicators do not meet a completeness rule of at most six missing years in 2000–2025 with no run of more than three, in Finland and Norway as in Brazil. In Brazil, the excluded include three of the ten bridges and two of the three exposed targets of the main specification with a cut-off of ten, whose normalised series consist largely of carried values. In the UN database, only 38 to 39 targets per country have an aggregate series reported by the country over 2010–2023, in Brazil as in Finland and Norway, and only 33 or 34 have one whose intended direction is unambiguous.
- **Linearised and modelled series.** The national Red List Index is the global index weighted by each species' share of range in the country, linearly interpolated between assessments and extrapolated beyond them. It ranks at or near the top of trade-off degree in every source for Brazil, and is a bridge in Norway's raw-value network and an exposed target in Finland's. Child stunting in the UN database is a modelled estimate rising almost linearly (time R² 0.95) and takes the same position when the Red List is removed. Such series are close to straight lines by construction and correlate with any other trending series.
- **Steps, scores and flows.** What remains after excluding modelled values includes series that change once and stay flat, ordinal scores, and official development assistance received, which fluctuates without trend and measures the country's performance poorly. These series dominate the networks of annual changes.

### 7.5 Significance, direction and inventories

The IGES tool accepts any correlation coefficient, whatever its significance (Zhou and Moinuddin, 2017). Removing the filter in the package's IGES/JRC procedure for Brazil adds 627 arcs (from 1,486 to 2,113), with a median |r| of 0.17 against 0.71 among the significant ones; 372 of them become trade-offs. In Finland and Norway it adds 447 and 521 arcs, with median |r| of 0.19 and 0.18 against 0.62 and 0.69, of which 224 and 246 become trade-offs. Their sign carries no information, since a coefficient that cannot be distinguished from zero cannot be called positive or negative. Bridges change little (Jaccard 1 in Brazil and Finland, 0.5 in Norway), because the strong links, which pass the filter easily, determine them. The absence of a filter is indefensible, but its presence does not rescue the method: the links that pass are the ones Section 7.2 shows to be largely persistence.

The direction of links fares no better. Lagged and conditional tests orient in a single direction fewer than half of the significant pairs in the raw-value networks (49% in Brazil and Finland, 47% in Norway), and those tests rest on the same trending series. Without direction, the framework loses the distinction between origin and destination that gives bridges and contributors their meaning. Read without direction, ranking pairs by the trade-off degree of each end and the strength of the tie, the networks single out targets that the directed roles leave out, either because the lagged tests mark them as origins of cost or because they split their trade-offs between received and sent; and the highest-ranked pairs are nearly tied in levels. Inventories do not solve the problem either. They restrict which pairs are examined, but the IGES/JRC networks show the same persistence and the same dependence of roles on degree and direction.

### 7.6 What the tests allow

With the indicators as they are published and available today, in Brazil as in the two countries whose statistical systems are among the best rated, correlation between national annual series cannot support valid inference about interlinkages between SDG targets, and network analysis built on such correlations cannot identify roles. In levels, the links are mostly trend and persistence, and the roles follow from each indicator's direction and the linearity of its trend; in changes, the signal is small, mixed with chance and indistinguishable from the artefacts of filling, carried values and bounded scales. This holds for sign-based classification and for the performance-based classification proposed here, for literature-restricted and data-driven pair selection, with and without significance filters, and with Pearson or Spearman coefficients. The performance-based reading of synergies and trade-offs remains a conceptual requirement for any interlinkage analysis. What the tests rule out is estimating it from correlations between the series currently available.

## 8 Other uses of the open implementation

The implementation remains useful beyond the roles, above all as an instrument of verification.

**An open, end-to-end pipeline.** A single run collects observations from the official UNSD SDG API (or reads the SDG Index workbooks), selects and completes series, estimates associations, applies the evidence and reclassification rules, selects roles and exports workbooks and figures. It is available as a browser application and from the command line. Every intermediate decision is recorded: the evidence behind each arc, excluded and reclassified links, and every interface measure. The IGES tool, by contrast, is offered as a visualisation whose processing steps, expert-consultation procedures and intended use in decision-making are not documented to the same degree (Desiderá Neto et al., 2025). Openness allows the procedure to be replicated, scrutinised and changed.

**Two sources of evidence and two ways of defining direction.** The IGES/JRC procedure takes the existence and orientation of links from literature inventories; the SDG Index procedure estimates both from data, with direction inferred from temporal tests. Applied to the same country, the two procedures allow the same tests to be run on literature-restricted and data-driven networks, as in Section 7, and expose links or directions supported by one source and not the other.

**Policy-created links.** Literature inventories record links that studies have found or experts expect. Some interlinkages, however, are created by policy decisions rather than by mechanisms the literature would predict. In Brazil, the National School Feeding Programme (PNAE) has required since 2009 that at least 30% of the federal funds it transfers be spent on food bought directly from family farming, a share raised to 45% from 2026 (Brasil, 2009, art. 14; Brasil, 2025). The rule ties family farming to school meals and, through them, to child nutrition. A filter that keeps only links supported by an apparent mechanism or a scientific study, such as evidence that more family farming reduces child malnutrition, would remove this synergy from the network and discard the information that a strong, significant association between the indicators could carry. Data-based networks keep such links; with indicators able to support inference, comparing them with literature-based ones could reveal interlinkages created by policy.

**Policy-intended links.** Brazil's Pluriannual Plan (PPA) 2024–2027 required those formulating each programme to state which SDG targets it contributes to. Mapping each programme's central target to the targets its formulators indicated yields a network of the links that policy expects to create. All technical programmes have been classified by SDG, from their components, justification, objectives and expected results, using a BERT-based SDG classification model (ods-brasil-bahia). These intended links do not depend on correlations between indicator series. They can be compared with the literature inventories now and, once indicators with more granularity and variance are available, with the associations those indicators show. The aim is to inform hypotheses to be considered in drafting the PPA 2028–2031.

**Other countries and regions.** The same procedures and tests run for 169 countries and 14 regions or aggregates in the SDG Index, and for UNSD countries and regions in the IGES/JRC procedure. Section 7 applies the tests to Finland and Norway, with the same results as for Brazil; applied to other countries, they can show how general those results are. The indicator properties behind them, carried values, bounds, interpolation and modelling, are features of the global databases rather than of one country.

**Transmission between countries.** Overlaying national networks could in principle help investigate whether performance in one country is associated with trade-offs in another, for instance through trade. Such a design would face the limits shown in Section 7 and would require bilateral data with more variance than national annual series.

## 9 Limitations

The tests of Section 7 have limits of their own.

- **Three countries.** The tests were run for Brazil, Finland and Norway. Other countries may differ, although the properties that drive the results are features of the global databases, and Finland and Norway are among the countries with the best-rated statistical systems.
- **Choices in the tests.** The completeness rules, the selection of one series per target, the exclusion of modelled, ordinal and binary series, and the normative directions assigned to UN series without an official one, first for Brazil's series and then for 38 further series, are choices; others are possible. The null model used a cut-off of three per role, as in Section 5, and the stability tests a cut-off of ten.
- **Power of the null model.** In dense networks the degree sequence leaves little room for rewiring, so the null model cannot move most arcs. This limits its power to separate structure from degree, and is itself part of the finding: at these densities there is little structure left to separate.
- **Corrections not applied.** Significance was not corrected for autocorrelation, and no predictive test was run. At current lengths, corrections remove most significance, and splitting the series for prediction leaves too few observations; both would weaken the remaining associations further.

None of these limits favours the use of correlation between the available series: each either restricts the scope of the tests to the data examined or would weaken the remaining associations further.

## 10 Conclusion

The commitment to leave no one behind expresses the mission of the 2030 Agenda as one of global synergy: progress is meant to be shared, not achieved by some at the expense of others.

The prestige of actors from developed countries has made the field permissive towards deep methodological fragilities, to the point that tools without any validity for inferring interlinkages or prioritising targets are officially recommended by the United Nations. This is one reflection, among several, of the trade-off that the Agenda ends up incorporating as a premise because it does not take as its central objective the gap that separates developed from developing countries in many dimensions.

The IGES tool justifies its use of correlation by restricting it to the sign and strength of relationships whose existence is assumed from the literature (Zhou and Moinuddin, 2017). Without significance, not even the sign means anything: a coefficient that cannot be distinguished from zero is neither positive nor negative, and the tool accepts any coefficient. With significance, Section 7 shows that the sign of correlations between these series reflects trend and persistence.

The JRC initiative is commendable. It records interaction types, directions, methods and contexts, including the cases where direction cannot be established. But the difference between its compilation and what the IGES tool presumes, both drawn from searches of the same literature (Section 3.4), is revealing of how much what enters a review defines its results.

The High-Level Political Forum cannot keep this indication in the toolkit it offers countries for preparing their Voluntary National Reviews. It induces error, and this is unacceptable because the interlinkage agenda is conceived as a path to support prioritisation and to accelerate the achievement of the goals.

The finding that the available series do not allow the application of network analysis is valid, and it produces a recommendation: to know synergies and trade-offs, other indicators, with more granularity and variance, need to be identified, created and collected.

At the same time, with the end date approaching, it is impossible not to stress that the fundamental interlinkage of the Agenda needs no goal, target, data, indicator, network, metrics or roles to be pointed out. That interlinkage is the maintenance of the trade-off of unequal development, without the status of a guiding goal for the whole Agenda, in an Agenda that intends to leave no one behind. If past exploitation is only condemned morally in the present, the inequality it produced, enjoyed in the present through unequal access to resources and well-being, will go on evidencing effective complicity with the past. The fallacy of the humanist appeal must be eliminated before any synergy can be expected from a global agenda.

## Data and code availability

The implementation, operational inputs, regression tests and methodological documentation are available at [github.com/netodowalter/SDG\_Interlinkages](https://github.com/netodowalter/SDG_Interlinkages). The same Python service runs a Gradio application, a command-line interface and a Python API. Each run exports full and summary workbooks, node and edge tables, an *Adverse cases* record of excluded and reclassified links, an Interface\_measures sheet with every role measure, rank and context value, and network images, including the Two-step interface view. IGES/JRC runs also export the link-share weighted workbook and figures, identified by the suffix \_pond. Replication should record the repository revision, data release, geographic coverage, analysis period and analytical settings.

**\[Author check: archive the release used in this article on Zenodo and cite its DOI here. The hosted application currently runs at ods-interlinkages-global.wdneto.chatgpt.site; a persistent address is preferable for a journal article.\]**

## Appendix: Operational criteria

| Element | IGES/JRC procedure | SDG Index procedure |
| --- | --- | --- |
| Analytical period | 2000–2025 | 2000–2025 |
| Series selection | Most distinct original numeric years; ties by IGES order | Component scores as supplied |
| Gap filling | CAGR from positive endpoint pairs (constant zero for two zero endpoints); bounds on generated values | None (supplied series may contain carried or interpolated values) |
| Shared series | One representative target | Distinct indicators mapped to one target keep distinct node IDs |
| Pair exclusions | — | Same goal or same target |
| Association | Pearson, p ≤ 0.10 | Pearson and/or Spearman, ≥ 8 matched observations, nonzero r, p < 0.10 |
| Orientation | IGES/JRC evidence rules, each direction evaluated separately (Section 3.4) | Lagged and conditional tests, both p < 0.10; otherwise two arcs |
| Trend | Linear, ≥ 3 distinct years; negligible change = stable | Same |
| Reclassification | Exclude discordant link if min R² < 0.10, or min R² < 0.20 and \|r\| < 0.40; otherwise reclassify | Same |
| Rankings | Top 10 positive values within direction, exact ties at position 10 included | Top 10 positive values within direction, ties resolved by stable node ID |
| Interface measures | Links between nodes with defined directions only | Same |
| Isolation | φ < 1 among top receivers R | Same |
| Context | Semantic ambitiousness, reported for every role | Years to target or to zero, reported for every role |
| Precedence | One role per node; D-2 over D-3 and D-1 | Same |

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

Yuan, Z., Gao, X., Liu, X., Feng, Y., & Zhang, L. (2026). Progress, trade-offs, and synergies of sustainable development goals in China's urban agglomerations. *Humanities and Social Sciences Communications*. https://doi.org/10.1057/s41599-026-07960-z

Zhou, X., & Moinuddin, M. (2017). *Sustainable Development Goals interlinkages and network analysis: A practical tool for SDG integration and policy coherence*. IGES Research Report RR1602. Institute for Global Environmental Strategies. https://www.iges.or.jp/en/pub/sustainable-development-goals-interlinkages/en

Zhou, X., & Moinuddin, M. (2021). Impacts and implications of the COVID-19 crisis and its recovery for achieving sustainable development goals in Asia: A review from an SDG interlinkage perspective. Book chapter, Elsevier. https://doi.org/10.1016/B978-0-323-85512-9.00018-8
