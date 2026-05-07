import matplotlib
matplotlib.rcParams['font.family'] = 'Droid Sans Fallback'
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arc, Polygon, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(10, 32))
ax.set_xlim(-1.5, 5.5)
ax.set_ylim(-1.5, 17)
ax.set_aspect('equal')
ax.set_xlabel('X (m) →', fontsize=12)
ax.set_ylabel('Y (m) →', fontsize=12)
ax.set_title('机器狗仿真竞赛 — 赛道地图 (俯视图)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')

# ============================================================
# 1. Draw track border regions (yellow lines)
# ============================================================
border_regions = {
    "Area1\n边界黄线": (1, (-0.73, 3.49), (-0.63, 6.67), '#FFD700', 0.15),
    "Area2\n边界黄线": (2, (-0.74, 3.49), (6.55, 12.16), '#FFD700', 0.15),
    "Area3\n边界黄线": (3, (-0.74, 3.48), (12.05, 15.78), '#FFD700', 0.15),
}

for name, (idx, xr, yr, color, alpha) in border_regions.items():
    rect = Rectangle((xr[0], yr[0]), xr[1]-xr[0], yr[1]-yr[0],
                      linewidth=2, edgecolor=color, facecolor=color, alpha=alpha, linestyle='-')
    ax.add_patch(rect)
    ax.text(xr[0]-0.3, (yr[0]+yr[1])/2, name, fontsize=7, ha='right', va='center', color='#B8860B')

# ============================================================
# 2. Draw rock road (Area 1)
# ============================================================
rock = Rectangle((0.60, -0.52), 2.40-0.60, 0.48-(-0.52), linewidth=1,
                 edgecolor='#8B4513', facecolor='#A0522D', alpha=0.5, hatch='....')
ax.add_patch(rock)
ax.text(1.5, -0.02, '岩石路\n(4块,30cm宽)', fontsize=7, ha='center', va='center', color='#5C3317')

# ============================================================
# 3. Draw bridge (Area 2)
# ============================================================
bridge = Rectangle((2.87, 7.66), 3.38-2.87, 12.16-7.66, linewidth=2,
                   edgecolor='#8B4513', facecolor='#DEB887', alpha=0.7, hatch='////')
ax.add_patch(bridge)
ax.text(3.12, 9.9, '独\n木\n桥', fontsize=8, ha='center', va='center', color='#8B4513', fontweight='bold')

# ============================================================
# 4. Draw goal
# ============================================================
goal = Rectangle((1.78, 11.34), 2.35-1.78, 11.36-11.34, linewidth=2,
                 edgecolor='#FF4500', facecolor='#FF6347', alpha=0.6)
ax.add_patch(goal)
ax.text(2.07, 11.35, '球门\n50×30cm', fontsize=6, ha='center', va='bottom', color='#FF4500')

# ============================================================
# 5. Draw obstacles (Area 2)
# ============================================================
# Two 20cm blocks with 20cm spacing
obs1 = Rectangle((0.72, 8.46), 0.20, 0.20, linewidth=1.5, edgecolor='red', facecolor='red', alpha=0.6)
obs2 = Rectangle((1.02, 8.46), 0.20, 0.20, linewidth=1.5, edgecolor='red', facecolor='red', alpha=0.6)
ax.add_patch(obs1)
ax.add_patch(obs2)
ax.text(0.97, 8.36, '障碍物\n(2×20cm)', fontsize=6, ha='center', va='top', color='red')

# ============================================================
# 6. Draw height bars
# ============================================================
bar1 = Rectangle((-0.63, 9.55), 0.37-(-0.63), 9.65-9.55, linewidth=2,
                 edgecolor='red', facecolor='red', alpha=0.7)
bar2 = Rectangle((1.57, 10.53), 2.57-1.57, 10.63-10.53, linewidth=2,
                 edgecolor='red', facecolor='red', alpha=0.7)
ax.add_patch(bar1)
ax.add_patch(bar2)
ax.text(-0.13, 9.60, '限高杆1', fontsize=6, ha='center', va='bottom', color='red')
ax.text(2.07, 10.58, '限高杆2', fontsize=6, ha='center', va='bottom', color='red')

