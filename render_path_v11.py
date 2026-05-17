import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle
import numpy as np
import json

# Load data
with open('/home/cyberdog_sim/src/Option_One/地图与路径/关键节点.json', 'r') as f:
    nodes = json.load(f)['节点']
nodes_by_id = {n['id']: n for n in nodes}

# Traversal order
traversal = [
    1, 2, 3, 31, 32, 6, 5, 4, 33, 34, 7, 8, 9, 11, 10, 12, 20, 19, 28, 13,
    14, 13, 28, 30, 16, 30, 29, 15, 17, 18, 15, 29, 20, 12, 21, 22, 23, 24,
    25, 27, 26, 27
]

fig, ax = plt.subplots(1, 1, figsize=(10, 32))
ax.set_xlim(-1.5, 5.5)
ax.set_ylim(-1.5, 17)
ax.set_aspect('equal')
ax.set_xlabel('X (m)', fontsize=12)
ax.set_ylabel('Y (m)', fontsize=12)
ax.set_title('Cyberdog Track v11 — 42-Stage Sharp Path (no smoothing)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.25, linestyle='--')

# ========== TRACK ELEMENTS ==========
for xr, yr in [((-0.73, 3.49), (-0.63, 6.67)),
               ((-0.74, 3.49), (6.55, 12.16)),
               ((-0.74, 3.48), (12.05, 15.78))]:
    ax.add_patch(Rectangle((xr[0], yr[0]), xr[1]-xr[0], yr[1]-yr[0],
                           lw=2, ec='#FFD700', fc='#FFD700', alpha=0.08))

ax.add_patch(Rectangle((0.60, -0.52), 1.80, 1.00, lw=1, ec='#8B4513', fc='#A0522D', alpha=0.30, hatch='....'))
ax.text(1.5, -0.05, 'Rock Road', fontsize=7, ha='center', va='center', color='#5C3317')

ax.add_patch(Rectangle((2.87, 7.66), 0.51, 4.50, lw=2, ec='#8B4513', fc='#DEB887', alpha=0.4, hatch='////'))
ax.text(3.12, 9.9, 'Bridge', fontsize=8, ha='center', va='center', color='#8B4513', fontweight='bold')

ax.add_patch(Rectangle((1.78, 11.34), 0.57, 0.02, lw=2, ec='#FF4500', fc='#FF6347', alpha=0.6))
ax.add_patch(Rectangle((0.72, 8.46), 0.20, 0.20, lw=1.5, ec='red', fc='red', alpha=0.5))
ax.add_patch(Rectangle((1.02, 8.46), 0.20, 0.20, lw=1.5, ec='red', fc='red', alpha=0.5))
ax.add_patch(Rectangle((-0.63, 9.55), 1.00, 0.10, lw=2, ec='red', fc='red', alpha=0.7))
ax.add_patch(Rectangle((1.57, 10.53), 1.00, 0.10, lw=2, ec='red', fc='red', alpha=0.7))
ax.text(-0.13, 9.72, 'Bar1', fontsize=6, ha='center', va='bottom', color='red')
ax.text(2.07, 10.70, 'Bar2', fontsize=6, ha='center', va='bottom', color='red')
ax.add_patch(Rectangle((-0.63, 12.16), 4.00, 3.50, lw=1, ec='#696969', fc='#A9A9A9', alpha=0.25, hatch='///'))

ax.add_patch(Circle((2.1, 10.8), 0.1, fc='white', ec='black', lw=2, zorder=10))
ax.text(2.15, 10.6, 'FB2', fontsize=6, ha='center', va='top', color='black')
ax.add_patch(Circle((0.4, 14.7), 0.1, fc='white', ec='black', lw=2, zorder=10))
ax.text(0.4, 14.45, 'FB3', fontsize=6, ha='center', va='top', color='black')
ax.add_patch(Rectangle((-0.1-0.065, 11.1-0.17), 0.13, 0.34, lw=1.5, ec='#1a1a1a', fc='#333333', alpha=0.8, zorder=10))
ax.text(-0.1, 10.80, 'Coke', fontsize=6, ha='center', va='top', color='#1a1a1a')

for ri, row_y in enumerate([1.34, 2.18, 3.02, 3.86]):
    for ci, col_x in enumerate([-0.4, 0.8, 2.0, 3.2]):
        grid = [['蓝','橙','蓝','蓝'],['蓝','蓝','橙','蓝'],['蓝','蓝','蓝','橙'],['橙','蓝','蓝','蓝']]
        is_orange = '橙' in grid[ri][ci]
        ax.add_patch(Circle((col_x, row_y), 0.1, fc='#E67E22' if is_orange else '#2980B9',
                            ec='#D35400' if is_orange else '#1F618D', lw=1.5, zorder=8, alpha=0.85))
ax.add_patch(Circle((0.95, 11.1), 0.1, fc='#E67E22', ec='#D35400', lw=2, zorder=10))

for ch_name, cx, color in [("Ch1", -0.14, '#E74C3C'), ("Ch2", 0.96, '#2ECC71'), ("Ch3", 2.06, '#3498DB')]:
    ax.axvline(x=cx, ymin=10.0/18.5, ymax=13.0/18.5, color=color, lw=2, ls='--', alpha=0.4)

# Start marker
ax.plot(0, 0, 'P', color='green', markersize=20, zorder=25, markeredgecolor='darkgreen', markeredgewidth=3)
ax.text(0.30, -0.15, 'START', fontsize=10, ha='left', va='top', color='green', fontweight='bold')

# ========== SHARP PATH LINES ==========
seg_colors = {
    'S1': '#27AE60', 'S2': '#2980B9', 'S3': '#8E44AD',
    'S4': '#E74C3C', 'S5': '#D35400', 'S6': '#C0392B',
}

# Draw each segment as a THICK sharp line between consecutive nodes
for i in range(len(traversal) - 1):
    nid_a = traversal[i]
    nid_b = traversal[i+1]
    x0, y0 = nodes_by_id[nid_a]['x'], nodes_by_id[nid_a]['y']
    x1, y1 = nodes_by_id[nid_b]['x'], nodes_by_id[nid_b]['y']

    # Use the segment color of the destination node
    seg = nodes_by_id[nid_b]['seg']
    color = seg_colors.get(seg, '#333333')

    # Determine if this is a backtracking segment (same segment, going "backward")
    seg_a = nodes_by_id[nid_a]['seg']
    is_backtrack = False
    for j in range(i):
        if traversal[j] == nid_a and j < i:
            prev_nid = traversal[j-1] if j > 0 else None
            if prev_nid == nid_b:
                is_backtrack = True
                break

    # Draw sharp straight line with arrow in the middle
    lw = 2.5
    alpha = 0.85
    ls = '--' if is_backtrack else '-'

    ax.plot([x0, x1], [y0, y1], ls, color=color, lw=lw, alpha=alpha, zorder=9)

    # Arrow at midpoint
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    length = np.sqrt(dx**2 + dy**2)
    if length > 0.15:
        dx, dy = dx / length * 0.08, dy / length * 0.08
        ax.arrow(mx - dx, my - dy, dx*2, dy*2,
                 head_width=0.08, head_length=0.10, fc=color, ec=color,
                 alpha=0.8, zorder=10, lw=0)

    # Step number label near midpoint
    step_num = i + 1
    label_x = mx + dy * 1.5
    label_y = my - dx * 1.5
    ax.text(label_x, label_y, str(step_num), fontsize=5, color=color, fontweight='bold',
            ha='center', va='center', zorder=11,
            bbox=dict(boxstyle='round,pad=0.1', fc='white', alpha=0.8, ec=color, lw=0.5))

# ========== NODES with traversal rank ==========
offsets = {
    1:(0.18,0.00), 2:(0.18,0.18), 3:(0.18,0.18), 4:(-0.35,-0.28), 5:(0.24,0.08),
    6:(0.24,0.08), 7:(-0.35,0.15), 8:(-0.20,0.18), 9:(0.18,-0.26), 10:(0.18,-0.26),
    11:(-0.42,-0.05), 12:(0.18,0.18), 13:(-0.35,0.18), 14:(-0.35,-0.15), 15:(0.18,0.15),
    16:(-0.12,-0.28), 17:(0.18,-0.26), 18:(0.18,-0.26), 19:(-0.44,0.00), 20:(0.24,0.00),
    21:(-0.35,0.18), 22:(-0.35,-0.15), 23:(-0.35,0.00), 24:(-0.35,0.00), 25:(0.18,-0.26),
    26:(0.18,-0.26), 27:(0.18,0.18), 28:(-0.40,0.12), 29:(0.14,0.12), 30:(0.18,-0.08),
    31:(0.18,-0.28), 32:(0.24,0.14), 33:(-0.35,-0.28), 34:(-0.35,0.14),
}

# Build step->rank map (which step number each node first appears)
first_appearance = {}
for step, nid in enumerate(traversal, 1):
    if nid not in first_appearance:
        first_appearance[nid] = step

# Count total visits per node
visit_counts = {}
for nid in traversal:
    visit_counts[nid] = visit_counts.get(nid, 0) + 1

for nid in sorted(nodes_by_id.keys()):
    node = nodes_by_id[nid]
    x, y = node['x'], node['y']
    name = node['name']
    seg = node['seg']
    is_new = nid >= 31
    color = seg_colors.get(seg, '#333333')
    visits = visit_counts.get(nid, 0)

    # Marker
    ms = 15 if is_new else 13
    ax.plot(x, y, marker='D' if is_new else 'o', markersize=ms,
            color=color, markeredgecolor='black' if is_new else '#333333',
            markeredgewidth=2.5 if is_new else 1.5, zorder=20)

    # White node ID
    ax.text(x, y, str(nid), fontsize=8, fontweight='bold',
            ha='center', va='center', color='white', zorder=21, fontfamily='DejaVu Sans')

    # Name label with first appearance rank
    step_label = f"[{first_appearance.get(nid, '?')}]{name}"
    if visits > 1:
        step_label += f" x{visits}"
    dx, dy = offsets.get(nid, (0.15, 0.13))
    ax.annotate(step_label, (x, y), textcoords="offset points", xytext=(dx*40, dy*40),
                fontsize=7, fontweight='bold' if is_new else 'normal',
                color=color, fontfamily='DejaVu Sans',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.88,
                          ec=color, lw=1.5),
                zorder=19)

