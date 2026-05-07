#include <iostream>
#include <cmath>
#include <csignal>
#include <unistd.h>
#include <rclcpp/rclcpp.hpp>
#include <cyberdog_msg/msg/yaml_param.hpp>
#include <lcm/lcm-cpp.hpp>
#include "simulator_lcmt.hpp"
#include "gamepad_lcmt.hpp"

volatile bool running = true;
void on_sigint(int) { running = false; }

double cur_x, cur_y, cur_yaw;
bool pose_ok = false;

enum class ControlParameterValueKind : uint64_t {
    kDOUBLE = 1, kS64 = 2, kVEC_X_DOUBLE = 3, kMAT_X_DOUBLE = 4
};

double yaw_deg() { return cur_yaw * 180.0 / M_PI; }

double yaw_error(double target) {
    double err = target - cur_yaw;
    while (err > M_PI) err -= 2 * M_PI;
    while (err < -M_PI) err += 2 * M_PI;
    return err;
}

void send_yaml(rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub,
               const char* name, int64_t val) {
    auto msg = cyberdog_msg::msg::YamlParam();
    msg.name = name; msg.kind = uint64_t(ControlParameterValueKind::kS64);
    msg.s64_value = val; msg.is_user = 0;
    pub->publish(msg);
}

// 闭环旋转到目标角度
bool turn_to(lcm::LCM& lcm, double target_yaw, double kp = 0.6, double tol = 0.05, int timeout = 800) {
    for (int i = 0; i < timeout && running; i++) {
        lcm.handleTimeout(10);
        if (!pose_ok) { usleep(5000); continue; }

        double err = yaw_error(target_yaw);
        if (fabs(err) < tol) {
            std::cout << "  ✓ Converged: err=" << err*180/M_PI << "°\n";
            return true;
        }

        double cmd = kp * err;
        if (cmd >  1.0) cmd =  1.0;
        if (cmd < -1.0) cmd = -1.0;
        if (fabs(cmd) < 0.15) cmd = (cmd > 0) ? 0.15 : -0.15;  // 最小指令防死区

        gamepad_lcmt g; memset(&g, 0, sizeof(g));
        g.rightStickAnalog[0] = cmd;
        lcm.publish("gamepad_lcmt", &g);
        usleep(50000);  // 50Hz

        if (i % 20 == 0)
            std::cout << "  turn " << i << ": yaw=" << yaw_deg() << "° err=" << err*180/M_PI
                      << "° cmd=" << cmd << "\n";
    }
    std::cout << "  ⚠ Timeout, err=" << yaw_error(target_yaw)*180/M_PI << "°\n";
    return false;
}

int main(int argc, char** argv) {
    std::cerr << "test_turn starting..." << std::endl;
    signal(SIGINT, on_sigint);
    rclcpp::init(argc, argv);
    std::cerr << "ros2 init done" << std::endl;
    auto node = std::make_shared<rclcpp::Node>("test_turn");
    auto para_pub = node->create_publisher<cyberdog_msg::msg::YamlParam>("yaml_parameter", 10);

    lcm::LCM lcm;
    if (!lcm.good()) { std::cerr << "LCM init failed\n"; return 1; }
    std::cerr << "lcm init done" << std::endl;

    lcm.subscribe("simulator_state",
        std::function<void(const lcm::ReceiveBuffer*, const std::string&, const simulator_lcmt*)>(
            [](auto, auto, auto m) { cur_x = m->p[0]; cur_y = m->p[1]; cur_yaw = m->rpy[2]; pose_ok = true; }));

    std::cerr << "starting init sequence..." << std::endl;
    sleep(1);
    send_yaml(para_pub, "use_rc", 0); std::cerr << "use_rc sent\n"; sleep(1);
    send_yaml(para_pub, "control_mode", 12); std::cerr << "stand sent\n"; sleep(5);
    send_yaml(para_pub, "control_mode", 11); std::cerr << "loco sent\n"; sleep(1);

    std::cerr << "waiting for pose..." << std::endl;
    for (int w = 0; w < 100 && !pose_ok; w++) {
        lcm.handleTimeout(10);
        usleep(10000);
        if (w % 20 == 0) std::cerr << "  pose wait " << w << "...\n";
    }
    if (!pose_ok) { std::cerr << "No pose!\n"; return 1; }
    std::cerr << "pose ok! yaw=" << yaw_deg() << "°\n";

    // ── 闭环旋转测试 ──
    // Test A: 转 90°
    double start_yaw = cur_yaw;
    double target = start_yaw + M_PI/2;  // +90°
    while (target > M_PI) target -= 2*M_PI;
    std::cout << "\n[A] Closed-loop turn +90° (target=" << target*180/M_PI << "°)\n";
    turn_to(lcm, target);
    { gamepad_lcmt g; memset(&g, 0, sizeof(g)); lcm.publish("gamepad_lcmt", &g); }
    sleep(1);
    for (int w = 0; w < 30; w++) { lcm.handleTimeout(10); usleep(10000); }
    std::cout << "  Final yaw=" << yaw_deg() << "° Δ=" << (cur_yaw-start_yaw)*180/M_PI << "°\n";

    // Test B: 转 -180°
    start_yaw = cur_yaw;
    target = start_yaw - M_PI;  // -180°
    while (target < -M_PI) target += 2*M_PI;
    std::cout << "\n[B] Closed-loop turn -180° (target=" << target*180/M_PI << "°)\n";
    turn_to(lcm, target);
    { gamepad_lcmt g; memset(&g, 0, sizeof(g)); lcm.publish("gamepad_lcmt", &g); }
    sleep(1);
    for (int w = 0; w < 30; w++) { lcm.handleTimeout(10); usleep(10000); }
    std::cout << "  Final yaw=" << yaw_deg() << "° Δ=" << (cur_yaw-start_yaw)*180/M_PI << "°\n";

    // Test C: 转到 0° (朝东)
    std::cout << "\n[C] Closed-loop turn to 0° (face east)\n";
    start_yaw = cur_yaw;
    turn_to(lcm, 0.0);
    { gamepad_lcmt g; memset(&g, 0, sizeof(g)); lcm.publish("gamepad_lcmt", &g); }
    sleep(1);
    for (int w = 0; w < 30; w++) { lcm.handleTimeout(10); usleep(10000); }
    std::cout << "  Final yaw=" << yaw_deg() << "°\n";

    { gamepad_lcmt g; memset(&g, 0, sizeof(g)); lcm.publish("gamepad_lcmt", &g); }
    send_yaml(para_pub, "control_mode", 12);
    rclcpp::shutdown();
    return 0;
}