# ============================================================
# 7. Draw slope (Area 3)
# ============================================================
slope = Rectangle((-0.63, 12.16), 3.37-(-0.63), 15.66-12.16, linewidth=1,
                  edgecolor='#696969', facecolor='#A9A9A9', alpha=0.4, hatch='///')
ax.add_patch(slope)
ax.text(1.37, 13.9, '斜坡', fontsize=9, ha='center', va='center', color='#333333', fontweight='bold')

# ============================================================
# 8. Draw independent objects
# ============================================================
# football2
c = Circle((2.1, 10.8), 0.1, facecolor='white', edgecolor='black', linewidth=2, zorder=10)
ax.add_patch(c)
ax.text(2.1, 10.6, '⚽ 足球2', fontsize=7, ha='center', va='top', color='black')

# coke
coke = Rectangle((-0.1-0.065, 11.1-0.17), 0.13, 0.34, linewidth=1.5,
                 edgecolor='#1a1a1a', facecolor='#333333', alpha=0.8, zorder=10)
ax.add_patch(coke)
ax.text(-0.1, 10.85, '🥤可乐', fontsize=7, ha='center', va='top', color='#1a1a1a')

# football3
c3 = Circle((0.4, 14.7), 0.1, facecolor='white', edgecolor='black', linewidth=2, zorder=10)
ax.add_patch(c3)
ax.text(0.4, 14.5, '⚽ 足球3', fontsize=7, ha='center', va='top', color='black')

# ============================================================
# 9. Draw hanging ball matrix (Area 2) - 4x4 grid
# ============================================================
ball_colors_map = {
    '橙': ('orange', '#E67E22'),
    '蓝': ('blue', '#2980B9'),
    '蓝(固定)': ('blue', '#2980B9'),
}
grid_cols_x = [-0.4, 0.8, 2.0, 3.2]
grid_rows_y = [1.34, 2.18, 3.02, 3.86]
grid_colors = [
    ['蓝', '橙', '蓝', '蓝'],
    ['蓝', '蓝', '橙', '蓝'],
    ['蓝', '蓝', '蓝', '橙'],
    ['橙', '蓝', '蓝(固定)', '蓝(固定)'],
]

for ri, row_y in enumerate(grid_rows_y):
    for ci, col_x in enumerate(grid_cols_x):
        color_key = grid_colors[ri][ci]
        is_orange = '橙' in color_key
        fc = '#E67E22' if is_orange else '#2980B9'
        ec = '#D35400' if is_orange else '#1F618D'
        c = Circle((col_x, row_y), 0.1, facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=8, alpha=0.85)
        ax.add_patch(c)
        if is_orange:
            c_inner = Circle((col_x, row_y), 0.04, facecolor='yellow', edgecolor='none', alpha=0.7, zorder=9)
            ax.add_patch(c_inner)

