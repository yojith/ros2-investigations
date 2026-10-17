cmake_minimum_required(VERSION 3.8)
project(my_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(square src/square.cpp src/math_helper.cpp)
target_include_directories(square PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)
target_compile_features(square PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17

ament_target_dependencies(square rclcpp std_msgs)
install(TARGETS square
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  # Block requited for GTest
  # find_package(ament_lint_auto REQUIRED)
  # set(ament_cmake_copyright_FOUND TRUE)
  # set(ament_cmake_cpplint_FOUND TRUE)
  # ament_lint_auto_find_test_dependencies()
  # ----- Added -----
  find_package(rclcpp REQUIRED)
  find_package(std_msgs REQUIRED)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(${PROJECT_NAME}_unit_test test/unit_test.cpp src/math_helper.cpp)
  target_include_directories(${PROJECT_NAME}_unit_test PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)
  # -----------------


  # Block for Python integration test
  find_package(ament_cmake_ros REQUIRED)
  find_package(launch_testing_ament_cmake REQUIRED)
  function(add_ros_isolated_launch_test path)
    set(RUNNER "${ament_cmake_ros_DIR}/run_test_isolated.py")
    add_launch_test("${path}" RUNNER "${RUNNER}" ${ARGN})
  endfunction()
  # We defined this function so that adding additional tests is a simple one line addition per test
  add_ros_isolated_launch_test(test/test_square.py)
endif()

ament_package()
