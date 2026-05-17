/**
 * full_track_nav.cpp V2
 *
 * 纯前向/后退路径追踪 + 节点手动旋转 + 轻量朝向 P 修正
 * v_lat 恒为 0, 不侧移
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <csignal>
#include <cstring>
#include <unistd.h>

#include <rclcpp/rclcpp.hpp>
#include <cyberdog_msg/msg/yaml_param.hpp>
#include <lcm/lcm-cpp.hpp>
#include "simulator_lcmt.hpp"
#include "robot_control_cmd_lcmt.hpp"
#include "full_track_nav/types.hpp"
#include "full_track_nav/node_rotation.hpp"

volatile bool running = true;
void on_sigint(int) { running = false; }

// ═══════════════════════════════════════════ 全局状态
struct RobotState { double x=0, y=0, z=0, yaw=0; bool valid=false; };
RobotState g;

// ═══════════════════════════════════════════ 路径
std::vector<Waypoint> path;

bool load_path(const char* fn) {
    std::ifstream f(fn);
    if (!f) { std::cerr << "[ERR] Cannot open " << fn << "\n"; return false; }
    std::string l;
    while (std::getline(f, l)) {
        Waypoint w;
        if (sscanf(l.c_str(), "%lf,%lf,%lf", &w.x, &w.y, &w.yaw) >= 2)
            path.push_back(w);
    }
    std::cout << "[OK] Loaded " << path.size() << " waypoints\n";
    return !path.empty();
}

size_t nearest(double x, double y, size_t start) {
    if (start >= path.size()) start = 0;
    size_t best = start;
    double bd = hypot(path[best].x - x, path[best].y - y);
    for (size_t i = start+1; i < std::min(start+500, path.size()); i++) {
        double d = hypot(path[i].x - x, path[i].y - y);
        if (d < bd) { bd = d; best = i; }
    }
    return best;
}

// ═══════════════════════════════════════════ ROS2 helper
void set_param(rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr& pub,
               const char* name, int64_t val) {
    auto m = cyberdog_msg::msg::YamlParam();
    m.name = name; m.kind = uint64_t(2); m.s64_value = val; m.is_user = 0;
    pub->publish(m);
}

// ═══════════════════════════════════════════ RobotCommander
class Cmd {
public:
    Cmd(lcm::LCM& ca, lcm::LCM& ra) : ca_(ca), ra_(ra), life_(0) {}
    void publish_raw(float vf, float vl, float vy, float sh=0.03f, float pz=0.20f) {
        robot_control_cmd_lcmt m; memset(&m, 0, sizeof(m));
        m.mode=11; m.gait_id=27; m.contact=15;
        m.vel_des[0]=vf; m.vel_des[1]=vl; m.vel_des[2]=vy;
        m.step_height[0]=sh; m.step_height[1]=sh; m.pos_des[2]=pz;
        m.life_count = ++life_;
        ca_.publish("robot_control_cmd", &m);
    }
    void stand() {  // mode=12, 站起
        robot_control_cmd_lcmt m; memset(&m, 0, sizeof(m));
        m.mode=12; m.life_count=++life_;
        ca_.publish("robot_control_cmd", &m);
    }
    void prone() {
        robot_control_cmd_lcmt m; memset(&m, 0, sizeof(m));
        m.mode=7; m.life_count=++life_;
        ca_.publish("robot_control_cmd", &m);
    }
    void pump() { ra_.handleTimeout(10); }
private:
    lcm::LCM& ca_; lcm::LCM& ra_; int8_t life_;
};

// ═══════════════════════════════════════════ Pure Pursuit
struct Out { float vf, vy; };

Out pursuit(const RobotState& s, size_t& idx,
            double tx, double ty, bool decel) {
    const double Lf = 0.5, base = 0.30;
    idx = nearest(s.x, s.y, idx);

    // lookahead
    size_t la = idx;
    for (size_t i = idx; i < path.size(); i++)
        if (hypot(path[i].x-s.x, path[i].y-s.y) >= Lf) { la=i; break; }
    if (la <= idx+5 && la+15 < path.size()) la += 15;

    double dx = path[la].x - s.x, dy = path[la].y - s.y;
    double L = hypot(dx, dy);
    if (L < 0.01) return {0,0};

    double spd = base;

    // 弯道减速
    if (idx+10 < path.size()) {
        double d1 = atan2(path[std::min(idx+10,path.size()-1)].y - path[idx].y,
                          path[std::min(idx+10,path.size()-1)].x - path[idx].x);
        double ad = fabs(normalize_angle(atan2(dy,dx) - d1));
        if (ad > 0.5)       spd = base*0.4;
        else if (ad > 0.25) spd = base*0.7;
    }

    // 节点减速: 仅对需停的节点
    if (decel) {
        double d = hypot(tx-s.x, ty-s.y);
        if (d < 1.0) spd *= std::max(0.15, (d-0.35)/0.65);
    }

    if (spd < 0.06) spd = 0.06;
    if (spd > 0.45) spd = 0.45;

    // 世界速度
    double vx = dx/L*spd, vy = dy/L*spd;

    // 限幅
    double tv = hypot(vx, vy);
    if (tv > 0.45) { vx*=0.45/tv; vy*=0.45/tv; }

    // 世界→狗体: 只取前向, vl=0 恒成立
    double c = cos(s.yaw), si = sin(s.yaw);
    float vf = vx*c + vy*si;

    // 朝向修正
    double py = path[la].yaw;
    if (fabs(py) < 1e-6) {  // yaw=0 → 从相邻点算切线
        size_t lb = std::min(la+5, path.size()-1);
        py = atan2(path[lb].y-path[la].y, path[lb].x-path[la].x);
    }
    float vyaw = normalize_angle(py - s.yaw) * 0.25;
    if      (vyaw >  0.35) vyaw =  0.35;
    else if (vyaw < -0.35) vyaw = -0.35;

    return {vf, vyaw};
}

// ═══════════════════════════════════════════ 卡住恢复
void stuck_recover(Cmd& cmd) {
    // 持续后退 0.5s, 每 20ms 续一发, 不超时
    for (int i = 0; i < 25 && running; i++) {
        cmd.publish_raw(-0.15f, 0, 0);
        cmd.pump();
        usleep(20000);
    }
    for (int i = 0; i < 5 && running; i++) {
        cmd.publish_raw(0, 0, 0);
        cmd.pump();
        usleep(20000);
    }
}

// ═══════════════════════════════════════════ MAIN
int main(int argc, char** argv) {
    signal(SIGINT, on_sigint);

    const char* pf = (argc>1) ? argv[1]
        : "/home/cyberdog_sim/src/full_track_nav/track_path_v11.csv";
    if (!load_path(pf)) return 1;

    printf("Nodes: %d\n", NODE_COUNT);
    for (int i=0; i<NODE_COUNT; i++)
        printf("  [%2d] %-12s (%.2f,%.2f)\n", i, TRACK_NODES[i].name, TRACK_NODES[i].x, TRACK_NODES[i].y);
    printf("Rotations configured:\n");
    for (int i=0; i<ROTATION_COUNT; i++)
        if (node_needs_rotation(i))
            printf("  [%2d] %-12s rate=%.2f dur=%d ms\n",
                   i, g_rotations[i].name, g_rotations[i].yaw_rate, g_rotations[i].duration_ms);

    rclcpp::init(argc, argv);
    auto nd = std::make_shared<rclcpp::Node>("full_track_nav");
    auto pp = nd->create_publisher<cyberdog_msg::msg::YamlParam>("yaml_parameter", 10);

    lcm::LCM rx;                                    // port 7667, 收 simulator_state
    lcm::LCM tx("udpm://239.255.76.67:7671?ttl=255"); // port 7671, 发 robot_control_cmd
    if (!rx.good()) { std::cerr << "[ERR] LCM rx\n"; return 1; }
    if (!tx.good()) { std::cerr << "[ERR] LCM tx\n"; return 1; }

    rx.subscribe("simulator_state",
        std::function<void(const lcm::ReceiveBuffer*,const std::string&,const simulator_lcmt*)>(
            [](auto,auto,auto m){ g.x=m->p[0]; g.y=m->p[1]; g.z=m->p[2]; g.yaw=m->rpy[2]; g.valid=true; }));

    Cmd cmd(tx, rx);

    // ── 初始化 ──
    set_param(pp, "use_rc", 1); usleep(100000);

    printf("[0] Waiting pose...\n");
    for (int i=0; i<100 && !g.valid; i++) { cmd.pump(); usleep(10000); }
    if (!g.valid) { std::cerr << "[ERR] no pose\n"; rclcpp::shutdown(); return 1; }
    printf("    pose=(%.2f,%.2f) yaw=%.1f°\n", g.x, g.y, g.yaw*180/M_PI);

    printf("[1] Standing up...\n");
    for (int i=0; i<35 && running; i++) { cmd.stand(); cmd.pump(); usleep(200000); }
    // 确认站起后静止
    {
        double sx=g.x, sy=g.y;
        for (int i=0; i<10; i++) { cmd.pump(); usleep(200000); }  // 2s 沉降
        printf("    settle: (%.2f,%.2f)→(%.2f,%.2f) drift=%.3fm yaw=%.1f°\n",
               sx, sy, g.x, g.y, hypot(g.x-sx,g.y-sy), g.yaw*180/M_PI);
    }

    printf("[2] Switch to locomotion (vel=0)...\n");
    for (int i=0; i<15 && running; i++) { cmd.publish_raw(0,0,0); cmd.pump(); usleep(200000); }
    // 确认静止
    {
        double sx=g.x, sy=g.y;
        for (int i=0; i<10; i++) { cmd.pump(); usleep(200000); }
        printf("    settle: (%.2f,%.2f)→(%.2f,%.2f) drift=%.3fm yaw=%.1f°\n",
               sx, sy, g.x, g.y, hypot(g.x-sx,g.y-sy), g.yaw*180/M_PI);
    }

    // ── SPAWN ──
    size_t pi = nearest(g.x, g.y, 0);
    int cn = 0;
    {
        double d = hypot(TRACK_NODES[0].x-g.x, TRACK_NODES[0].y-g.y);
        if (d < NODE_RADIUS) {
            if (node_needs_rotation(0)) {
                printf("◆ SPAWN: stationary check before rotate\n");
                double sx=g.x, sy=g.y;
                for (int i=0; i<5; i++) { cmd.pump(); usleep(200000); }
                printf("    drift=%.3fm\n", hypot(g.x-sx,g.y-sy));

                printf("◆ SPAWN: rotate\n");
                cmd.publish_raw(0,0,0); usleep(200000);
                execute_node_rotation(cmd, rx, 0);
                for (int i=0; i<5; i++) { cmd.pump(); usleep(10000); }
                double syaw = g.yaw;
                printf("   post-rot: pos(%.2f,%.2f) yaw=%.1f°\n", g.x, g.y, g.yaw*180/M_PI);

                // 旋转后确认静止再进入追踪
                sx=g.x; sy=g.y;
                for (int i=0; i<10; i++) { cmd.publish_raw(0,0,0); cmd.pump(); usleep(200000); }
                printf("   settle: drift=%.3fm yaw: %.1f°→%.1f°\n",
                       hypot(g.x-sx,g.y-sy), syaw*180/M_PI, g.yaw*180/M_PI);
            }
            cn = 1;
        }
    }

    double lx=g.x, ly=g.y;
    int stuck=0, tick=0;
    double dist=0;
    pi = nearest(g.x, g.y, 0);  // 用沉降后位置重算

    printf("\n═══ Start tracking ═══\n\n");

    // ── 主循环 ──
    while (running && rclcpp::ok() && cn < NODE_COUNT) {
        cmd.pump();
        if (!g.valid) { usleep(5000); continue; }

        const KeyNode& tgt = TRACK_NODES[cn];
        double d = hypot(tgt.x-g.x, tgt.y-g.y);

        if (d < NODE_RADIUS) {
            if (node_needs_rotation(cn)) {
                printf("\n◆ [%d/%d] %s (%.2f,%.2f) d=%.2f [ROT]\n",
                       cn+1, NODE_COUNT, tgt.name, tgt.x, tgt.y, d);
                cmd.publish_raw(0,0,0); usleep(200000);
                execute_node_rotation(cmd, rx, cn);
                for (int i=0; i<5; i++) { cmd.pump(); usleep(10000); }
                printf("   post-rot yaw=%.1f°\n", g.yaw*180/M_PI);
            }
            cn++;
            if (cn >= NODE_COUNT) { printf("\n🎯 ALL DONE\n"); break; }
            if (node_needs_rotation(cn))
                printf("   → next %s (has ROT)\n", TRACK_NODES[cn].name);
            stuck=0; lx=g.x; ly=g.y;
            continue;
        }

        // Pursuit
        Out o = pursuit(g, pi, tgt.x, tgt.y, node_needs_rotation(cn));
        cmd.publish_raw(o.vf, 0, o.vy);

        // 卡住检测
        double mv = hypot(g.x-lx, g.y-ly);
        dist += mv;
        if (mv < 0.012) {
            if (++stuck > 200) {
                printf("\n⚠️ STUCK [%d]%s (%.2f,%.2f)\n", cn, tgt.name, g.x, g.y);
                stuck_recover(cmd);
                stuck=0;
            }
        } else { if (stuck>0) stuck--; lx=g.x; ly=g.y; }

        // 日志 (每 1s)
        if (tick % 50 == 0) {
            double py = path[pi].yaw;
            if (fabs(py)<1e-6) {
                size_t pi2 = std::min(pi+5, path.size()-1);
                py = atan2(path[pi2].y-path[pi].y, path[pi2].x-path[pi].x);
            }
            printf("  [%d/%d] %s | pos(%.2f,%.2f) yaw=%.0f° | path_yaw=%.0f° "
                   "vf=%.2f vy=%.2f | d=%.1f\n",
                   cn+1, NODE_COUNT, tgt.name, g.x, g.y, g.yaw*180/M_PI,
                   py*180/M_PI, o.vf, o.vy, d);
        }
        tick++;
        usleep(20000);
    }

    // ── 结束 ──
    cmd.publish_raw(0,0,0); usleep(500000);
    printf("\n[FINISH] Prone. dist=%.1fm nodes=%d/%d\n", dist, cn, NODE_COUNT);
    cmd.prone(); sleep(3);
    rclcpp::shutdown();
    return 0;
}
