#!/usr/bin/env python3
"""
scheme1_step_tracking_v3.py — 离散步态寻迹引擎

所有路线、区域、交互在 config_v3.py 中配置，只改配置不动引擎。
航向使用路径 yaw + 横向偏差修正，避免几何方向引起的无意义旋转。

用法:
    python3 /home/cyberdog_sim/src/workspace/scheme1_step_tracking_v3.py
"""

import sys, os, time, math, signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gait_lib_v2 import GaitLib
import config_v3 as cfg

running = True
_triggers_fired = set()

def on_sigint(*_):
    global running; running = False
    print("\n\n⚠  Ctrl+C — 安全退出中...")

def normalize_angle(a):
    while a >  math.pi: a -= 2*math.pi
    while a < -math.pi: a += 2*math.pi
    return a

# ═══════════════════════════════════════════════════════
def load_path(csv_path):
    path = []
    with open(csv_path) as f:
        for line in f:
            p = line.strip().split(',')
            if len(p) >= 2:
                yaw = float(p[2]) if len(p) >= 3 else 0.0
                path.append((float(p[0]), float(p[1]), yaw))
    print(f"[PATH] {len(path)} waypoints from {csv_path}")
    return path

def nearest_index(path, x, y, start):
    if start >= len(path): start = 0
    best, best_d = start, math.hypot(path[start][0]-x, path[start][1]-y)
    for i in range(start+1, min(start+500, len(path))):
        d = math.hypot(path[i][0]-x, path[i][1]-y)
        if d < best_d: best_d = d; best = i
    return best

def lookahead_index(path, x, y, start, L):
    for i in range(start, len(path)):
        if math.hypot(path[i][0]-x, path[i][1]-y) >= L: return i
    return len(path)-1

def is_curve(path, idx, n=10):
    if idx+n >= len(path): return False
    a0 = math.atan2(path[min(idx+n,len(path)-1)][1]-path[idx][1],
                    path[min(idx+n,len(path)-1)][0]-path[idx][0])
    a1 = math.atan2(path[min(idx+n+5,len(path)-1)][1]-path[min(idx+n,len(path)-1)][1],
                    path[min(idx+n+5,len(path)-1)][0]-path[min(idx+n,len(path)-1)][0])
    return math.degrees(abs(a1-a0)) > cfg.CURVE_ANGLE

def match_zone(x, y):
    for z in cfg.ZONES:
        if z['x_min'] <= x <= z['x_max'] and z['y_min'] <= y <= z['y_max']:
            return z
    return cfg.ZONES[-1]

def match_triggers(x, y):
    return [t for t in cfg.TRIGGERS
            if t['name'] not in _triggers_fired
            and t['x_min'] <= x <= t['x_max']
            and t['y_min'] <= y <= t['y_max']]

def fire_trigger(gl, t):
    _triggers_fired.add(t['name'])
    print(f"\n  ⚡ [{t['name']}]", end='')
    if t['action'] == 'announce':
        print(f" 📢 {t['arg']}"); gl.announce(t['arg'])
    elif t['action'] == 'print':
        print(f" ℹ️  {t['arg']}")
    elif t['action'] == 'jump':
        print(" 🤸"); gl.jump()
    elif t['action'] == 'custom' and callable(t['arg']):
        print(" 🔧"); t['arg'](gl)

def execute_gait(gl, zone, dg):
    g, d, s = zone['gait'], zone['step_m'], zone['speed_ms']
    if dg < 1.0: d = max(0.03, d*(dg/1.0))
    if   g == 'backward':      gl.step_backward(d, speed=s)
    elif g == 'high_forward':  gl.step_high_forward(d, speed=s)
    elif g == 'crouch':        gl.crouch_step_forward(d, speed=s)
    elif g == 'slope':         gl.step_forward(d, speed=s)
    else:                      gl.step_forward(d, speed=s)

