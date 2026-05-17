#!/usr/bin/env python3
"""
full_track_openloop.py — 全赛道开环兜底方案 (Python 版)

无需编译, 直接运行:
    python3 /home/cyberdog_sim/src/mycode/src/full_track_openloop.py

所有方向相对狗体 (前进/后退/左转/右转).
Ctrl+C 安全退出.
"""

import sys
import signal
sys.path.insert(0, '/home/cyberdog_sim/src/mycode/src')

from openloop_motion import OpenLoop

# 速度预设
F_SLOW = 0.25
F_NORM = 0.40
F_FAST = 0.60
T_SLOW = 0.30
T_NORM = 0.50
T_FAST = 0.70

running = True

def on_sigint(*_):
    global running
    running = False
    print("\n\n⚠  Ctrl+C — 正在安全退出...")

signal.signal(signal.SIGINT, on_sigint)


def run(ol: OpenLoop):
    global running

    # ═══════════════════════════════════════════════════
    # S1
    # ═══════════════════════════════════════════════════
    print("── S1 ──")
    if not running: return
    ol.right_deg(T_NORM, 153)
    ol.backward_dist(0.2, 7.0)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(0.4, 2)

    # ═══════════════════════════════════════════════════
    # S2
    # ═══════════════════════════════════════════════════
    print("── S2 ──")
    if not running: return
    ol.left_deg(T_NORM, 90)
    ol.backward(F_SLOW, 0.5)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(0.4, 1.5)

    if not running: return
    ol.right_deg(T_SLOW, 36)
    ol.forward_dist(F_SLOW, 0.87)

    if not running: return
    ol.left_deg(T_SLOW, 145)
    ol.forward_dist(F_SLOW, 1.47)

    if not running: return
    ol.left_deg(T_SLOW, 145)
    ol.forward_dist(F_SLOW, 1.47)

    if not running: return
    ol.left_deg(T_SLOW, 90)
    ol.forward_dist(F_SLOW, 0.6)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_SLOW, 1.68)

    if not running: return
    ol.left_deg(T_SLOW, 54)
    ol.forward_dist(F_SLOW, 1.03)

    if not running: return
    ol.left_deg(T_SLOW, 9)
    ol.forward_dist(F_SLOW, 0.65)

    # ═══════════════════════════════════════════════════
    # S3
    # ═══════════════════════════════════════════════════
    print("── S3 ──")
    if not running: return
    ol.right_deg(T_SLOW, 52)
    ol.forward_dist(F_SLOW, 1.14)

    if not running: return
    ol.right_deg(T_SLOW, 10)
    ol.forward_dist(F_SLOW, 1.12)

    if not running: return
    ol.right_deg(T_SLOW, 11)
    ol.forward_dist(F_SLOW, 1.02)

    if not running: return
    ol.right_deg(T_SLOW, 67)
    ol.forward_dist(F_SLOW, 1.30)

    if not running: return
    ol.left_deg(T_NORM, 180)
    ol.forward_dist(F_SLOW, 0.93)

    # ═══════════════════════════════════════════════════
    # S4
    # ═══════════════════════════════════════════════════
    print("── S4 ──")

    # Ch1: BAR1 + COKE
    print("  Ch1")
    if not running: return
    ol.forward_dist(F_NORM, 2.17)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_SLOW, 1.80)

    if not running: return
    ol.forward_dist(F_SLOW, 0.80)

    if not running: return
    ol.forward_dist(F_SLOW, 1.50)

    if not running: return
    ol.forward_dist(F_SLOW, 0.20)

    # 退回
    if not running: return
    ol.left_deg(T_NORM, 180)
    ol.forward_dist(F_NORM, 1.50)

    if not running: return
    ol.forward_dist(F_NORM, 0.80)

    if not running: return
    ol.forward_dist(F_NORM, 1.80)

    # Ch2: 障碍 + 悬挂橙球
    print("  Ch2")
    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_NORM, 1.13)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_SLOW, 0.70)

    if not running: return
    ol.forward_dist(F_NORM, 0.30)

    if not running: return
    ol.forward_dist(F_SLOW, 2.10)

    if not running: return
    ol.forward_dist(F_SLOW, 0.20)

    # 退回
    if not running: return
    ol.left_deg(T_NORM, 180)
    ol.forward_dist(F_NORM, 2.10)

    if not running: return
    ol.forward_dist(F_NORM, 1.00)

    # Ch3: BAR2 + 足球2 + 球门
    print("  Ch3")
    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_NORM, 1.07)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_SLOW, 1.80)

    if not running: return
    ol.forward_dist(F_SLOW, 1.78)

    if not running: return
    ol.forward_dist(F_SLOW, 0.22)

    if not running: return
    ol.forward_dist(F_SLOW, 0.55)

    # 退回
    if not running: return
    ol.left_deg(T_NORM, 180)
    ol.forward_dist(F_NORM, 0.77)

    if not running: return
    ol.forward_dist(F_NORM, 1.78)

    if not running: return
    ol.forward_dist(F_NORM, 1.80)

    if not running: return
    ol.left_deg(T_NORM, 90)
    ol.forward_dist(F_NORM, 0.93)

    # ═══════════════════════════════════════════════════
    # S5
    # ═══════════════════════════════════════════════════
    print("── S5 ──")
    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_SLOW, 0.45)

    if not running: return
    ol.forward_dist(F_SLOW, 5.0)

    # ═══════════════════════════════════════════════════
    # S6
    # ═══════════════════════════════════════════════════
    print("── S6 ──")
    if not running: return
    ol.left_deg(T_NORM, 90)
    ol.forward_dist(F_NORM, 3.55)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_NORM, 3.00)

    if not running: return
    ol.right_deg(T_NORM, 90)
    ol.forward_dist(F_NORM, 3.55)

    if not running: return
    ol.right_deg(T_SLOW, 135)
    ol.forward_dist(F_SLOW, 2.50)

    if not running: return
    ol.left_deg(T_SLOW, 146)
    ol.forward_dist(F_SLOW, 3.25)

    if not running: return
    ol.left_deg(T_SLOW, 146)
    ol.forward_dist(F_SLOW, 3.25)


if __name__ == "__main__":
    ol = OpenLoop()
    try:
        print("init ...")
        ol.init()
        print("\n========== FULL TRACK OPENLOOP (Python) ==========\n")
        run(ol)
        print("\n========== DONE ==========")
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        print("finish ...")
        ol.finish()
