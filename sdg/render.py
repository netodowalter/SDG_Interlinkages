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


# Borders retain the same category meaning in all three views.
BORDER_COLORS = ['#ffffff', '#f2c500', '#888888', '#d71920']
PLOT = (80, 215, 3120, 1760)


def components(ids, edges):
    adjacency = {i: set() for i in ids}
    for e in edges:
        adjacency[e['source']].add(e['target'])
        adjacency[e['target']].add(e['source'])
    remaining = set(ids)
    result = []
    while remaining:
        pending = [min(remaining)]
        remaining.remove(pending[0])
        group = []
        while pending:
            node = pending.pop()
            group.append(node)
            following = sorted(adjacency[node] & remaining)
            remaining.difference_update(following)
            pending.extend(following)
        result.append(sorted(group))
    return sorted(result, key=lambda group: (-len(group), group[0]))


def component_cells(groups, box):
    # Recursively allocate area to connected components. The gap is a display
    # convention; distances between disconnected components are not a metric.
    if len(groups) == 1:
        return [(groups[0], box)]
    total = sum(map(len, groups))
    cut = min(range(1, len(groups)), key=lambda k: abs(sum(map(len, groups[:k])) - total/2))
    ratio = sum(map(len, groups[:cut])) / total
    x0, y0, x1, y1 = box
    if x1-x0 >= y1-y0:
        split = x0 + (x1-x0)*ratio
        left, right = (x0,y0,split-16,y1), (split+16,y0,x1,y1)
    else:
        split = y0 + (y1-y0)*ratio
        left, right = (x0,y0,x1,split-16), (x0,split+16,x1,y1)
    return component_cells(groups[:cut], left) + component_cells(groups[cut:], right)


def overlaps(xy, ids, sizes, padding=18):
    for a, node in enumerate(ids):
        for other in ids[a+1:]:
            required = (sizes[node]+sizes[other])/2 + padding
            delta = np.abs(xy[node]-xy[other])
            if delta[0] < required-0.1 and delta[1] < required-0.1:
                return True
    return False


