import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import numpy as np
import json
import os

json_path = '/home/cyberdog_sim/src/Option_One/地图与路径/关键节点.json'
with open(json_path, 'r') as f:
    nodes_data = json.load(f)
nodes = nodes_data['节点']

fig, ax = plt.subplots(1, 1, figsize=(10, 32))
ax.set_xlim(-1.5, 5.5)
ax.set_ylim(-1.5, 17)
ax.set_aspect('equal')
ax.set_xlabel('X (m)', fontsize=12)
ax.set_ylabel('Y (m)', fontsize=12)
ax.set_title('Cyberdog Track v11 -- 34 Key Nodes  (NEW: 31=D, 32=D, 33=D, 34=D)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')

# ============================================================
# Track elements
# ============================================================
for xr, yr in [((-0.73, 3.49), (-0.63, 6.67)),
               ((-0.74, 3.49), (6.55, 12.16)),
               ((-0.74, 3.48), (12.05, 15.78))]:
    ax.add_patch(Rectangle((xr[0], yr[0]), xr[1]-xr[0], yr[1]-yr[0],
                           lw=2, ec='#FFD700', fc='#FFD700', alpha=0.10))

ax.add_patch(Rectangle((0.60, -0.52), 1.80, 1.00, lw=1, ec='#8B4513', fc='#A0522D', alpha=0.35, hatch='....'))
ax.text(1.5, -0.02, 'Rock Road', fontsize=7, ha='center', va='center', color='#5C3317')

ax.add_patch(Rectangle((2.87, 7.66), 0.51, 4.50, lw=2, ec='#8B4513', fc='#DEB887', alpha=0.5, hatch='////'))
ax.text(3.12, 9.9, 'Bridge', fontsize=8, ha='center', va='center', color='#8B4513', fontweight='bold')

ax.add_patch(Rectangle((1.78, 11.34), 0.57, 0.02, lw=2, ec='#FF4500', fc='#FF6347', alpha=0.6))
ax.add_patch(Rectangle((0.72, 8.46), 0.20, 0.20, lw=1.5, ec='red', fc='red', alpha=0.5))
ax.add_patch(Rectangle((1.02, 8.46), 0.20, 0.20, lw=1.5, ec='red', fc='red', alpha=0.5))
ax.add_patch(Rectangle((-0.63, 9.55), 1.00, 0.10, lw=2, ec='red', fc='red', alpha=0.7))
ax.add_patch(Rectangle((1.57, 10.53), 1.00, 0.10, lw=2, ec='red', fc='red', alpha=0.7))
ax.text(-0.13, 9.72, 'Bar1', fontsize=6, ha='center', va='bottom', color='red')
ax.text(2.07, 10.70, 'Bar2', fontsize=6, ha='center', va='bottom', color='red')
ax.add_patch(Rectangle((-0.63, 12.16), 4.00, 3.50, lw=1, ec='#696969', fc='#A9A9A9', alpha=0.3, hatch='///'))

ax.add_patch(Circle((2.1, 10.8), 0.1, fc='white', ec='black', lw=2, zorder=10))
ax.text(2.1, 10.6, 'FB2', fontsize=6, ha='center', va='top', color='black')
ax.add_patch(Circle((0.4, 14.7), 0.1, fc='white', ec='black', lw=2, zorder=10))
ax.text(0.4, 14.5, 'FB3', fontsize=6, ha='center', va='top', color='black')
ax.add_patch(Rectangle((-0.1-0.065, 11.1-0.17), 0.13, 0.34, lw=1.5, ec='#1a1a1a', fc='#333333', alpha=0.8, zorder=10))
ax.text(-0.1, 10.85, 'Coke', fontsize=6, ha='center', va='top', color='#1a1a1a')

for ri, row_y in enumerate([1.34, 2.18, 3.02, 3.86]):
    for ci, col_x in enumerate([-0.4, 0.8, 2.0, 3.2]):
        colors_4x4 = [['蓝','橙','蓝','蓝'],['蓝','蓝','橙','蓝'],['蓝','蓝','蓝','橙'],['橙','蓝','蓝','蓝']]
        is_orange = '橙' in colors_4x4[ri][ci]
        ax.add_patch(Circle((col_x, row_y), 0.1, fc='#E67E22' if is_orange else '#2980B9',
                            ec='#D35400' if is_orange else '#1F618D', lw=1.5, zorder=8, alpha=0.85))
ax.add_patch(Circle((0.95, 11.1), 0.1, fc='#E67E22', ec='#D35400', lw=2, zorder=10))

for ch_name, cx, color in [("Ch1", -0.14, '#E74C3C'), ("Ch2", 0.96, '#2ECC71'), ("Ch3", 2.06, '#3498DB')]:
    ax.axvline(x=cx, ymin=(10.0)/18.5, ymax=(13.0)/18.5, color=color, lw=2, ls='--', alpha=0.5)
    ax.text(cx, 11.7, ch_name, fontsize=6, ha='center', va='bottom', color=color)