# ========== SEGMENT TITLES ==========
for sx, sy, sl, sc in [(1.5, 0.5, 'S1', '#27AE60'), (1.5, 2.6, 'S2', '#2980B9'),
                         (1.5, 6.3, 'S3', '#8E44AD'), (0.96, 10.0, 'S4', '#E74C3C'),
                         (3.12, 10.0, 'S5', '#D35400'), (1.37, 14.0, 'S6', '#C0392B')]:
    ax.text(sx, sy, sl, fontsize=12, ha='center', va='center', color=sc, fontweight='bold',
            fontfamily='DejaVu Sans',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9, ec=sc, lw=2))

# Legend
legend_elements = [
    mpatches.Patch(fc='#FFD700', alpha=0.3, label='Border zone'),
    mpatches.Patch(fc='#DEB887', alpha=0.4, label='Bridge'),
    mpatches.Patch(fc='red', alpha=0.5, label='Bar / Obstacle'),
    plt.Line2D([0],[0], marker='D', color='w', markerfacecolor='#2980B9',
               markeredgecolor='black', markersize=10, label='NEW nodes (31-34)'),
    plt.Line2D([0],[0], lw=3, color='#27AE60', label='S1 path'),
    plt.Line2D([0],[0], lw=3, color='#C0392B', label='S6 path'),
    plt.Line2D([0],[0], lw=3, color='gray', ls='--', label='Backtrack'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=7, ncol=2,
          bbox_to_anchor=(1.02, 1.02), framealpha=0.9)

# Dimensions
ax.annotate('', xy=(-0.74,-1.0), xytext=(3.49,-1.0), arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax.text(1.37, -1.15, '4.2m', fontsize=8, ha='center', color='gray')
ax.annotate('', xy=(-1.2,-0.63), xytext=(-1.2,15.78), arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax.text(-1.35, 7.5, '16.4m', fontsize=8, ha='center', va='center', rotation=90, color='gray')

plt.tight_layout()
output_path = '/home/cyberdog_sim/path_v11_map.png'
plt.savefig(output_path, dpi=180, bbox_inches='tight', fc='white', ec='none')
plt.close()

import os
print(f"OK: {output_path}  ({os.path.getsize(output_path)} bytes)")
print(f"Path: {len(traversal)} stages, {len(traversal)-1} segments")
