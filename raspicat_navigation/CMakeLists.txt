cmake_minimum_required(VERSION 3.8)
project(raspicat_navigation)
find_package(ament_cmake_auto REQUIRED)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_launch_files test/test_launch_files.py TIMEOUT 120)
endif()

ament_auto_package(
  INSTALL_TO_SHARE
  config
  launch
)
