#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <visualization_msgs/msg/marker.hpp>

struct Waypoint { double x, y, yaw; };

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("path_viz");
    auto pub  = node->create_publisher<visualization_msgs::msg::Marker>("path_marker", 10);

    // 加载路径
    std::ifstream f("waypoints.csv");
    if (!f) { std::cerr << "No waypoints.csv\n"; return 1; }
    std::vector<Waypoint> path;
    for (std::string l; std::getline(f, l);) {
        Waypoint w;
        if (sscanf(l.c_str(), "%lf,%lf,%lf", &w.x, &w.y, &w.yaw) == 3) path.push_back(w);
    }
    std::cout << "Loaded " << path.size() << " waypoints." << std::endl;

    std::cerr << "Publishing markers to /path_marker...\n";
    while (rclcpp::ok()) {
        auto msg = visualization_msgs::msg::Marker();
        msg.header.frame_id = "world";
        msg.header.stamp = node->now();
        msg.ns = "path";
        msg.id = 0;
        msg.type = visualization_msgs::msg::Marker::LINE_STRIP;
        msg.action = visualization_msgs::msg::Marker::ADD;
        msg.scale.x = 0.03;  // 线宽 3cm
        msg.color.r = 0.0; msg.color.g = 1.0; msg.color.b = 0.0; msg.color.a = 1.0;

        msg.points.resize(path.size());
        for (size_t i = 0; i < path.size(); i++) {
            msg.points[i].x = path[i].x;
            msg.points[i].y = path[i].y;
            msg.points[i].z = 0.02;  // 略高于地面
        }

        // 起点红色球
        auto start = visualization_msgs::msg::Marker();
        start.header.frame_id = "world";
        start.header.stamp = node->now();
        start.ns = "path";
        start.id = 1;
        start.type = visualization_msgs::msg::Marker::SPHERE;
        start.action = visualization_msgs::msg::Marker::ADD;
        start.scale.x = start.scale.y = start.scale.z = 0.1;
        start.color.r = 1.0; start.color.g = 0.0; start.color.b = 0.0; start.color.a = 1.0;
        start.pose.position.x = path.front().x;
        start.pose.position.y = path.front().y;
        start.pose.position.z = 0.1;

        // 终点绿色球
        auto end = start;
        end.id = 2;
        end.color.r = 0.0; end.color.g = 1.0;
        end.pose.position.x = path.back().x;
        end.pose.position.y = path.back().y;

        pub->publish(msg);
        pub->publish(start);
        pub->publish(end);
        std::cerr << "Published " << path.size() << " waypoints to /path_marker\n";
        rclcpp::sleep_for(std::chrono::seconds(2));
    }

    rclcpp::shutdown();
}
