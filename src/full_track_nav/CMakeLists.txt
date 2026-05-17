cmake_minimum_required(VERSION 3.8)
project(full_track_nav)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(cyberdog_msg REQUIRED)
find_package(lcm REQUIRED)

set(LCM_TYPE_DIR /home/cyberdog_sim/src/cyberdog_locomotion/common/lcm_type/lcm)

add_executable(full_track_nav src/full_track_nav.cpp)
target_include_directories(full_track_nav PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${LCM_TYPE_DIR}
)
target_link_libraries(full_track_nav lcm)
ament_target_dependencies(full_track_nav rclcpp cyberdog_msg)

install(TARGETS full_track_nav DESTINATION lib/${PROJECT_NAME})

ament_package()
