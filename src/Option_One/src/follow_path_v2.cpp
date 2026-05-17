/**
 * follow_path_v2.cpp — V1 + 高抬脚步态 (过石板路)
 *
 * 与 V1 完全相同的 Pure Pursuit 路径跟踪逻辑。
 * 唯一改动: 初始化时将步态切换为 WALK (gait_id=6) 并提高 step_height_max 到 0.08m。
 *
 * V1 原始注释:
 *   控制方式: gamepad_lcmt (手柄摇杆, 世界坐标速度)
 *   leftStickAnalog[1] = 东向速度 (正=东)
 *   leftStickAnalog[0] = 南向速度 (正=南, 代码中取反)
 *   摇杆→速度映射: stick * 1.25 ≈ m/s
 */

#include <iostream>
#include <fstream>
#include <vector>
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

// ── 参数 ─────────────────────────────────────────────
const double LOOKAHEAD   = 0.50;
const double BASE_SPEED  = 0.50;
const double MAX_SPEED   = 0.70;
const double MIN_SPEED   = 0.15;
const double GOAL_TOL    = 0.20;
const double STICK_SCALE = 1.25;
const double LAT_KP      = 0.30;
const int    STUCK_LIMIT = 150;
const double STUCK_EPS   = 0.02;
// ─────────────────────────────────────────────────────

struct Waypoint { double x, y, yaw; };
std::vector<Waypoint> path;
double cur_x = 0, cur_y = 0, cur_yaw = 0;
bool pose_ok = false;

bool load_path(const char* fn) {
    std::ifstream f(fn);
    if (!f) { std::cerr << "Cannot open " << fn << "\n"; return false; }
    std::string l;
    while (std::getline(f, l)) {
        Waypoint w;
        if (sscanf(l.c_str(), "%lf,%lf,%lf", &w.x, &w.y, &w.yaw) == 3)
            path.push_back(w);
    }
    std::cout << "Loaded " << path.size() << " waypoints\n";
    return !path.empty();
}

size_t nearest_index(double x, double y, size_t start) {
    if (start >= path.size()) start = 0;
    size_t best = start;
    double best_d = hypot(path[best].x - x, path[best].y - y);
    size_t end = std::min(start + 300, path.size());
    for (size_t i = start + 1; i < end; i++) {
        double d = hypot(path[i].x - x, path[i].y - y);
        if (d < best_d) { best_d = d; best = i; }
    }
    return best;
}

void send_param(rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub,
                const char* name, int64_t val) {
    auto msg = cyberdog_msg::msg::YamlParam();
    msg.name = name; msg.kind = uint64_t(2); msg.s64_value = val; msg.is_user = 0;
    pub->publish(msg);
}

// V2 新增: 发送 double 型用户参数
void send_user_double(rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub,
                      const char* name, double val) {
    auto msg = cyberdog_msg::msg::YamlParam();
    msg.name = name; msg.kind = uint64_t(1); msg.double_value = val; msg.is_user = 1;
    pub->publish(msg);
}