# Grid label
ax.text(1.4, 0.9, '悬挂球阵\n4×4 (蓝/橙)', fontsize=8, ha='center', va='top', color='#2980B9',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# Area4 hanging orange ball
c4 = Circle((0.95, 11.1), 0.1, facecolor='#E67E22', edgecolor='#D35400', linewidth=2, zorder=10)
ax.add_patch(c4)
ax.text(0.95, 10.85, '悬挂橙球\n(距地60cm)', fontsize=6, ha='center', va='top', color='#E67E22')

# ============================================================
# 10. Draw channel centerlines & gap regions
# ============================================================
# Channel definitions from JSON
channels = [
    ("Ch1_左", -0.14, 8.5, 11.5, '#E74C3C'),
    ("Ch2_中", 0.96, 8.5, 11.5, '#2ECC71'),
    ("Ch3_右", 2.06, 8.5, 11.5, '#3498DB'),
]

for ch_name, cx, y0, y1, color in channels:
    ax.axvline(x=cx, ymin=(y0+1.5)/18.5, ymax=(y1+1.5)/18.5,
               color=color, linewidth=2, linestyle='--', alpha=0.7)
    ax.text(cx, y1+0.2, ch_name, fontsize=7, ha='center', va='bottom', color=color, fontweight='bold')

# Draw the 3-channel region highlight
ch_region = Rectangle((-0.64, 8.5), 2.56-(-0.64), 11.5-8.5,
                      linewidth=1, edgecolor='#9B59B6', facecolor='#D2B4DE', alpha=0.15, linestyle='--')
ax.add_patch(ch_region)
ax.text(0.96, 12.0, 'Area4: 三条竖向通道', fontsize=8, ha='center', va='bottom', color='#9B59B6')

# ============================================================
# 11. Draw narrow passages (key gap points)
# ============================================================
narrow_points = [
    (5.0, -0.15, '左转弯道\n78cm', '#E74C3C'),
    (5.5, 1.15, '过渡区\n250cm', '#F39C12'),
    (6.0, 2.60, '右侧通道\n104cm', '#E67E22'),
    (12.0, 3.11, '桥面入口\n50cm', '#8E44AD'),
    (13.0, -0.39, '左侧窄道\n50cm', '#2980B9'),
]

for yy, xx, label, color in narrow_points:
    ax.plot(xx, yy, 's', color=color, markersize=10, zorder=11)
    ax.text(xx+0.15, yy, label, fontsize=6, ha='left', va='center', color=color, fontweight='bold')

# ============================================================
# 12. Draw competition segment paths (approximate arrows)
# ============================================================
segment_paths = [
    ("S1\n石径探路", 0.5, 1.5, 0.0, 4.0, '#27AE60'),
    ("S2\n荒野寻珠", 1.4, 1.4, 1.3, 4.0, '#2980B9'),
    ("S3\n曲道冲锋", 1.4, 2.0, 4.0, 7.5, '#8E44AD'),
    ("S4\n深隧寻珍", 0.96, 2.0, 7.5, 11.5, '#E74C3C'),
    ("S5\n孤梁稳渡", 3.12, 3.12, 7.7, 12.2, '#D35400'),
    ("S6\n撷金建功", 1.37, 1.37, 12.2, 15.7, '#C0392B'),
]

for sname, x0, x1, y0, y1, color in segment_paths:
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=3, alpha=0.6,
                               connectionstyle='arc3,rad=0'))
    ax.text(x0+0.1, (y0+y1)/2, sname, fontsize=7, ha='left', va='center',
            color=color, fontweight='bold')

# ============================================================
# 13. Start point
# ============================================================
ax.plot(0, 0, 'P', color='green', markersize=18, zorder=15, markeredgecolor='darkgreen', markeredgewidth=2)
ax.text(0.15, -0.1, '起点 (0,0)', fontsize=9, ha='left', va='top', color='green', fontweight='bold')

# ============================================================
# 14. Legend
# ============================================================
legend_elements = [
    mpatches.Patch(facecolor='#FFD700', alpha=0.3, label='边界黄线区域'),
    mpatches.Patch(facecolor='#A0522D', alpha=0.5, label='岩石路'),
    mpatches.Patch(facecolor='#DEB887', alpha=0.7, label='独木桥'),
    mpatches.Patch(facecolor='#A9A9A9', alpha=0.4, label='斜坡'),
    mpatches.Patch(facecolor='#D2B4DE', alpha=0.2, label='三通道区域'),
    mpatches.Patch(facecolor='red', alpha=0.5, label='障碍物/限高杆'),
    mpatches.Patch(facecolor='#E67E22', alpha=0.8, label='橙色球 (悬挂)'),
    mpatches.Patch(facecolor='#2980B9', alpha=0.8, label='蓝色球 (悬挂)'),
    mpatches.Patch(facecolor='white', edgecolor='black', label='足球'),
    mpatches.Patch(facecolor='#333333', alpha=0.8, label='可乐瓶'),
    mpatches.Patch(facecolor='#FF6347', alpha=0.6, label='球门'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=7, ncol=2,
          bbox_to_anchor=(1.02, 1.02), framealpha=0.9)

# ============================================================
# 15. Dimensional annotations
# ============================================================
ax.annotate('', xy=(-0.74, -1.0), xytext=(3.49, -1.0),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax.text(1.37, -1.15, '4.2m', fontsize=8, ha='center', color='gray')

ax.annotate('', xy=(-1.2, -0.63), xytext=(-1.2, 15.78),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax.text(-1.35, 7.5, '16.4m', fontsize=8, ha='center', va='center', rotation=90, color='gray')

plt.tight_layout()
plt.savefig('/home/cyberdog_sim/赛道地图.png', dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("地图已保存到: /home/cyberdog_sim/赛道地图.png")
