#!/usr/bin/env python3
"""
从手绘路径图片中提取 waypoints.csv

用法:
  1. 用图像编辑器在 track_map.png 上用纯红色 (RGB=255,0,0) 手绘路径
  2. 保存为 track_map_path.png (或其他文件名)
  3. 运行: python3 extract_path.py [输入图片路径]

输出: waypoints.csv (在 Option_One 目录下)
"""

import cv2
import numpy as np
import math
import sys

# ---- 配置 ----
STEP = 0.04                    # 路径点间距 (m)
SMOOTH_WINDOW = 8              # 平滑窗口

# 图像 → 世界坐标变换 (从橙色球控制点计算)
# world_x = 0.008 * img_x - 1.488
# world_y = 0.008 * img_y - 0.972
SCALE = 0.008
OFFSET_X = -1.488
OFFSET_Y = -0.972


def extract_path(image_path, output_csv="waypoints.csv"):
    img = cv2.imread(image_path)
    if img is None:
        print(f"ERROR: Cannot read {image_path}")
        return

    H, W = img.shape[:2]
    print(f"Image: {W}x{H}")

    # 检测"红色"像素：高 R、低 G、低 B（适应 JPEG 压缩后的颜色偏移）
    # BGR: channel 0=B, 1=G, 2=R
    R, G, B = img[:, :, 2].astype(int), img[:, :, 1].astype(int), img[:, :, 0].astype(int)
    mask = (R > 150) & (G < 120) & (B < 120) & ((R - G) > 50) & ((R - B) > 50)
    mask = mask.astype(np.uint8) * 255

    n_pixels = cv2.countNonZero(mask)
    print(f"Detected {n_pixels} path pixels")
    if n_pixels == 0:
        print("ERROR: No path pixels found! Did you draw in the right color?")
        print(f"Looking for BGR={DRAW_COLOR_BGR} ±{COLOR_TOLERANCE}")
        return

    # 使用骨架化 (skeletonization) 从填充区域提取中心线
    # 先用形态学闭运算清理 mask
    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 距离变换 + 骨架化
    dist = cv2.distanceTransform(mask_clean, cv2.DIST_L2, 5)
    # 找局部最大值（骨架点）
    dilated = cv2.dilate(dist, np.ones((3, 3), np.uint8))
    skeleton = (dist == dilated) & (mask_clean > 0)

    skeleton_pts = np.where(skeleton)
    print(f"Skeleton points: {len(skeleton_pts[0])}")

    if len(skeleton_pts[0]) < 10:
        print("ERROR: Too few skeleton points. Draw a clearer line.")
        return

    # 对每行取骨架点的中位数 X
    sorted_path = []
    for row in range(H):
        cols = np.where(skeleton[row] > 0)[0]
        if len(cols) >= 1:
            med_x = np.median(cols)
            sorted_path.append((med_x, row))

    print(f"Path rows with data: {len(sorted_path)}/{H}")

    if len(sorted_path) < 10:
        print("ERROR: Too few path points. Draw a longer line.")
        return

    # 转为世界坐标
    world_pts = []
    for ix, iy in sorted_path:
        wx = SCALE * ix + OFFSET_X
        wy = SCALE * iy + OFFSET_Y
        world_pts.append((wx, wy))

    # 降采样
    filtered = [world_pts[0]]
    for p in world_pts[1:]:
        d = math.hypot(p[0] - filtered[-1][0], p[1] - filtered[-1][1])
        if d >= STEP:
            filtered.append(p)

    # 确保终点保留
    if math.hypot(world_pts[-1][0] - filtered[-1][0],
                  world_pts[-1][1] - filtered[-1][1]) > STEP * 0.5:
        filtered.append(world_pts[-1])

    # 平滑
    win = SMOOTH_WINDOW
    smooth = []
    for i in range(len(filtered)):
        lo, hi = max(0, i - win // 2), min(len(filtered), i + win // 2)
        sx = sum(p[0] for p in filtered[lo:hi]) / (hi - lo)
        sy = sum(p[1] for p in filtered[lo:hi]) / (hi - lo)
        smooth.append((sx, sy))

    # 保留首尾
    smooth[0] = filtered[0]
    smooth[-1] = filtered[-1]

    # 保存 CSV
    with open(output_csv, "w") as f:
        for i, (x, y) in enumerate(smooth):
            j = min(i + 1, len(smooth) - 1)
            yaw = math.atan2(smooth[j][1] - y, smooth[j][0] - x)
            f.write(f"{x:.4f},{y:.4f},{yaw:.4f}\n")

    total_len = sum(
        math.hypot(smooth[i][0] - smooth[i - 1][0],
                   smooth[i][1] - smooth[i - 1][1])
        for i in range(1, len(smooth))
    )

    print(f"\nDone! Generated {len(smooth)} waypoints → {output_csv}")
    print(f"Total length: {total_len:.1f}m")
    print(f"Start: ({smooth[0][0]:.3f}, {smooth[0][1]:.3f})")
    print(f"End:   ({smooth[-1][0]:.3f}, {smooth[-1][1]:.3f})")

    # 生成验证叠加图
    overlay = img.copy()
    for i in range(1, len(smooth)):
        x1, y1 = smooth[i - 1]
        x2, y2 = smooth[i]
        ix1 = int((x1 - OFFSET_X) / SCALE)
        iy1 = int((y1 - OFFSET_Y) / SCALE)
        ix2 = int((x2 - OFFSET_X) / SCALE)
        iy2 = int((y2 - OFFSET_Y) / SCALE)
        if 0 <= ix1 < W and 0 <= iy1 < H and 0 <= ix2 < W and 0 <= iy2 < H:
            cv2.line(overlay, (ix1, iy1), (ix2, iy2), (0, 255, 255), 2)

    # 起点绿点，终点蓝点
    for label, color, pt in [("S", (0, 255, 0), smooth[0]),
                              ("E", (255, 0, 0), smooth[-1])]:
        ix = int((pt[0] - OFFSET_X) / SCALE)
        iy = int((pt[1] - OFFSET_Y) / SCALE)
        cv2.circle(overlay, (ix, iy), 6, color, -1)
        cv2.putText(overlay, label, (ix + 8, iy), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)

    overlay_path = output_csv.replace(".csv", "_verify.png")
    cv2.imwrite(overlay_path, overlay)
    print(f"Verification image: {overlay_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = "/home/cyberdog_sim/src/Option_One/track_map_path.png"

    out = "/home/cyberdog_sim/waypoints.csv"
    if len(sys.argv) > 2:
        out = sys.argv[2]

    extract_path(img_path, out)