# ═══════════════════════════════════════════════════════
def run():
    global running
    if not os.path.exists(cfg.PATH_CSV):
        print(f"[ERROR] {cfg.PATH_CSV} not found!"); return
    path = load_path(cfg.PATH_CSV)

    gl = GaitLib()
    gl.init()
    if not gl.pose_valid: print("[ERROR] No pose"); return

    x, y, z, roll, pitch, yaw = gl.get_position()
    idx = nearest_index(path, x, y, 0)
    last_x, last_y = x, y
    stuck_cnt = step = 0
    total_dist = 0.0
    last_zone = slope_active = None

    goal = path[-1]
    print(f"\n═══ V3 ═══")
    print(f"  Start: ({x:.2f},{y:.2f}) yaw={math.degrees(yaw):.0f}°")
    print(f"  Goal:  ({goal[0]:.2f},{goal[1]:.2f})")
    print(f"  Zones:{len(cfg.ZONES)}  Triggers:{len(cfg.TRIGGERS)}\n")

    while running:
        x, y, z, roll, pitch, yaw = gl.get_position()

        # ── 区域 ──
        zone = match_zone(x, y)
        if zone != last_zone:
            print(f"\n  ➜ [{zone['name']}] gait={zone['gait']}")
            last_zone = zone

        # ── 斜坡力控 (滞后) ──
        if zone['gait'] == 'slope' or slope_active:
            want = (y > 12.2) if not slope_active else (y > 11.8)
            if want and not slope_active:
                gl.enable_slope_comp(cfg.SLOPE_FORCE_GAIN, cfg.SLOPE_LEAN_GAIN)
                slope_active = True
            elif not want and slope_active:
                gl.disable_slope_comp(); slope_active = False
        if slope_active: gl._slope_tick()

        # ── 触发器 ──
        for t in match_triggers(x, y): fire_trigger(gl, t)

        # ── 终点 ──
        dg = math.hypot(goal[0]-x, goal[1]-y)
        if dg < cfg.GOAL_TOL:
            print(f"\n🎯 GOAL! d={dg:.2f}m steps={step} dist={total_dist:.1f}m"); break

        # ── 路点 + 前视 ──
        idx = nearest_index(path, x, y, idx)
        curve = is_curve(path, idx)
        L = cfg.LOOKAHEAD_MIN if curve else cfg.LOOKAHEAD
        la = lookahead_index(path, x, y, idx, L)
        tx, ty, _ = path[la]

        # ── 航向: 几何方向 (狗→前视点) ──
        is_backward = (zone['gait'] == 'backward')
        geo_angle = math.atan2(ty - y, tx - x)
        if is_backward:
            target = normalize_angle(geo_angle + math.pi)
        else:
            target = geo_angle
        a_err = math.degrees(normalize_angle(target - yaw))

        # ── 执行 ──
        if abs(a_err) > cfg.ANGLE_THRESH:
            rate = 0.5 if abs(a_err) > cfg.TURN_FAST_THRES else 0.25
            gl.step_turn(a_err, rate=rate)
        else:
            execute_gait(gl, zone, dg)

        # ── 卡住 ──
        moved = math.hypot(x-last_x, y-last_y)
        total_dist += moved
        if moved < cfg.STUCK_EPS:
            stuck_cnt += 1
            if stuck_cnt > cfg.STUCK_LIMIT:
                print(f"\n⚠️  STUCK ({x:.2f},{y:.2f}) wp={idx}")
                gl.stuck_recover(); stuck_cnt = 0
        else:
            if stuck_cnt: stuck_cnt -= 1
            last_x, last_y = x, y

        step += 1
        if step % 20 == 0:
            print(f"  [{step:5d}] ({x:6.2f},{y:6.2f}) y={math.degrees(yaw):5.0f}°  "
                  f"wp={idx:5d} a_err={a_err:+5.1f}° dg={dg:4.1f}m [{zone['name']}]")

    if slope_active: gl.disable_slope_comp()
    gl.finish()
    print(f"\nDone. steps={step} dist={total_dist:.1f}m")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_sigint)
    try:
        run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback; traceback.print_exc()
