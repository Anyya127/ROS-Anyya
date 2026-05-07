cmake_minimum_required(VERSION 3.8)
project(Option_One)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(cyberdog_msg REQUIRED)
find_package(lcm REQUIRED)
set(LCM_TYPE_DIR /home/cyberdog_sim/src/cyberdog_locomotion/common/lcm_type/lcm)

add_executable(follow_path src/follow_path.cpp)
target_include_directories(follow_path PRIVATE ${LCM_TYPE_DIR})
target_link_libraries(follow_path lcm)
ament_target_dependencies(follow_path rclcpp cyberdog_msg)

add_executable(test_turn src/test_turn.cpp)
target_include_directories(test_turn PRIVATE ${LCM_TYPE_DIR})
target_link_libraries(test_turn lcm)
ament_target_dependencies(test_turn rclcpp cyberdog_msg)

ament_package()
