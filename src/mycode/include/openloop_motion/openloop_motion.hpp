#pragma once
/**
 * openloop_motion.hpp — 开环运动积木库
 *
 * 通过 LCM gamepad_lcmt 模拟手柄, 提供相对狗体的基础动作.
 * 所有动作阻塞执行, 可像搭积木一样顺序堆叠.
 *
 * 依赖: lcm, gamepad_lcmt.hpp, rclcpp, cyberdog_msg
 *
 * 用法示例:
 *   lcm::LCM lcm;                          // 默认 LCM (端口 7667)
 *   ol_init(lcm, para_pub);                // 站起 + 进入运动模式
 *   ol_forward(lcm, 0.4, 2000);            // 0.4 速前进 2 秒
 *   ol_turn_right(lcm, 0.5, 3500);         // 0.5 速右转 3.5 秒 (~180°)
 *   ol_forward(lcm, 0.4, 3000);            // 继续前进
 *   ol_finish(lcm, para_pub);              // 停车 → 趴下
 */

#include <unistd.h>
#include <cmath>
#include <signal.h>
#include <lcm/lcm-cpp.hpp>
#include <rclcpp/rclcpp.hpp>
#include <cyberdog_msg/msg/yaml_param.hpp>
#include "gamepad_lcmt.hpp"

// ═══════════════════════════════════════════════════════
// 校准参数 (根据实机/仿真调速)
// ═══════════════════════════════════════════════════════
constexpr float  OL_MPS_PER_STICK   = 2.72f;   // stick=1.0 时约 2.72 m/s
constexpr float  OL_DEGS_PER_STICK  = 104.6f;  // stick=1.0 时约 104.6 °/s
constexpr int    OL_TICK_US         = 20000;   // 控制周期 20ms

// ═══════════════════════════════════════════════════════
// 全局运行标志 (Ctrl+C 安全退出)
// ═══════════════════════════════════════════════════════
extern volatile bool ol_running;

enum class ParamKind : uint64_t { kDOUBLE = 1, kS64 = 2, kVEC = 3, kMAT = 4 };

// ═══════════════════════════════════════════════════════
// 内部辅助
// ═══════════════════════════════════════════════════════
namespace ol_detail {
    inline void pub_param(
        rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub,
        const char* name, int64_t val)
    {
        auto msg = cyberdog_msg::msg::YamlParam();
        msg.name = name;
        msg.kind = uint64_t(ParamKind::kS64);
        msg.s64_value = val;
        msg.is_user = 0;
        pub->publish(msg);
    }

    inline void pub_gamepad(lcm::LCM& lcm, float left_y, float right_x) {
        gamepad_lcmt g;
        memset(&g, 0, sizeof(g));
        g.leftStickAnalog[1]  = left_y;   // >0 前进, <0 后退
        g.rightStickAnalog[0] = right_x;  // >0 右转, <0 左转
        lcm.publish("gamepad_lcmt", &g);
    }

    inline void run_for(lcm::LCM& lcm, float l_y, float r_x, int total_ms) {
        int ticks = total_ms * 1000 / OL_TICK_US;
        if (ticks < 1) ticks = 1;
        for (int i = 0; i < ticks && ol_running; i++) {
            pub_gamepad(lcm, l_y, r_x);
            usleep(OL_TICK_US);
        }
        pub_gamepad(lcm, 0, 0);
        usleep(100000);
    }
}

// ═══════════════════════════════════════════════════════
// 1. 初始化 / 收尾
// ═══════════════════════════════════════════════════════

inline void ol_init(
    lcm::LCM& lcm,
    rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub)
{
    ol_detail::pub_param(pub, "use_rc", 0);
    sleep(1);
    ol_detail::pub_param(pub, "control_mode", 12);  // stand
    sleep(5);
    ol_detail::pub_param(pub, "control_mode", 11);  // locomotion
    sleep(1);
    ol_detail::pub_gamepad(lcm, 0, 0);
}

inline void ol_finish(
    lcm::LCM& lcm,
    rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub)
{
    ol_detail::pub_gamepad(lcm, 0, 0);
    usleep(300000);
    ol_detail::pub_param(pub, "control_mode", 12);  // stand
    sleep(2);
    ol_detail::pub_param(pub, "control_mode", 7);   // prone
    sleep(3);
}

// ═══════════════════════════════════════════════════════
// 2. 基础动作 — 相对狗体, 时长控制
// ═══════════════════════════════════════════════════════

/// 前进 (狗体前方), speed=0~1, duration_ms 毫秒
inline void ol_forward(lcm::LCM& lcm, float speed, int duration_ms) {
    ol_detail::run_for(lcm, speed, 0, duration_ms);
}

/// 后退 (狗体后方), speed=0~1, duration_ms 毫秒
inline void ol_backward(lcm::LCM& lcm, float speed, int duration_ms) {
    ol_detail::run_for(lcm, -speed, 0, duration_ms);
}

/// 原地左转, speed=0~1, duration_ms 毫秒
inline void ol_turn_left(lcm::LCM& lcm, float speed, int duration_ms) {
    ol_detail::run_for(lcm, 0, -speed, duration_ms);
}

/// 原地右转, speed=0~1, duration_ms 毫秒
inline void ol_turn_right(lcm::LCM& lcm, float speed, int duration_ms) {
    ol_detail::run_for(lcm, 0, speed, duration_ms);
}

/// 原地不动, duration_ms 毫秒
inline void ol_wait(lcm::LCM& lcm, int duration_ms) {
    ol_detail::run_for(lcm, 0, 0, duration_ms);
}

// ═══════════════════════════════════════════════════════
// 3. 便利动作 — 距离/角度换算
// ═══════════════════════════════════════════════════════

/// 前进约 meters 米
inline void ol_forward_dist(lcm::LCM& lcm, float speed, float meters) {
    if (speed <= 0 || meters <= 0) return;
    float mps = speed * OL_MPS_PER_STICK;
    int ms = int(meters / mps * 1000.0f);
    ol_detail::run_for(lcm, speed, 0, ms);
}

/// 后退约 meters 米
inline void ol_backward_dist(lcm::LCM& lcm, float speed, float meters) {
    if (speed <= 0 || meters <= 0) return;
    float mps = speed * OL_MPS_PER_STICK;
    int ms = int(meters / mps * 1000.0f);
    ol_detail::run_for(lcm, -speed, 0, ms);
}

/// 原地左转约 degrees 度
inline void ol_turn_left_deg(lcm::LCM& lcm, float speed, float degrees) {
    if (speed <= 0 || degrees <= 0) return;
    float dps = speed * OL_DEGS_PER_STICK;
    int ms = int(degrees / dps * 1000.0f);
    ol_detail::run_for(lcm, 0, -speed, ms);
}

/// 原地右转约 degrees 度
inline void ol_turn_right_deg(lcm::LCM& lcm, float speed, float degrees) {
    if (speed <= 0 || degrees <= 0) return;
    float dps = speed * OL_DEGS_PER_STICK;
    int ms = int(degrees / dps * 1000.0f);
    ol_detail::run_for(lcm, 0, speed, ms);
}
