#!/usr/bin/env python3

# Copyright (c) 2023-2023 Beijing Xiaomi Mobile Software Co., Ltd. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time
import subprocess
import argparse

def kill_simulation_processes():
    """杀死所有与仿真相关的进程，防止端口或资源冲突。"""
    processes_to_kill = [
        "gzclient",
        "gzserver",
        "rviz2",
        "cyberdog_control",
        "robot_controller",
        "lcm-*",
    ]

    print("[launchsim_safe] 正在清理旧的仿真进程...")
    for proc in processes_to_kill:
        os.system(f"pkill -9 -f {proc} >/dev/null 2>&1")

    # 额外清理 ROS2 相关守护进程
    os.system("pkill -9 -f 'ros2 launch' >/dev/null 2>&1")
    os.system("pkill -9 -f 'ros2 run' >/dev/null 2>&1")
    time.sleep(1)
    print("[launchsim_safe] 进程清理完成。")

def run_in_background(script_path, log_path, env=None):
    """在无图形界面环境下后台运行脚本，输出重定向到日志文件。"""
    env_vars = env.copy() if env else os.environ.copy()
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    proc = subprocess.Popen(
        ["bash", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env_vars,
        cwd="/home/cyberdog_sim"
    )
    # 启动一个线程将输出写入日志文件
    def write_log():
        try:
            with open(log_path, "wb") as f:
                for line in proc.stdout:
                    f.write(line)
                    f.flush()
        except Exception:
            pass
    import threading
    t = threading.Thread(target=write_log, daemon=True)
    t.start()
    return proc

def launchsim():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Cyberdog 仿真启动脚本')
    parser.add_argument('--lidar', action='store_true', help='启用激光雷达')
    parser.add_argument('--camera', action='store_true', help='启用RGB摄像头')
    parser.add_argument('--world', type=str, default='race', help='选择地图: race(默认) / empty(空地+黄线)')
    args = parser.parse_args()

    kill_simulation_processes()

    log_dir = "/home/cyberdog_sim/logs"
    os.makedirs(log_dir, exist_ok=True)

    # 构建启动参数
    gazebo_args = []
    gazebo_args.extend(["--world", args.world])
    if args.lidar:
        gazebo_args.append("--lidar")
    if args.camera:
        gazebo_args.append("--camera")

    print(f"[launchsim_safe] 地图: {args.world}, 激光雷达={'开启' if args.lidar else '关闭'}, RGB摄像头={'开启' if args.camera else '关闭'}")
    print("[launchsim_safe] 启动 Gazebo 仿真...")
    
    # 使用环境变量传递参数
    my_env = os.environ.copy()
    
    # 启动 Gazebo
    gazebo_script = "./src/cyberdog_simulator/cyberdog_gazebo/script/launchgazebo.sh"
    proc = subprocess.Popen(
        ["bash", gazebo_script] + gazebo_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=my_env,
        cwd="/home/cyberdog_sim"
    )
    
    # 启动日志线程
    def write_log():
        try:
            with open(f"{log_dir}/gazebo.log", "wb") as f:
                for line in proc.stdout:
                    f.write(line)
                    f.flush()
        except Exception:
            pass
    
    import threading
    t = threading.Thread(target=write_log, daemon=True)
    t.start()
    
    gazebo_proc = proc
    time.sleep(8)

    print("[launchsim_safe] 启动可视化界面...")
    visual_proc = run_in_background(
        "./src/cyberdog_simulator/cyberdog_gazebo/script/launchvisual.sh",
        f"{log_dir}/visual.log"
    )
    time.sleep(2)

    print("[launchsim_safe] 启动控制程序...")
    control_proc = run_in_background(
        "./src/cyberdog_simulator/cyberdog_gazebo/script/launchcontrol.sh",
        f"{log_dir}/control.log"
    )

    # 如果启用了摄像头，自动启动 Web 服务器
    web_proc = None
    if args.camera:
        time.sleep(3)  # 等待摄像头初始化
        print("[launchsim_safe] 启动摄像头 Web 服务器...")
        print("[launchsim_safe] 摄像头画面地址: http://localhost:8082")
        
        web_proc = subprocess.Popen(
            ["bash", "-c", "source /opt/ros/galactic/setup.bash && source /home/cyberdog_sim/install/setup.bash && python3 /home/cyberdog_sim/camera_viewer/web_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd="/home/cyberdog_sim"
        )
        
        # Web 服务器日志线程
        def write_web_log():
            try:
                with open(f"{log_dir}/camera_web.log", "wb") as f:
                    for line in web_proc.stdout:
                        f.write(line)
                        f.flush()
            except Exception:
                pass
        
        web_log_thread = threading.Thread(target=write_web_log, daemon=True)
        web_log_thread.start()

    print("[launchsim_safe] 所有进程已启动。")
    print(f"[launchsim_safe] 日志目录: {log_dir}/")
    if args.camera:
        print("[launchsim_safe] 📷 摄像头 Web 界面: http://localhost:8082")
    print("[launchsim_safe] 按 Ctrl+C 停止所有进程。")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[launchsim_safe] 收到中断信号，正在停止所有进程...")
        procs = [gazebo_proc, visual_proc, control_proc]
        if web_proc:
            procs.append(web_proc)
        for proc in procs:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        kill_simulation_processes()
        print("[launchsim_safe] 已停止。")

if __name__ == "__main__":
    launchsim()
