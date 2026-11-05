"""Figure 1 of the methodological article: six roles illustrated with Brazil.

Usage: python scripts/figure1_brazil.py   (writes docs/figures/figure1_interface_roles.png)

Values come from the SDG Index procedure for Brazil (data/SDGIndex, normalised scores, 2000-2025,
Pearson in levels, p < 0.10, top 3 per role without exclusions or backfilling), as computed by
sdgindex_country.analyze():
  - Improvement sender:     9.c internet use (14.14), 1.2 poverty $4.20 (13.70), 1.1 poverty $3.00 (13.64)
  - Deterioration receiver: 2.2 obesity (35.88), 8.8 labour rights (31.01), 2.4 trophic level (29.16)
  - Deterioration sender:   15.5 Red List Index (32.74), 12.4 nitrogen emissions (30.07), 2.2 obesity (26.40)
  - Improvement receiver:   7.1 clean fuels (13.70), 4.6 literacy (12.11), 10.1 Gini (12.05)
  - Improvement relay:      5.6 family planning (60.63), 4.6 literacy (60.57), 6.1 drinking water (59.32)
  - Deterioration relay:    6.4 scarce water in imports (20.14), 8.8 labour rights (20.06), 15.5 Red List (18.02)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

IMP, DET = '#2B6CB0', '#C0392B'          # improving / deteriorating nodes
SYN, TRA = '#4A4A4A', '#D97706'           # synergy / trade-off arcs
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.8})
fig, ax = plt.subplots(figsize=(11.2, 8.2))
ax.set_xlim(0, 11.2); ax.set_ylim(0, 8.2); ax.axis('off')

# subsystem bands
ax.add_patch(Rectangle((0.1, 0.35), 5.35, 7.35, color='#EAF1FA', zorder=0))
ax.add_patch(Rectangle((5.75, 0.35), 5.35, 7.35, color='#FBECEA', zorder=0))
ax.text(2.78, 7.88, 'Improving subsystem I (56 indicators)', ha='center', color=IMP, fontsize=11, weight='bold')
ax.text(8.42, 7.88, 'Deteriorating subsystem D (25 indicators)', ha='center', color=DET, fontsize=11, weight='bold')
ax.plot([5.6, 5.6], [0.35, 7.7], color='#999999', lw=0.9, ls=(0, (2, 3)), zorder=0)

def node(x, y, label, col, key=False, w=2.2):
    h = 0.52 if not key else 0.62
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12',
                         fc='white' if not key else col, ec=col, lw=1.4 if not key else 2.2, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', fontsize=8.0 if not key else 8.6,
            color=col if not key else 'white', weight='bold' if key else 'normal', zorder=4, linespacing=1.15)

def arc(p, q, w, kind, label=None, rad=0.0, lx=0.5, dy=0.0):
    a = FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, lw=0.6 + 3.0 * w,
                        color=SYN if kind == 's' else TRA, ls='-' if kind == 's' else (0, (4, 2)),
                        connectionstyle=f'arc3,rad={rad}', shrinkA=2, shrinkB=2, zorder=2)
    ax.add_patch(a)
    if label:
        x = p[0] + (q[0] - p[0]) * lx; y = p[1] + (q[1] - p[1]) * lx + dy
        ax.text(x, y, label, fontsize=7.4, ha='center', va='center', color=SYN if kind == 's' else TRA,
                bbox=dict(fc='white', ec='none', pad=0.6), zorder=5)

# ---------- Panel A: I -> D interface (Improvement sender -> Deterioration receiver) ----------
ax.text(0.25, 7.42, 'A  Interface I → D: Improvement sender to Deterioration receiver', fontsize=9.6, weight='bold', color='#222222')
srcA = [
    ((2.2, 6.85), '9.c Internet use\n(#1 sender: 14.1)', 0.99, True),
    ((2.2, 6.00), '1.2 Poverty $4.20\n(#2 sender: 13.7)', 0.96, False),
    ((2.2, 5.15), '1.1 Poverty $3.00\n(#3 sender: 13.6)', 0.96, False),
]
dstA = [
    ((9.0, 6.85), '2.2 Obesity\n(#1 receiver: 35.9)', True),
    ((9.0, 6.00), '8.8 Labour rights\n(#2 receiver: 31.0)', False),
    ((9.0, 5.15), '2.4 Trophic level\n(#3 receiver: 29.2)', False),
]
for (xy, lab, _, is_key) in srcA:
    node(*xy, lab, IMP, key=is_key)
for (xy, lab, is_key) in dstA:
    node(*xy, lab, DET, key=is_key)

arc((3.32, 6.85), (7.88, 6.85), 0.99, 't', '0.99', lx=0.5)
arc((3.32, 6.85), (7.88, 5.15), 0.93, 't', '0.93', lx=0.35, dy=0.05)
arc((3.32, 6.00), (7.88, 6.85), 0.96, 't', '0.96', lx=0.65, dy=0.05)
arc((3.32, 5.15), (7.88, 6.00), 0.87, 't', '0.87', lx=0.5)

# ---------- Panel B: D -> I interface (Deterioration sender -> Improvement receiver) ----------
ax.text(0.25, 4.45, 'B  Interface D → I: Deterioration sender to Improvement receiver', fontsize=9.6, weight='bold', color='#222222')
dstB = [
    ((2.2, 3.88), '7.1 Clean fuels\n(#1 receiver: 13.7)', True),
    ((2.2, 3.03), '4.6 Literacy rate\n(#2 receiver: 12.1)', False),
    ((2.2, 2.18), '10.1 Gini index\n(#3 receiver: 12.0)', False),
]
srcB = [
    ((9.0, 3.88), '15.5 Red List Index\n(#1 sender: 32.7)', True),
    ((9.0, 3.03), '12.4 Nitrogen prod.\n(#2 sender: 30.1)', False),
    ((9.0, 2.18), '2.2 Obesity\n(#3 sender: 26.4)', False),
]
for (xy, lab, is_key) in dstB:
    node(*xy, lab, IMP, key=is_key)
for (xy, lab, is_key) in srcB:
    node(*xy, lab, DET, key=is_key)

arc((7.88, 3.88), (3.32, 3.88), 0.98, 't', '0.98', lx=0.5)
arc((7.88, 3.03), (3.32, 3.88), 0.96, 't', '0.96', lx=0.38, dy=-0.04)
arc((7.88, 3.88), (3.32, 3.03), 0.97, 't', '0.97', lx=0.62, dy=-0.04)
arc((7.88, 2.18), (3.32, 2.18), 0.89, 't', '0.89', lx=0.5)

# ---------- Panel C: Internal subsystem relays (Improvement relay & Deterioration relay) ----------
ax.text(0.25, 1.50, 'C  Internal subsystem relays: Improvement relay (within I) and Deterioration relay (within D)', fontsize=9.6, weight='bold', color='#222222')
node(1.45, 0.90, '5.6 Family planning\n(#1 I-relay: 60.6)', IMP, key=True, w=2.1)
node(4.15, 0.90, '4.6 Literacy (60.6)\n& 6.1 Water (59.3)', IMP, key=False, w=2.1)
arc((2.52, 0.98), (3.08, 0.98), 0.98, 's', '0.98', lx=0.5, dy=0.14)
arc((3.08, 0.82), (2.52, 0.82), 0.98, 's')

node(7.10, 0.90, '6.4 Scarce water\n(#1 D-relay: 20.1)', DET, key=True, w=2.1)
node(9.80, 0.90, '8.8 Rights (20.1)\n& 15.5 Red List (18.0)', DET, key=False, w=2.1)
arc((8.17, 0.98), (8.73, 0.98), 0.85, 's', '0.85', lx=0.5, dy=0.14)
arc((8.73, 0.82), (8.17, 0.82), 0.85, 's')

# legend
ly = 0.05
ax.add_patch(FancyArrowPatch((0.3, ly + 0.1), (1.0, ly + 0.1), arrowstyle='-|>', mutation_scale=10, lw=2, color=SYN))
ax.text(1.08, ly + 0.1, 'synergy (within I or D)', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((3.1, ly + 0.1), (3.8, ly + 0.1), arrowstyle='-|>', mutation_scale=10, lw=2, color=TRA, ls=(0, (4, 2))))
ax.text(3.88, ly + 0.1, 'trade-off (across I ↔ D)', va='center', fontsize=8)
ax.text(6.0, ly + 0.1, 'Arc width and label: |r| (Pearson, levels, p < 0.10). Top 3 per role shown.',
        va='center', fontsize=8, color='#444444')
fig.savefig('docs/figures/figure1_interface_roles.png', dpi=220, bbox_inches='tight', facecolor='white')
