'Export network PNGs without a browser or graphics server.'
from collections import defaultdict
from math import atan2, cos, sin
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def font(size):
    for name in ('DejaVuSans-Bold.ttf', 'arialbd.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def scale(value, lo, hi, small, large):
    return (small + large) / 2 if lo == hi else small + (large-small)*(value-lo)/(hi-lo)


def positions(nodes, edges):
    # Force-directed layout with a fixed seed for reproducible figures.
    index = {n: i for i, n in enumerate(nodes)}
    count = len(nodes)
    attraction = np.zeros((count, count))
    for e in edges:
        a, b = index[e['source']], index[e['target']]
        attraction[a, b] = attraction[b, a] = max(attraction[a, b], .15 + abs(e['weight']))
    xy = np.random.default_rng(42).uniform(-1, 1, (count, 2))
    k = 2 / np.sqrt(count)
    for step in range(220):
        delta = xy[:, None] - xy[None, :]
        dist = np.maximum(np.linalg.norm(delta, axis=2), .015)
        force = ((k*k/dist**2 - attraction*dist/k)[:, :, None] * delta).sum(axis=1)
        xy += force / np.maximum(np.linalg.norm(force, axis=1)[:, None], .01) * (.09*(1-step/220))
    bounds = np.ptp(xy, axis=0)
    xy = (xy - (xy.max(axis=0)+xy.min(axis=0))/2) * min(2950/max(bounds[0], .01), 1850/max(bounds[1], .01))
    return dict(zip(nodes, xy + [1600, 1130]))


def render_networks(folder, prefix, title, graph, groups, icons):
    nodes = {n['id']: n for n in graph['nodes']}
    categories = {row[1]: i for i, g in enumerate(groups) for row in g['rows']}
    for mode, label in [('full', 'Progress and regression'), ('synergy', 'Synergies'), ('trade-off', 'Trade-offs')]:
        edges = [e for e in graph['edges'] if mode == 'full' or e['interaction'] == mode]
        ids = sorted({e[k] for e in edges for k in ('source', 'target')})
        image = Image.new('RGB', (3200, 2240), 'white')
        draw = ImageDraw.Draw(image)
        draw.text((66, 34), f"{title}   /   {label}", font=font(47), fill='#163b49')
        draw.text((70, 105), f"{len(ids)} nodes   ·   {len(edges)} arcs   ·   {prefix}", font=font(26), fill='#465b63')
        if not ids:
            draw.text((100, 400), 'No links in this view.', font=font(36), fill='#334455')
        else:
            scores = defaultdict(float)
            for e in edges:
                a, b, w = e['source'], e['target'], abs(e['weight'])
                if mode == 'synergy':
                    scores[a] += w
                    scores[b] += w * {'forward': 1, 'backward': -1}.get(nodes[a]['direction'], 0)
                elif mode == 'trade-off':
                    scores[b] += w * (nodes[a]['direction'] == 'forward')
                    scores[a] += w * (nodes[b]['direction'] == 'forward')
            if mode == 'full':
                scores = {i: nodes[i]['colab'] if nodes[i]['direction'] == 'forward' else
                          nodes[i]['neglect'] if nodes[i]['direction'] == 'backward' else 0 for i in ids}
                tiers = {i: categories.get(i, -1) for i in ids}
            else:
                direction = 'forward' if mode == 'synergy' else 'backward'
                eligible = sorted((scores[i] for i in ids if nodes[i]['direction'] == direction), reverse=True)
                cutoff = eligible[min(9, len(eligible)-1)] if eligible else float('inf')
                tiers = {i: 4 if nodes[i]['direction'] == direction and scores[i] >= cutoff else -1 for i in ids}
            extent = defaultdict(list)
            for i in ids:
                extent[tiers[i]].append(scores[i])
            ranges = {0:(65,75), 1:(85,100), 2:(65,75), 3:(85,100), 4:(80,100), -1:(20,50 if mode=='full' else 60)}
            sizes = {}
            for i in ids:
                values = extent[tiers[i]]
                sizes[i] = int(scale(scores[i], min(values), max(values), *ranges[tiers[i]]))
            xy = positions(ids, edges)
            weights = [abs(e['weight']) for e in edges]
            low, high = min(weights), max(weights)
            partners = {(e['source'],e['target']) for e in edges}
            for e in edges:
                a,b = e['source'],e['target']
                backwards = nodes[a]['direction'] == 'backward'
                base = (153,0,51) if (e['interaction'] == 'trade-off') != backwards else (51,51,51)
                color = tuple(round(255*.65 + v*.35) for v in base) if backwards else base
                dx,dy = xy[b]-xy[a]
                angle = atan2(dy,dx)
                ux,uy = cos(angle),sin(angle)
                # Offset reciprocal arcs so both arrowheads remain visible.
                offset = 4 if (b,a) in partners else 0
                end = xy[b] - np.array([ux,uy])*((sizes[b]/2+6)/max(abs(ux),abs(uy))) + np.array([-uy,ux])*offset
                start = xy[a] + np.array([-uy,ux])*offset
                width = round(scale(abs(e['weight']),low,high,1,5))
                draw.line([tuple(start),tuple(end)],fill=color,width=width)
                back = end - np.array([ux,uy])*(7+width)
                normal = np.array([-uy,ux])*(3+width/2)
                draw.polygon([tuple(end),tuple(back+normal),tuple(back-normal)],fill=color)
            colors = ['white','#f2c500','#888888','#d71920']
            for i in sorted(ids,key=lambda i:sizes[i]):
                node = nodes[i]; size = sizes[i]; x,y = map(int,xy[i]); tier = tiers[i]
                border = colors[tier] if 0 <= tier < 4 else ('white' if node['direction']=='forward' else '#d71920') if tier==4 else 'black'
                left,top = x-size//2,y-size//2
                margin = 5 if tier>=0 else 1
                draw.rectangle((left-margin,top-margin,left+size+margin,top+size+margin),fill=border,outline='#536067')
                target = node.get('target') or i
                with Image.open(Path(icons)/f"{int(target.split('.')[0]):02}.png") as icon:
                    image.paste(icon.resize((size,size), Image.Resampling.LANCZOS),(left,top))
                draw.text((x,y+size*.17),target,anchor='mm',fill='white',stroke_width=1,stroke_fill='#263238',font=font(max(11,size//4)))
        draw.text((70,2140), 'Thickness is proportional to |r|. Sources in regression use the opposite interaction color at 35% opacity.', font=font(24), fill='#334455')
        image.save(folder / f"{prefix}_{mode}.png")
