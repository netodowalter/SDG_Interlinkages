"""Figure 1 of the methodological article: interface roles illustrated with Brazil.

Usage: python scripts/figure1_brazil.py   (writes docs/figures/figure1_interface_roles.png)

Values come from the SDG Index procedure for Brazil (data/SDGIndex, normalised scores, 2000-2025,
Pearson in levels, p < 0.10, roles with ROLE_TOP = 3), as computed by
sdgindex_country.analyze(): 2.2 obesity is the second-ranked transmission bridge
(T+ 35.9, B 7.5, bridge flow 268.5) and 8.5 unemployment the first-ranked isolated beneficiary
(R 2.98, S_o 1.25, phi 0.42). Arcs shown are the strongest of each kind at those nodes (|r|).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

IMP, DET = '#2B6CB0', '#C0392B'          # improving / deteriorating nodes
SYN, TRA = '#4A4A4A', '#D97706'           # synergy / trade-off arcs
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, ax = plt.subplots(figsize=(11, 7.6))
ax.set_xlim(0, 11); ax.set_ylim(0, 7.6); ax.axis('off')

# subsystem bands
ax.add_patch(Rectangle((0.1, 0.25), 5.3, 6.85, color='#EAF1FA', zorder=0))
ax.add_patch(Rectangle((5.6, 0.25), 5.3, 6.85, color='#FBECEA', zorder=0))
ax.text(2.75, 7.28, 'Improving subsystem (56 targets)', ha='center', color=IMP, fontsize=11, weight='bold')
ax.text(8.25, 7.28, 'Deteriorating subsystem (25 targets)', ha='center', color=DET, fontsize=11, weight='bold')
ax.plot([5.5, 5.5], [0.25, 7.1], color='#999999', lw=0.8, ls=(0, (2, 3)), zorder=0)

def node(x, y, label, col, key=False, w=2.05):
    h = 0.5 if not key else 0.62
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12',
                         fc='white' if not key else col, ec=col, lw=1.4 if not key else 2.2, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', fontsize=8.3 if not key else 9,
            color=col if not key else 'white', weight='bold' if key else 'normal', zorder=4, linespacing=1.15)

def arc(p, q, w, kind, label=None, rad=0.0, lx=0.5, dy=0.0):
    a = FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, lw=0.6 + 3.2 * w,
                        color=SYN if kind == 's' else TRA, ls='-' if kind == 's' else (0, (4, 2)),
                        connectionstyle=f'arc3,rad={rad}', shrinkA=2, shrinkB=2, zorder=2)
    ax.add_patch(a)
    if label:
        x = p[0] + (q[0] - p[0]) * lx; y = p[1] + (q[1] - p[1]) * lx + dy
        ax.text(x, y, label, fontsize=7.6, ha='center', va='center', color=SYN if kind == 's' else TRA,
                bbox=dict(fc='white', ec='none', pad=0.6), zorder=5)

# ---------- Panel A: transmission bridge (2.2 obesity) ----------
ax.text(0.25, 6.82, 'A  Transmission bridge (D-2)', fontsize=10, weight='bold', color='#222222')
B = (6.75, 5.25)
srcA = [((2.2, 6.25), '6.1 Basic drinking\nwater', 0.99), ((2.2, 5.25), '6.2 Basic\nsanitation', 0.99),
        ((2.2, 4.25), '9.c Internet use', 0.99)]
dstA = [((9.85, 6.25), '8.8 Labour rights\nguaranteed', 0.93), ((9.85, 5.25), '16.6 Timeliness of\nadmin. proceedings', 0.93),
        ((9.85, 4.25), '16.5 Corruption\nPerceptions Index', 0.88)]
for (xy, lab, w) in srcA:
    node(*xy, lab, IMP); arc((xy[0] + 1.05, xy[1]), (B[0] - 1.1, B[1]), w, 't', f'{w:.2f}', lx=0.42)
for (xy, lab, w) in dstA:
    node(*xy, lab, DET); arc((B[0] + 1.1, B[1]), (xy[0] - 1.05, xy[1]), w, 's', f'{w:.2f}', lx=0.62)
node(*B, '2.2 Obesity\n(adult prevalence)', DET, key=True, w=2.15)
ax.text(B[0] + 0.15, B[1] - 1.15, 'Bridge flow = T⁺ × B = 35.9 × 7.5 = 268.5\n2nd-ranked bridge; 54 trade-offs in, 11 synergies out',
        ha='center', va='top', fontsize=7.6, color='#444444')

# ---------- Panel B: isolated beneficiary (8.5 unemployment) ----------
ax.text(0.25, 3.32, 'B  Isolated beneficiary (I-3)', fontsize=10, weight='bold', color='#222222')
I = (4.3, 1.75)
srcB = [((8.9, 2.85), '13.2 GHG emissions\nembodied in imports', 0.64), ((8.9, 2.12), '12.4 Air pollution\nassociated with imports', 0.60),
        ((8.9, 1.39), '12.4 Nitrogen emissions\nassociated with imports', 0.56), ((8.9, 0.66), '6.4 Scarce water\nembodied in imports', 0.43)]
dstB = [((1.15, 2.5), '9.1 Rural all-season\nroads', 0.48), ((1.15, 1.75), '16.4 Exports of\nconventional weapons', 0.40),
        ((1.15, 1.0), '9.1 Logistics:\ninfrastructure', 0.37)]
for (xy, lab, w) in srcB:
    node(*xy, lab, DET, w=2.3); arc((xy[0] - 1.17, xy[1]), (I[0] + 1.1, I[1]), w, 't', f'{w:.2f}', lx=0.35)
for (xy, lab, w) in dstB:
    node(*xy, lab, IMP, w=1.95); arc((I[0] - 1.1, I[1]), (xy[0] + 1.0, xy[1]), w, 's', f'{w:.2f}', lx=0.5)
node(*I, '8.5 Unemployment\nrate', IMP, key=True, w=2.15)
ax.text(I[0] - 0.15, I[1] - 0.42, 'φ = Sₒ / R = 1.25 / 2.98 = 0.42\n1st-ranked isolated beneficiary; R also includes\nplastic waste exports (0.40) and CO₂ (0.35)',
        ha='center', va='top', fontsize=7.6, color='#444444')

# legend
ly = 0.02
ax.add_patch(FancyArrowPatch((0.3, ly + 0.1), (1.0, ly + 0.1), arrowstyle='-|>', mutation_scale=10, lw=2, color=SYN))
ax.text(1.08, ly + 0.1, 'synergy', va='center', fontsize=8)
ax.add_patch(FancyArrowPatch((2.0, ly + 0.1), (2.7, ly + 0.1), arrowstyle='-|>', mutation_scale=10, lw=2, color=TRA, ls=(0, (4, 2))))
ax.text(2.78, ly + 0.1, 'trade-off', va='center', fontsize=8)
ax.text(4.0, ly + 0.1, 'Arc width and label: |r| (Pearson, levels, p < 0.10). Strongest arcs of each kind shown.',
        va='center', fontsize=8, color='#444444')
fig.savefig('docs/figures/figure1_interface_roles.png', dpi=220, bbox_inches='tight', facecolor='white')
