#include <iostream>
#include <unistd.h>
#include <rclcpp/rclcpp.hpp>
#include <cyberdog_msg/msg/yaml_param.hpp>
#include <lcm/lcm-cpp.hpp>
#include "gamepad_lcmt.hpp"

enum class ControlParameterValueKind : uint64_t {
  kDOUBLE = 1,
  kS64 = 2,
  kVEC_X_DOUBLE = 3,
  kMAT_X_DOUBLE = 4
};

class TurnAndMoveNode: public rclcpp::Node
{
public:
    TurnAndMoveNode(std::string node_name):Node(node_name){};
    ~TurnAndMoveNode(){};
};

int main(int argc, char** argv){
    rclcpp::init(argc, argv);
    // 创建节点
    auto turn_node_=std::make_shared<TurnAndMoveNode>("turn_and_move_cpp");

    // 创建发布者
    rclcpp::Publisher<cyberdog_msg::msg::YamlParam>::SharedPtr para_pub_;
    para_pub_=turn_node_->create_publisher<cyberdog_msg::msg::YamlParam>("yaml_parameter",10);

    // Initialize LCM
    lcm::LCM lcm;
    if (!lcm.good()) {
        std::cerr << "LCM initialization failed!" << std::endl;
        return 1;
    }

    gamepad_lcmt gamepad_msg;
    memset(&gamepad_msg, 0, sizeof(gamepad_msg));

    std::cout << "=== Cyberdog Turn and Move Controller (C++) ===" << std::endl;
    std::cout << "Sequence: Turn 180° -> Move backward 8m -> Turn 180° -> Stop" << std::endl;
    std::cout << std::endl;

    auto param_message_ = cyberdog_msg::msg::YamlParam();

    sleep(1);

    // Step 1: Switch to gamepad control mode
    std::cout << "[1/6] Switching to gamepad control mode..." << std::endl;
    param_message_.name = "use_rc";
    param_message_.kind = uint64_t(ControlParameterValueKind::kS64);
    param_message_.s64_value = int64_t(0);
    param_message_.is_user = 0;
    para_pub_->publish(param_message_);
    sleep(1);

    // Step 2: Recovery stand
    std::cout << "[2/6] Recovery stand..." << std::endl;
    param_message_.name = "control_mode";
    param_message_.kind = uint64_t(ControlParameterValueKind::kS64);
    param_message_.s64_value = int64_t(12);
    param_message_.is_user = 0;
    para_pub_->publish(param_message_);
    std::cout << "recovery stand ..." << std::endl;
    sleep(5);

    // Step 3: Switch to locomotion mode
    std::cout << "[3/6] Switching to locomotion mode..." << std::endl;
    param_message_.name = "control_mode";
    param_message_.kind = uint64_t(ControlParameterValueKind::kS64);
    param_message_.s64_value = int64_t(11);
    param_message_.is_user = 0;
    para_pub_->publish(param_message_);
    std::cout << "locomotion ..." << std::endl;
    sleep(1);

    // Step 4: First turn 180 degrees
    std::cout << "[4/6] First turn 180 degrees..." << std::endl;
    gamepad_msg.rightStickAnalog[0] = 0.5;
    for (int i = 0; i < 40; i++) {
        lcm.publish("gamepad_lcmt", &gamepad_msg);
        usleep(86000);
    }
    gamepad_msg.rightStickAnalog[0] = 0;
    lcm.publish("gamepad_lcmt", &gamepad_msg);
    sleep(1);

    // Step 5: Move backward 8 meters
    std::cout << "[5/6] Moving backward 8 meters..." << std::endl;
    gamepad_msg.leftStickAnalog[1] = -0.4;
    for (int i = 0; i < 135; i++) {
        lcm.publish("gamepad_lcmt", &gamepad_msg);
        usleep(54500);
    }
    gamepad_msg.leftStickAnalog[1] = 0;
    lcm.publish("gamepad_lcmt", &gamepad_msg);
    sleep(1);

    // Step 6: Second turn 180 degrees
    std::cout << "[6/6] Second turn 180 degrees..." << std::endl;
    gamepad_msg.rightStickAnalog[0] = 0.5;
    for (int i = 0; i < 40; i++) {
        lcm.publish("gamepad_lcmt", &gamepad_msg);
        usleep(40000);
    }
    gamepad_msg.rightStickAnalog[0] = 0;
    gamepad_msg.leftStickAnalog[0] = 0;
    gamepad_msg.leftStickAnalog[1] = 0;
    gamepad_msg.rightStickAnalog[1] = 0;
    lcm.publish("gamepad_lcmt", &gamepad_msg);
    sleep(1);

    // Recovery stand
    std::cout << "Mission completed! Recovery stand..." << std::endl;
    param_message_.name = "control_mode";
    param_message_.kind = uint64_t(ControlParameterValueKind::kS64);
    param_message_.s64_value = int64_t(12);
    param_message_.is_user = 0;
    para_pub_->publish(param_message_);

    rclcpp::shutdown();
    return 0;
}
