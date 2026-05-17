#!/usr/bin/env python3
"""
openloop_motion.py — 开环运动积木库 (Python 版)

通过 LCM gamepad_lcmt 模拟手柄, 所有运动相对狗体.
所有动作阻塞执行, 可像搭积木一样顺序堆叠.
无需编译, 直接 import 使用.

用法:
    from openloop_motion import OpenLoop
    ol = OpenLoop()
    ol.init()
    ol.forward(0.4, 2000)         # 前进 2 秒
    ol.right(0.5, 3500)           # 右转 3.5 秒 (~180°)
    ol.forward_dist(0.4, 3.0)     # 前进约 3 米
    ol.right_deg(0.5, 90)         # 右转约 90°
    ol.finish()
"""

import sys
import time

sys.path.insert(0, '/usr/local/lib/python3.8/site-packages')
sys.path.insert(0, '/home/cyberdog_sim/src/cyberdog_locomotion/common/lcm_type/lcm')

import lcm
from gamepad_lcmt import gamepad_lcmt

# ═══════════════════════════════════════════════════════
# 校准参数 (根据实机/仿真调速)
# ═══════════════════════════════════════════════════════
MPS_PER_STICK  = 2.72     # stick=1.0 时约 2.72 m/s
DEGS_PER_STICK = 104.6    # stick=1.0 时约 104.6 °/s
TICK_US        = 20000    # 控制周期 20ms


class OpenLoop:
    """开环运动控制器. 所有方向相对狗体."""

    def __init__(self, lcm_url=""):
        """
        lcm_url 为空时使用 LCM 默认 (端口 7667), 与 turn_and_move.cpp 一致.
        """
        self.lcm = lcm.LCM(lcm_url) if lcm_url else lcm.LCM()
        self.msg = gamepad_lcmt()

    # ═══════════════════════════════════════════════════════
    # 内部
    # ═══════════════════════════════════════════════════════
    def _send(self, left_y=0.0, right_x=0.0):
        """发送手柄指令. left_y>0=前进, right_x>0=右转"""
        self.msg.leftStickAnalog[1]  = left_y
        self.msg.rightStickAnalog[0] = right_x
        self.lcm.publish("gamepad_lcmt", self.msg.encode())

    def _run(self, left_y, right_x, duration_ms):
        """持续发送指令, 然后回零"""
        ticks = max(1, duration_ms * 1000 // TICK_US)
        for _ in range(ticks):
            self._send(left_y, right_x)
            time.sleep(TICK_US / 1_000_000)
        self._send(0, 0)
        time.sleep(0.1)

    # ═══════════════════════════════════════════════════════
    # 初始化 / 收尾
    # ═══════════════════════════════════════════════════════
    def init(self):
        """站起 + 进入 locomotion 模式 (~7s)"""
        import subprocess
        source = (
            "source /opt/ros/galactic/setup.bash && "
            "source /home/cyberdog_sim/install/setup.bash && "
        )

        subprocess.run(
            f"bash -c '{source} ros2 topic pub -1 /yaml_parameter "
            f"cyberdog_msg/msg/YamlParam "
            f"\"{{name: use_rc, kind: 2, s64_value: 0, is_user: 0}}\"'",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)

        subprocess.run(
            f"bash -c '{source} ros2 topic pub -1 /yaml_parameter "
            f"cyberdog_msg/msg/YamlParam "
            f"\"{{name: control_mode, kind: 2, s64_value: 12, is_user: 0}}\"'",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

        subprocess.run(
            f"bash -c '{source} ros2 topic pub -1 /yaml_parameter "
            f"cyberdog_msg/msg/YamlParam "
            f"\"{{name: control_mode, kind: 2, s64_value: 11, is_user: 0}}\"'",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)

        self._send(0, 0)

    def finish(self):
        """停车 → 趴下"""
        import subprocess
        self._send(0, 0)
        time.sleep(0.3)
        source = (
            "source /opt/ros/galactic/setup.bash && "
            "source /home/cyberdog_sim/install/setup.bash && "
        )
        subprocess.run(
            f"bash -c '{source} ros2 topic pub -1 /yaml_parameter "
            f"cyberdog_msg/msg/YamlParam "
            f"\"{{name: control_mode, kind: 2, s64_value: 12, is_user: 0}}\"'",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        subprocess.run(
            f"bash -c '{source} ros2 topic pub -1 /yaml_parameter "
            f"cyberdog_msg/msg/YamlParam "
            f"\"{{name: control_mode, kind: 2, s64_value: 7, is_user: 0}}\"'",
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

    # ═══════════════════════════════════════════════════════
    # 基础动作 (时长控制) — 全部相对狗体
    # ═══════════════════════════════════════════════════════
    def forward(self, speed, duration_ms):
        """前进 (狗体前方)"""
        self._run(speed, 0, duration_ms)

    def backward(self, speed, duration_ms):
        """后退 (狗体后方)"""
        self._run(-speed, 0, duration_ms)

    def left(self, speed, duration_ms):
        """原地左转"""
        self._run(0, -speed, duration_ms)

    def right(self, speed, duration_ms):
        """原地右转"""
        self._run(0, speed, duration_ms)

    def wait(self, duration_ms):
        """原地不动"""
        self._run(0, 0, duration_ms)

    # ═══════════════════════════════════════════════════════
    # 便利动作 (距离/角度换算)
    # ═══════════════════════════════════════════════════════
    def forward_dist(self, speed, meters):
        """前进约 meters 米"""
        if speed <= 0 or meters <= 0:
            return
        ms = int(meters / (speed * MPS_PER_STICK) * 1000)
        self._run(speed, 0, ms)

    def backward_dist(self, speed, meters):
        """后退约 meters 米"""
        if speed <= 0 or meters <= 0:
            return
        ms = int(meters / (speed * MPS_PER_STICK) * 1000)
        self._run(-speed, 0, ms)

    def left_deg(self, speed, degrees):
        """原地左转约 degrees 度"""
        if speed <= 0 or degrees <= 0:
            return
        ms = int(degrees / (speed * DEGS_PER_STICK) * 1000)
        self._run(0, -speed, ms)

    def right_deg(self, speed, degrees):
        """原地右转约 degrees 度"""
        if speed <= 0 or degrees <= 0:
            return
        ms = int(degrees / (speed * DEGS_PER_STICK) * 1000)
        self._run(0, speed, ms)
