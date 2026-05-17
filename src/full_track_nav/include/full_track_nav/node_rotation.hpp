#pragma once
#include <cstdio>
#include <unistd.h>
#include <lcm/lcm-cpp.hpp>
#include "robot_control_cmd_lcmt.hpp"

// ═══════════════════════════════════════════════════════════════
// 每个关键节点的开环旋转配置（用户手动填写）
// ═══════════════════════════════════════════════════════════════
struct NodeRotationCfg {
    const char* name;
    float yaw_rate;      // 旋转角速度 rad/s, +左转(CCW) / -右转(CW)
    int   duration_ms;   // 旋转持续时间 ms, 0=跳过
};

// ── 34 个关键节点, 按赛道行进顺序排列 ──────────────────────
//    导航到达某节点后, 自动执行对应的旋转配置
//    只需修改 yaw_rate / duration_ms, 重新编译即可
inline NodeRotationCfg g_rotations[] = {
    // id  节点名          yaw_rate(rad/s)  dur(ms)
    /*  0 */ {"SPAWN",       0.60f,   3400},
    /*  1 */ {"ROCK",        0.6f,    3400},
    /*  2 */ {"PRE_TURN",    0.0f,    0},
    /*  3 */ {"S2_P1",       0.0f,    0},
    /*  4 */ {"S2_P2",       0.0f,    0},
    /*  5 */ {"ORANGE2",     0.0f,    0},
    /*  6 */ {"ORANGE1",     0.0f,    0},
    /*  7 */ {"S2_P3",       0.0f,    0},
    /*  8 */ {"ORANGE4",     0.0f,    0},
    /*  9 */ {"S2_P4",       0.0f,    0},
    /* 10 */ {"ORANGE3",     0.0f,    0},
    /* 11 */ {"TURN",        0.0f,    0},
    /* 12 */ {"MID1",        0.0f,    0},
    /* 13 */ {"CURVE2",      0.0f,    0},
    /* 14 */ {"MID2",        0.0f,    0},
    /* 15 */ {"PASS",        0.0f,    0},
    /* 16 */ {"CH1_IN",      0.0f,    0},
    /* 17 */ {"BAR1_MID",    0.0f,    0},
    /* 18 */ {"BAR1",        0.0f,    0},
    /* 19 */ {"COKE",        0.0f,    0},
    /* 20 */ {"S4_MID",      0.0f,    0},
    /* 21 */ {"CH3_IN",      0.0f,    0},
    /* 22 */ {"BAR2_MID",    0.0f,    0},
    /* 23 */ {"BAR2",        0.0f,    0},
    /* 24 */ {"FOOTBALL2",   0.0f,    0},
    /* 25 */ {"GOAL",        0.0f,    0},
    /* 26 */ {"BR_BOT",      0.0f,    0},
    /* 27 */ {"BR_TOP",      0.0f,    0},
    /* 28 */ {"TOP_L",       0.0f,    0},
    /* 29 */ {"TOP_LL",      0.0f,    0},
    /* 30 */ {"FOOTBALL3",   0.0f,    0},
    /* 31 */ {"TOP_RR",      0.0f,    0},
    /* 32 */ {"FINISH",      0.0f,    0},
    /* 33 */ {"",            0.0f,    0},  // sentinel
};
constexpr int ROTATION_COUNT = sizeof(g_rotations) / sizeof(g_rotations[0]) - 1;

// 检查节点是否需要旋转 (duration_ms > 0)
inline bool node_needs_rotation(int idx) {
    return idx >= 0 && idx < ROTATION_COUNT && g_rotations[idx].duration_ms > 0;
}

// ═══════════════════════════════════════════════════════════════
// 开环旋转执行函数
// ═══════════════════════════════════════════════════════════════

template<typename Commander>
void execute_node_rotation(Commander& cmd, lcm::LCM& recv, int node_idx) {
    if (node_idx < 0 || node_idx >= ROTATION_COUNT) return;

    const NodeRotationCfg& cfg = g_rotations[node_idx];
    if (cfg.duration_ms <= 0) {
        printf("  [ROT] node %d '%s': skip (duration=0)\n", node_idx, g_rotations[node_idx].name);
        return;
    }

    printf("  [ROT] node %d '%s': yaw_rate=%.2f rad/s  dur=%d ms\n",
           node_idx, g_rotations[node_idx].name, cfg.yaw_rate, cfg.duration_ms);

    int loops = cfg.duration_ms / 20;  // 20ms per tick = 50Hz
    if (loops < 1) loops = 1;

    for (int i = 0; i < loops; i++) {
        cmd.publish_raw(0.0f, 0.0f, cfg.yaw_rate, 0.08f, 0.00f);  // 高抬腿+低重心, 防漂移
        recv.handleTimeout(10);
        usleep(20000);
    }

    // 停, 恢复正常步态参数
    cmd.publish_raw(0.0f, 0.0f, 0.0f, 0.03f, 0.20f);
    usleep(100000);
    printf("  [ROT] done.\n");
}
