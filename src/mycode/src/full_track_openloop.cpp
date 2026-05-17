/**
 * full_track_openloop.cpp — 全赛道开环兜底方案
 *
 * 使用 openloop_motion.hpp 搭积木, 所有运动相对狗体.
 * 作为 Pure Pursuit 导航不稳定时的备选方案.
 *
 * 编译: colcon build --merge-install --symlink-install --packages-up-to mycode
 * 运行: ros2 run mycode full_track_openloop
 */

#include <iostream>
#include <cmath>
#include <signal.h>
#include <rclcpp/rclcpp.hpp>
#include <cyberdog_msg/msg/yaml_param.hpp>
#include <lcm/lcm-cpp.hpp>
#include "openloop_motion/openloop_motion.hpp"

volatile bool ol_running = true;
void on_sigint(int) { ol_running = false; }

// 速度预设
constexpr float F_SLOW = 0.25f;
constexpr float F_NORM = 0.40f;
constexpr float F_FAST = 0.60f;
constexpr float T_SLOW = 0.30f;
constexpr float T_NORM = 0.50f;
constexpr float T_FAST = 0.70f;

int main(int argc, char** argv) {
    signal(SIGINT, on_sigint);

    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("full_track_openloop");
    auto pub  = node->create_publisher<cyberdog_msg::msg::YamlParam>("yaml_parameter", 10);

    // 默认 LCM 构造 (端口 7667), 与 turn_and_move.cpp 一致
    lcm::LCM lcm;
    if (!lcm.good()) { std::cerr << "LCM init failed\n"; return 1; }

    ol_init(lcm, pub);
    std::cout << "\n========== FULL TRACK OPENLOOP ==========\n" << std::endl;

    // ═══════════════════════════════════════════════════
    // S1
    // ═══════════════════════════════════════════════════
    std::cout << "── S1 ──" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 180);
    ol_forward_dist(lcm, F_NORM, 3.0);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 1.0);

    // ═══════════════════════════════════════════════════
    // S2
    // ═══════════════════════════════════════════════════
    std::cout << "── S2 ──" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 180);
    ol_backward(lcm, F_SLOW, 0.5);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 1.5);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_SLOW, 36);
    ol_forward_dist(lcm, F_SLOW, 0.87);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 145);
    ol_forward_dist(lcm, F_SLOW, 1.47);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 145);
    ol_forward_dist(lcm, F_SLOW, 1.47);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 90);
    ol_forward_dist(lcm, F_SLOW, 0.6);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 1.68);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 54);
    ol_forward_dist(lcm, F_SLOW, 1.03);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 9);
    ol_forward_dist(lcm, F_SLOW, 0.65);

    // ═══════════════════════════════════════════════════
    // S3
    // ═══════════════════════════════════════════════════
    std::cout << "── S3 ──" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_SLOW, 52);
    ol_forward_dist(lcm, F_SLOW, 1.14);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_SLOW, 10);
    ol_forward_dist(lcm, F_SLOW, 1.12);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_SLOW, 11);
    ol_forward_dist(lcm, F_SLOW, 1.02);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_SLOW, 67);
    ol_forward_dist(lcm, F_SLOW, 1.30);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 180);
    ol_forward_dist(lcm, F_SLOW, 0.93);

    // ═══════════════════════════════════════════════════
    // S4
    // ═══════════════════════════════════════════════════
    std::cout << "── S4 ──" << std::endl;

    // Ch1: BAR1 + COKE
    std::cout << "  Ch1" << std::endl;
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 2.17);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 1.80);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 0.80);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 1.50);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 0.20);
    // 退回
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 180);
    ol_forward_dist(lcm, F_NORM, 1.50);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 0.80);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 1.80);

    // Ch2: 障碍 + 悬挂橙球
    std::cout << "  Ch2" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_NORM, 1.13);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 0.70);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 0.30);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 2.10);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 0.20);
    // 退回
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 180);
    ol_forward_dist(lcm, F_NORM, 2.10);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 1.00);

    // Ch3: BAR2 + 足球2 + 球门
    std::cout << "  Ch3" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_NORM, 1.07);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 1.80);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 1.78);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 0.22);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 0.55);
    // 退回
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 180);
    ol_forward_dist(lcm, F_NORM, 0.77);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 1.78);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_NORM, 1.80);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_NORM, 0.93);

    // ═══════════════════════════════════════════════════
    // S5
    // ═══════════════════════════════════════════════════
    std::cout << "── S5 ──" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_SLOW, 0.45);
    if (!ol_running) goto cleanup;
    ol_forward_dist(lcm, F_SLOW, 5.0);

    // ═══════════════════════════════════════════════════
    // S6
    // ═══════════════════════════════════════════════════
    std::cout << "── S6 ──" << std::endl;
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_NORM, 3.55);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_NORM, 3.00);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_NORM, 90);
    ol_forward_dist(lcm, F_NORM, 3.55);
    if (!ol_running) goto cleanup;
    ol_turn_right_deg(lcm, T_SLOW, 135);
    ol_forward_dist(lcm, F_SLOW, 2.50);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 146);
    ol_forward_dist(lcm, F_SLOW, 3.25);
    if (!ol_running) goto cleanup;
    ol_turn_left_deg(lcm, T_SLOW, 146);
    ol_forward_dist(lcm, F_SLOW, 3.25);

cleanup:
    std::cout << "\n========== DONE ==========" << std::endl;
    ol_finish(lcm, pub);
    rclcpp::shutdown();
    return 0;
}