def grid_positions(ids, xy, sizes, box):
    # Guaranteed readable fallback for unusually dense components. Preserve
    # rough left-to-right / top-to-bottom order from the force layout.
    x0,y0,x1,y1 = box
    step = max(sizes[i] for i in ids) + 20
    if x1-x0 < step:
        return None
    columns = max(1, int((x1-x0)//step))
    rows = int(np.ceil(len(ids)/columns))
    if rows*step > y1-y0:
        return None
    ordered = sorted(ids, key=lambda i: (round(xy[i][1]/step), xy[i][0], i))
    return {i: np.array([x0+(col+.5)*(x1-x0)/columns,
                         y0+(row+.5)*(y1-y0)/rows])
            for index,i in enumerate(ordered) for row,col in [divmod(index,columns)]}


def positions(nodes, edges, sizes=None, bounds=PLOT):
    sizes = sizes or {i: 60 for i in nodes}
    if not nodes:
        return {}
    result = {}
    for ids, box in component_cells(components(nodes, edges), bounds):
        index = {n: i for i,n in enumerate(ids)}
        count = len(ids)
        attraction = np.zeros((count,count))
        for e in edges:
            if e['source'] in index and e['target'] in index:
                a,b = index[e['source']],index[e['target']]
                attraction[a,b] = attraction[b,a] = max(attraction[a,b], .15+abs(e['weight']))
        xy = np.random.default_rng(42).uniform(-1,1,(count,2))
        k = 2/np.sqrt(count)
        for step in range(220):
            delta = xy[:,None]-xy[None,:]
            dist = np.maximum(np.linalg.norm(delta,axis=2), .015)
            force = ((k*k/dist**2-attraction*dist/k)[:,:,None]*delta).sum(axis=1)
            xy += force/np.maximum(np.linalg.norm(force,axis=1)[:,None],.01)*(.09*(1-step/220))
        x0,y0,x1,y1 = box
        half = np.array([sizes[i]/2+10 for i in ids])
        span = np.maximum(np.ptp(xy,axis=0),.01)
        margin = max(half)
        normalized = (xy-xy.min(axis=0))/span
        if count > 10:
            # Spread dense centers without letting a few force-layout outliers
            # shrink the other icons into a small corner of the canvas.
            for axis in (0,1):
                order = np.argsort(xy[:,axis],kind='stable')
                quantiles = np.empty(count)
                quantiles[order] = np.linspace(0,1,count)
                normalized[:,axis] = .7*quantiles + .3*normalized[:,axis]
        xy = normalized * np.maximum([x1-x0-2*margin,y1-y0-2*margin],0) + [x0+margin,y0+margin]
        if count == 1:
            xy[0] = [(x0+x1)/2,(y0+y1)/2]
        # Separate bounding squares, including border and label safety margin.
        for iteration in range(300):
            changed = False
            for a in range(count):
                for b in range(a+1,count):
                    delta = xy[b]-xy[a]
                    gap = (sizes[ids[a]]+sizes[ids[b]])/2 + 18 - np.abs(delta)
                    if np.all(gap > 0):
                        axis = int(np.argmin(gap))
                        shift = (gap[axis]/2+.1) * (1 if delta[axis]>=0 else -1)
                        xy[a,axis] -= shift
                        xy[b,axis] += shift
                        changed = True
            xy[:,0] = np.clip(xy[:,0],x0+half,x1-half)
            xy[:,1] = np.clip(xy[:,1],y0+half,y1-half)
            if not changed:
                break
        local = dict(zip(ids,xy))
        if overlaps(local,ids,sizes) or any(x1-x0 < 2*h or y1-y0 < 2*h for h in half):
            local = grid_positions(ids,local,sizes,box)
            if local is None:
                fallback = grid_positions(nodes,{**result,**dict(zip(ids,xy)),
                    **{i:np.zeros(2) for i in nodes if i not in result and i not in ids}},sizes,bounds)
                if fallback is None:
                    raise ValueError('Too many nodes for a readable PNG canvas.')
                return fallback
        result.update(local)
    return result


def edge_color(edge, nodes):
    backwards = nodes[edge['source']]['direction'] == 'backward'
    base = (153,0,51) if (edge['interaction']=='trade-off') != backwards else (51,51,51)
    return tuple(round(255*.65+v*.35) for v in base) if backwards else base


def legend(draw, dataset):
    y = 1830
    draw.line((70,y-24,3130,y-24),fill='#cbd5da',width=2)
    draw.text((70,y), 'LINK COLOR',font=font(24),fill='#163b49')
    links = [((51,51,51),'Synergy: non-regressing source'),((153,0,51),'Trade-off: non-regressing source'),
             ((184,184,184),'Trade-off from regression'),((219,166,184),'Backward synergy')]
    for x,(color,label) in zip((310,1000,1730,2440),links):
        draw.line((x,y+14,x+70,y+14),fill=color,width=6)
        draw.polygon([(x+70,y+14),(x+57,y+7),(x+57,y+21)],fill=color)
        draw.text((x+86,y),label,font=font(23),fill='#334455')
    y += 73
    draw.text((70,y), 'ICON BORDER',font=font(24),fill='#163b49')
    labels = ['Fast-achieving collaborators','Dependent collaborators','Resilient neglected indicators','Propagating neglected indicators']
    if dataset != 'SDGIndex':
        labels[0] = 'High-ambition collaborators'
        labels[2] = 'Low-ambition neglected targets'
    for j,(color,label) in enumerate(zip(BORDER_COLORS,labels)):
        x = 310 if j%2==0 else 1730
        yy = y+(j//2)*62
        draw.rectangle((x,yy,x+32,yy+32),fill=color,outline='#536067',width=2)
        draw.text((x+50,yy+2),label,font=font(24),fill='#334455')
    draw.text((70,2070),'Black border: other indicators. Highlights use the same four groups in every view.',font=font(23),fill='#465b63')
    draw.text((70,2110),'Link thickness: |r|. Links from regression use 35% opacity. Component spacing is optimized for readability.',font=font(23),fill='#465b63')


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
                scores = {i: nodes[i]['colab'] if nodes[i]['direction']=='forward' else
                          nodes[i]['neglect'] if nodes[i]['direction']=='backward' else 0 for i in ids}
            tiers = {i: categories.get(i,-1) for i in ids}
            extent = defaultdict(list)
            for i in ids:
                extent[tiers[i]].append(scores[i])
            ranges = {0:(58,68), 1:(66,76), 2:(58,68), 3:(66,76), -1:(44,56)}
            sizes = {i:int(scale(scores[i],min(extent[tiers[i]]),max(extent[tiers[i]]),*ranges[tiers[i]])) for i in ids}
            xy = positions(ids,edges,sizes)
            weights = [abs(e['weight']) for e in edges]
            low, high = min(weights), max(weights)
            partners = {(e['source'],e['target']) for e in edges}
            for e in edges:
                a,b = e['source'],e['target']
                color = edge_color(e,nodes)
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
            colors = BORDER_COLORS
            for i in sorted(ids,key=lambda i:sizes[i]):
                node = nodes[i]; size = sizes[i]; x,y = map(int,xy[i]); tier = tiers[i]
                border = colors[tier] if 0 <= tier < 4 else 'black'
                left,top = x-size//2,y-size//2
                margin = 5 if tier>=0 else 1
                draw.rectangle((left-margin,top-margin,left+size+margin,top+size+margin),fill=border,outline='#536067')
                target = node.get('target') or i
                with Image.open(Path(icons)/f"{int(target.split('.')[0]):02}.png") as icon:
                    image.paste(icon.resize((size,size), Image.Resampling.LANCZOS),(left,top))
                label_font = font(max(13,size//4))
                while draw.textbbox((0,0),target,font=label_font)[2] > size-6:
                    label_font = font(label_font.size-1)
                draw.text((x,y+size*.17),target,anchor='mm',fill='white',stroke_width=1,stroke_fill='#263238',font=label_font)
        legend(draw,graph.get('dataset','IGES_JRC'))
        image.save(folder / f"{prefix}_{mode}.png")