ax.plot(0, 0, 'P', color='green', markersize=18, zorder=15, markeredgecolor='darkgreen', markeredgewidth=2)
ax.text(0.25, -0.1, 'START', fontsize=9, ha='left', va='top', color='green', fontweight='bold')

# ============================================================
# NODES
# ============================================================
seg_colors = {
    'S1': '#27AE60', 'S2': '#2980B9', 'S3': '#8E44AD',
    'S4': '#E74C3C', 'S5': '#D35400', 'S6': '#C0392B',
}

offsets = {
    1:(0.18,0.00), 2:(0.18,0.18), 3:(0.18,0.18), 4:(-0.30,-0.28), 5:(0.22,0.08),
    6:(0.22,0.08), 7:(-0.30,0.15), 8:(-0.20,0.18), 9:(0.18,-0.24), 10:(0.18,-0.24),
    11:(-0.40,-0.05), 12:(0.18,0.18), 13:(-0.35,0.18), 14:(-0.35,-0.15), 15:(0.18,0.15),
    16:(-0.12,-0.28), 17:(0.18,-0.25), 18:(0.18,-0.25), 19:(-0.42,0.00), 20:(0.22,0.00),
    21:(-0.35,0.18), 22:(-0.35,-0.15), 23:(-0.35,0.00), 24:(-0.35,0.00), 25:(0.18,-0.24),
    26:(0.18,-0.25), 27:(0.18,0.18), 28:(-0.38,0.12), 29:(0.12,0.12), 30:(0.18,-0.08),
    31:(0.18,-0.26), 32:(0.22,0.14), 33:(-0.32,-0.28), 34:(-0.32,0.14),
}

for node in nodes:
    nid = node['id']
    name = node['name']
    x, y = node['x'], node['y']
    seg = node['seg']
    is_new = nid >= 31
    color = seg_colors.get(seg, '#333333')

    # Large marker with thick edge
    ax.plot(x, y, marker='D' if is_new else 'o', markersize=14 if is_new else 12,
            color=color, markeredgecolor='black' if is_new else '#333333',
            markeredgewidth=2.0 if is_new else 1.2, zorder=12)

    # WHITE number on marker - large, bold, centered
    ax.text(x, y, str(nid), fontsize=8, fontweight='bold',
            ha='center', va='center', color='white', zorder=15,
            fontfamily='DejaVu Sans')

    # Name label with offset
    dx, dy = offsets.get(nid, (0.15, 0.13))
    ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx*40, dy*40),
                fontsize=7, fontweight='bold' if is_new else 'normal',
                color=color, fontfamily='DejaVu Sans',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.85, ec=color, lw=1.2),
                zorder=13)

# Segment labels
for sx, sy, sl, sc in [(1.5,0.5,'S1 Rock','#27AE60'), (1.5,2.6,'S2 Ball Hunt','#2980B9'),
                         (1.5,6.3,'S3 Sprint','#8E44AD'), (0.96,10.0,'S4 Tunnel','#E74C3C'),
                         (3.12,10.0,'S5 Bridge','#D35400'), (1.37,14.0,'S6 Push','#C0392B')]:
    ax.text(sx, sy, sl, fontsize=9, ha='center', va='center', color=sc, fontweight='bold',
            fontfamily='DejaVu Sans',
            bbox=dict(boxstyle='round', fc='white', alpha=0.85, ec=sc, lw=1.5))

# Legend
legend_elements = [
    mpatches.Patch(fc='#FFD700', alpha=0.3, label='Border'),
    mpatches.Patch(fc='#A0522D', alpha=0.35, label='Rock Road'),
    mpatches.Patch(fc='#DEB887', alpha=0.5, label='Bridge'),
    plt.Line2D([0],[0], marker='D', color='w', markerfacecolor='#2980B9',
               markeredgecolor='black', markersize=10, label='NEW nodes (31-34)'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=6.5, ncol=2,
          bbox_to_anchor=(1.02, 1.02), framealpha=0.9)

# Dimension arrows
ax.annotate('', xy=(-0.74,-1.0), xytext=(3.49,-1.0), arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax.text(1.37, -1.15, '4.2m', fontsize=8, ha='center', color='gray')
ax.annotate('', xy=(-1.2,-0.63), xytext=(-1.2,15.78), arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax.text(-1.35, 7.5, '16.4m', fontsize=8, ha='center', va='center', rotation=90, color='gray')

plt.tight_layout()
output_path = '/tmp/nodes_map_v11.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', fc='white', ec='none')
plt.close()
print(f"OK: {output_path}  ({os.path.getsize(output_path)} bytes, {len(nodes)} nodes)")
