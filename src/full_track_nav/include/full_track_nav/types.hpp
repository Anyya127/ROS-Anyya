#pragma once
#include <cmath>
#include <vector>
#include <string>

// ── 路径点 ─────────────────────────────────
struct Waypoint { double x, y, yaw; };

// ── 关键节点位置 (赛道行进顺序, 34个) ──────
struct KeyNode {
    const char* name;
    double x, y;
};
constexpr double NODE_RADIUS = 0.35;  // 到达判定半径 (m)

inline const KeyNode TRACK_NODES[] = {
    {"SPAWN",       0.00,  0.00},
    {"ROCK",        3.00,  0.00},
    {"PRE_TURN",    3.00,  1.00},
    {"S2_P1",       2.50,  1.00},
    {"S2_P2",       2.50,  2.50},
    {"ORANGE2",     2.00,  2.18},
    {"ORANGE1",     0.80,  1.34},
    {"S2_P3",       0.20,  1.34},
    {"ORANGE4",    -0.40,  3.86},
    {"S2_P4",       0.20,  3.02},
    {"ORANGE3",     3.20,  3.02},
    {"TURN",       -0.30,  4.50},
    {"MID1",        0.40,  5.40},
    {"CURVE2",      1.50,  5.60},
    {"MID2",        2.50,  5.80},
    {"PASS",        3.00,  7.00},
    {"CH1_IN",     -0.10,  7.00},
    {"BAR1_MID",   -0.13,  8.80},
    {"BAR1",       -0.13,  9.60},
    {"COKE",       -0.10, 11.10},
    {"S4_MID",      1.00,  9.00},
    {"CH3_IN",      2.07,  7.00},
    {"BAR2_MID",    2.07,  8.80},
    {"BAR2",        2.07, 10.58},
    {"FOOTBALL2",   2.10, 10.80},
    {"GOAL",        2.07, 11.35},
    {"BR_BOT",      3.20,  7.40},
    {"BR_TOP",      3.20, 12.40},
    {"TOP_L",      -0.35, 12.40},
    {"TOP_LL",     -0.35, 15.40},
    {"FOOTBALL3",   0.40, 14.70},
    {"TOP_RR",      3.20, 15.40},
    {"FINISH",      3.10, 12.90},
};
constexpr int NODE_COUNT = sizeof(TRACK_NODES) / sizeof(TRACK_NODES[0]);

// ── 辅助函数 ───────────────────────────────
inline double normalize_angle(double a) {
    while (a >  M_PI) a -= 2*M_PI;
    while (a < -M_PI) a += 2*M_PI;
    return a;
}

inline size_t nearest_index(double x, double y, size_t start,
                            const std::vector<Waypoint>& path) {
    if (start >= path.size()) start = 0;
    size_t best = start;
    double best_d = hypot(path[best].x - x, path[best].y - y);
    size_t end = std::min(start + 500, path.size());
    for (size_t i = start + 1; i < end; i++) {
        double d = hypot(path[i].x - x, path[i].y - y);
        if (d < best_d) { best_d = d; best = i; }
    }
    return best;
}
