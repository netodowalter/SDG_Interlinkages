# Two-step interface layout

## Purpose and scope

The **Two-step interface** is an additional view of the complete directed network. The existing complete, synergy and trade-off views remain available. This view changes positions only: it keeps all linked nodes and arcs, arrow directions, weights, interaction classifications, four highlight categories, icon-size rules and legends of the complete progress/regression view. It is available for SDGIndex and IGES/JRC, including newly calculated results.

Every interface PNG and the web view display:

> Note: This experimental layout is a more reader-friendly visual representation designed to place the study’s targets of interest more centrally in the network.

There are no separating lines, enclosing outlines or additional group labels.

## Display score

Use the final conceptual interaction type after the analysis has applied its exclusion and reclassification rules. Let each arc weight be its absolute coefficient. For each progressing or regressing node `i`:

1. `P(i)` is the sum of incoming trade-off weights whose source has the opposite progress direction.
2. `S(i)` is the sum of outgoing synergy weights whose destination has the same progress direction as `i`.
3. `M(i) = P(i) × S(i)`.

This product equals the sum of weight products over the relevant directed two-step channels `source → i → destination`. Self-arcs are excluded. The source is in the opposite direction group; `i` and the destination share a direction. Stable or undetermined directions do not contribute to these channels. Parallel recorded arcs, if present, each contribute their weight. A node missing either part has score zero.

The score is computed for all nodes, without consulting highlight colors. It is used only to arrange the drawing; it does not replace Colab, Neglect, time-to-target, ambition, category membership or any reported substantive ranking. Its alignment with dependent collaborators and propagating neglected nodes is partly expected from shared ingredients in those categories, and is not independent validation of them.

## Positioning

Within each direction, sort `M` in ascending order and assign average ranks to ties. Normalize as `(average_rank − 1) / max(1, cohort_size − 1)` to obtain `q`. Progressing nodes initially occupy the left half and regressing nodes the right half. Their horizontal coordinate, expressed as a fraction of the drawing width, is:

`x = 0.5 + sign × 0.46 × [0.10 + 0.90 × (1 − q)]`

where `sign = −1` for progression and `+1` for regression. Higher scores therefore approach the center from either side. A tied cohort occupies the same initial horizontal band; ties do not receive artificial score differences.

The vertical order follows the existing weighted force layout, with deterministic ID ordering for vertical ties, and is spread over 8%–92% of drawing height. The web implementation uses CoSE and the Python PNG renderer uses its existing seeded force layout; their vertical coordinates need not match pixel for pixel. Stable or undetermined nodes start near the upper center. If every display score is zero, the existing complete-network placement is retained.

For legibility, projected coordinates are assigned to separate rectangular slots, each at least the largest icon width plus 26 units apart. Nodes are placed by decreasing score with ID tie-breaking. Each chooses the nearest free slot using cost `4 × horizontal_displacement² + vertical_displacement²`, with both displacements normalized by the drawing dimensions. This favors preservation of horizontal placement while avoiding overlapping icons and their internal labels. A fixed-size Python PNG raises an explicit error if the available area cannot hold every icon readably. The web drawing can expand its coordinate space and is then fitted to the viewport. Positions can still be dragged manually in the webapp.

Neither coordinate axis, displayed distance nor the gap between direction groups is a statistical scale or evidence of a causal relationship. The diagram uses no inferred partition to classify nodes. It does not guarantee that every colored node is centrally placed: centrality here follows the channel score, not its border color.

## Implementation and verification

- Python: `sdg/two_step.py`, called by `sdg/render.py`; additional output suffix `_two_step_interface.png`.
- Web: `lib/two-step-interface.ts`, called from `components/NetworkPanel.tsx`; additional **Two-step interface** tab and PNG export.
- Both retain the existing complete-network scores, highlights and legend; the experimental note appears only in the additional view.
- Tests verify directed channel products, exclusion of irrelevant directions and self-arcs, unchanged graph contents/categories/sizes, and non-overlapping positions. The supplied Oceania runs are included in implementation smoke checks. Source data and analytical results do not need to be regenerated to select the additional view.
