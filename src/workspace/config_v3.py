#!/usr/bin/env python3
"""
config_v3.py — 赛道配置文件

修改路线、步态区域、交互触发只需改此文件，无需动引擎代码。
引擎: scheme1_step_tracking_v3.py
"""

# ═══════════════════════════════════════════════════════
# 路线文件
# ═══════════════════════════════════════════════════════
PATH_CSV = "/home/cyberdog_sim/src/workspace/track_path.csv"

# ═══════════════════════════════════════════════════════
# 跟踪参数
# ═══════════════════════════════════════════════════════
LOOKAHEAD       = 0.50      # 前视距离 (m)
LOOKAHEAD_MIN   = 0.25      # 弯道近距前视
ANGLE_THRESH    = 15.0      # 航向修正阈值 (°) — 放宽减少无意义旋转
TURN_FAST_THRES = 30.0      # 快转阈值 (°)
STEP_FAR        = 0.10      # 直道步距 (m)
STEP_NEAR       = 0.05      # 弯道步距 (m)
CURVE_ANGLE     = 25.0      # 弯道判断角 (°)
STUCK_LIMIT     = 12        # 卡住步数上限
STUCK_EPS       = 0.012     # 卡住位移阈值 (m)
GOAL_TOL        = 0.35      # 终点判定半径 (m)

# ═══════════════════════════════════════════════════════
# 步态区域 (按优先级排序, 第一个匹配的生效)
#
# gait 类型:
#   forward       — 普通前进
#   backward      — 倒退 (S1 背身)
#   high_forward  — 高抬腿 (石板路、坎)
#   crouch        — 匍匐前进 (限高杆)
#   slope         — 斜坡慢走 + 力控补偿
#
# 每个区域: dict(name, gait, step_m, speed_ms, x_min, x_max, y_min, y_max)
#   x_min/x_max 用 ±99 表示不限
# ═══════════════════════════════════════════════════════
ZONES = [
    dict(name="S1_back",   gait="backward",
         step_m=0.08, speed_ms=0.18, times=1,
         x_min=-99, x_max=2.5,  y_min=-99, y_max=0.6),

    dict(name="bridge_bump", gait="high_forward",
         step_m=0.06, speed_ms=0.12,
         x_min=3.0, x_max=99,   y_min=7.5, y_max=8.5),

    dict(name="crouch_bar1", gait="crouch",
         step_m=0.04, speed_ms=0.13, times=2,
         x_min=-2, x_max=0.6,   y_min=8.3, y_max=10.2),
    
     dict(name="crouch_bar2", gait="crouch",
          step_m=0.04, speed_ms=0.13,
          x_min=1.9, x_max=2.5,   y_min=9.3, y_max=11.8),

    dict(name="slope_area", gait="slope",
         step_m=0.04, speed_ms=0.08,
         x_min=-99, x_max=99,   y_min=11.5, y_max=99),

    dict(name="default",   gait="forward",
         step_m=STEP_FAR, speed_ms=0.30,
         x_min=-99, x_max=99,   y_min=-99, y_max=99),
]

# ═══════════════════════════════════════════════════════
# 一次性触发器 (进入区域时触发一次)
#
# action: announce(text) | print(text) | jump | custom(func)
# ═══════════════════════════════════════════════════════
TRIGGERS = [
    dict(name="s1_done",
         x_min=2.5, x_max=99,  y_min=-99, y_max=0.5,
         action="announce", arg="石板路通过"),
    
     dict(name="crouch_bar1", 
         x_min=-2, x_max=0.6,   y_min=8.3, y_max=10.2,
         action="announce", arg="识别到限高杆"),
     
     dict(name="obstacle", skip=2,
         x_min=0.5, x_max=2.0,   y_min=8.3, y_max=10.2,
         action="announce", arg="识别到障碍物"),
    
     dict(name="crouch_bar2",
          x_min=1.9, x_max=2.5,y_min=9.3, y_max=10.8,
          action="announce", arg="识别到限高杆"),

    dict(name="bridge_enter",
         x_min=3.0, x_max=99,  y_min=7.0, y_max=7.5,
         action="announce", arg="进入独木桥"),

    dict(name="finish_line",
         x_min=-99, x_max=99,  y_min=12.5, y_max=99,
         action="announce", arg="到达终点"),
]

# ═══════════════════════════════════════════════════════
# 斜坡力控
# ═══════════════════════════════════════════════════════
SLOPE_FORCE_GAIN = 300.0
SLOPE_LEAN_GAIN  = 0.8
