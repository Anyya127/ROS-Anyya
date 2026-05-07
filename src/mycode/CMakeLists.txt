cmake_minimum_required(VERSION 3.8)
project(mycode)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(cyberdog_msg REQUIRED)
find_package(lcm REQUIRED)
find_package(sensor_msgs REQUIRED)

# C++ executable
add_executable(turn_and_move_cpp src/turn_and_move.cpp)
target_include_directories(turn_and_move_cpp PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  /home/cyberdog_sim/src/cyberdog_locomotion/common/lcm_type/lcm
)
target_link_libraries(turn_and_move_cpp lcm)
ament_target_dependencies(turn_and_move_cpp rclcpp cyberdog_msg)


install(TARGETS
  turn_and_move_cpp
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