int main(int argc, char** argv) {
    signal(SIGINT, on_sigint);

    const char* path_file = (argc > 1) ? argv[1] : "track_path_v10.csv";
    if (!load_path(path_file)) return 1;

    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("follow_path");
    auto para_pub = node->create_publisher<cyberdog_msg::msg::YamlParam>("yaml_parameter", 10);

    lcm::LCM lcm;
    if (!lcm.good()) { std::cerr << "LCM init failed\n"; return 1; }

    lcm.subscribe("simulator_state",
        std::function<void(const lcm::ReceiveBuffer*, const std::string&, const simulator_lcmt*)>(
            [](auto, auto, auto m) {
                cur_x = m->p[0]; cur_y = m->p[1]; cur_yaw = m->rpy[2];
                pose_ok = true;
            }));

    // ── 初始化 (V2: 增加高抬脚步态设置) ──
    sleep(1);
    std::cout << "[1] Gamepad mode\n"; send_param(para_pub, "use_rc", 0); sleep(1);
    std::cout << "[2] Recovery stand\n"; send_param(para_pub, "control_mode", 12); sleep(5);
    std::cout << "[3] Locomotion\n"; send_param(para_pub, "control_mode", 11); sleep(1);

    // ★ V2 新增: 切 WALK 步态 + 提高抬腿高度
    std::cout << "[3b] Gait → WALK (id=6)\n";       send_param(para_pub, "gait_id", 6);  sleep(1);
    std::cout << "[3c] Step height max → 0.08m\n";  send_user_double(para_pub, "step_height_max", 0.08);  sleep(1);

    for (int w = 0; w < 100 && !pose_ok; w++) { lcm.handleTimeout(10); usleep(10000); }
    if (!pose_ok) { std::cerr << "No pose\n"; rclcpp::shutdown(); return 1; }
    std::cout << "Start: (" << cur_x << "," << cur_y << ") yaw="
              << cur_yaw * 180.0 / M_PI << "°\n";

    size_t idx = nearest_index(cur_x, cur_y, 0);
    double last_x = cur_x, last_y = cur_y;
    int stuck = 0, tick = 0;
    double total_dist = 0;
    int last_wp = -1;
    std::cout << "[4] Tracking from wp#" << idx << "/" << path.size() << "\n";

    // ── 主循环 (与 V1 完全一致) ──
    while (running && rclcpp::ok()) {
        lcm.handleTimeout(10);
        if (!pose_ok) { usleep(5000); continue; }

        double dg = hypot(path.back().x - cur_x, path.back().y - cur_y);
        if (dg < GOAL_TOL) {
            std::cout << "\n🎯 GOAL REACHED! d=" << dg << "m\n";
            break;
        }

        idx = nearest_index(cur_x, cur_y, idx);

        size_t la = idx;
        for (size_t i = idx; i < path.size(); i++)
            if (hypot(path[i].x - cur_x, path[i].y - cur_y) >= LOOKAHEAD) {
                la = i; break;
            }
        if (la <= idx + 3 && la + 10 < path.size()) la += 10;

        double dx = path[la].x - cur_x;
        double dy = path[la].y - cur_y;
        double L = hypot(dx, dy);

        double vx = 0, vy = 0;
        if (L > 0.02) {
            double speed = BASE_SPEED;

            if (idx + 10 < path.size()) {
                double next_dir = atan2(
                    path[std::min(idx + 10, path.size() - 1)].y - path[idx].y,
                    path[std::min(idx + 10, path.size() - 1)].x - path[idx].x);
                double cur_dir = atan2(dy, dx);
                double angle_diff = fabs(next_dir - cur_dir);
                while (angle_diff > M_PI) angle_diff = 2 * M_PI - angle_diff;
                if (angle_diff > 0.5) speed = BASE_SPEED * 0.5;
                else if (angle_diff > 0.25) speed = BASE_SPEED * 0.75;
            }

            if (dg < 1.0) {
                double ratio = std::max(0.2, (dg - GOAL_TOL) / 0.80);
                speed *= ratio;
            }

            if (speed < MIN_SPEED) speed = MIN_SPEED;
            if (speed > MAX_SPEED) speed = MAX_SPEED;

            vx = dx / L * speed;
            vy = dy / L * speed;

            double y_err = path[idx].y - cur_y;
            double x_err = path[idx].x - cur_x;
            vy += y_err * LAT_KP;
            vx += x_err * LAT_KP * 0.3;

            double tv = hypot(vx, vy);
            if (tv > MAX_SPEED) { vx *= MAX_SPEED / tv; vy *= MAX_SPEED / tv; }
        }

        float stick_x = (float)(vx / STICK_SCALE);
        float stick_y = (float)(vy / STICK_SCALE);
        if (stick_x >  1.0f) stick_x =  1.0f;
        if (stick_x < -1.0f) stick_x = -1.0f;
        if (stick_y >  1.0f) stick_y =  1.0f;
        if (stick_y < -1.0f) stick_y = -1.0f;

        double moved = hypot(cur_x - last_x, cur_y - last_y);
        total_dist += moved;
        if (moved < STUCK_EPS) {
            if (++stuck > STUCK_LIMIT) {
                std::cout << "\n⚠️  STUCK at wp#" << idx << "\n"; break;
            }
        } else {
            stuck = 0;
            last_x = cur_x; last_y = cur_y;
        }

        if ((int)idx != last_wp || tick % 125 == 0) {
            printf("  wp#%zu (%.2f,%.2f)  cur(%.2f,%.2f)  v(%.2f,%.2f)  dg=%.1f\n",
                   idx, path[idx].x, path[idx].y, cur_x, cur_y, vx, vy, dg);
            last_wp = (int)idx;
        }
        tick++;

        gamepad_lcmt g;
        memset(&g, 0, sizeof(g));
        g.leftStickAnalog[1] = stick_x;
        g.leftStickAnalog[0] = -stick_y;
        lcm.publish("gamepad_lcmt", &g);
        usleep(20000);
    }

    {
        gamepad_lcmt g; memset(&g, 0, sizeof(g));
        lcm.publish("gamepad_lcmt", &g);
    }
    send_param(para_pub, "control_mode", 12);
    rclcpp::shutdown();
    std::cout << "Done. dist=" << total_dist << "m\n";
    return 0;
}
