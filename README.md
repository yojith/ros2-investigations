# ROS2 Investigations

## Week 1
Yojith is working on CICD/testing/traceability investigation.
For week 1, try to implement a simple workflow for creating ROS2 tests and having them run via CI/CD pipeline and produce reports via strictdoc

### ROS2 package setup
Used this playlist, its a decent quick start: https://www.youtube.com/playlist?list=PLSK7NtBWwmpTS_YVfjeN3ZzIxItI1P_Sr
1. use the setup script to launch the docker image
2. clone a GitHub repo (ros2-investigations)
3. `ros2 pkg create <package> --build-type ament_cmake --node-name <node>` will create a ros2 package with a node built in. it creates an empty folder with a CMakeLists.txt and package.xml file for compilation instructions and project dependencies
4. Make sure to fill out package.xml with the proper description, maintainer, and license tags.
5. Also in package.xml, make sure to add the proper ros package dependencies based on the package include statements. For example, rclcpp and std_msgs.
6. Similarly, in Cmakelists.txt add the corresponding find_package statements
7. If it isnt already there, make sure add_executable is there with the particular node (c++ file), and that install is pointing to the correct executablet target and the libs destination 
8. Include ament_target_dependencies with the executable name and any dependencies, like rclcpp and std_msgs.
10. For all ros2 commands, make sure to run source /opt/ros/jazzy/setup.bash. Put it in /.bashrc file to avoid running it every time.
11. See https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Cpp-Publisher-And-Subscriber.html for simple example on building a publisher/subsriber.
12. See square.cpp for a simple node that takes in a number from a subscribed topic, squares it, and publishes to another topic. A few things to note are the included packages, and the main function which starts the node. All node are defined as classes that must inherit from `rclcpp::Node`. 
13. `colcon build --packages-select <package>` to build. Afterwards, make sure to run `source install/setup.bash`.
14. To start a ros2 node, launch `ros2 run <package> <node_executable>`. We can see all ros2 nodes and topics using `ros2 node list` or `ros2 topic list`
15. We can see a specific ros2's susbcribers and publishers using `ros2 node info <node_name>` (make sure to include the slash in the node name).
16. We can set a terminal to listen to a topic using `ros2 topic echo <topic_name>` (make sure to include the slash in the topic name).
17. We can "inject" messages manually into topics using ros2 cli instead of creating a cpp node. This allows for easy tests. Use the command `ros2 topic pub --once <topic_name> <msg_type> '<args>'`. Remove --once to keep publishing at 1Hz. Adjust frequency with `-r <hz>`.
18. note: args must be in the form of a yaml dictionary. eg for std_msgs/msg/Int32, the args would be '{data: 5}' to send the number 5.


### Testing
Ros2 uses google test framework, called GTest.
1. Add test dependency in package.xml for ament_cmake_gtest
2. Edit the BUILD_TESTING section in CMakeLists.txt to find the ament_cmake_gtest package, add a gtest, and add target include directories
3. Create a test file in the test folder. See square_test.cpp for an example. Note that the test file must include gtest/gtest.h. After creating the tests, make sure to rebuild the package and rerun the `source install/setup.bash` command.
4. To compile and run the tests, just run `colcon test --packages-select <package>`. To see the test results, run `colcon test-result --all --verbose`. Test results are output to an xml file that can be used for generating reports.
5. By default, linting is on for tests. To disable them, comment out linting related lines in CMakeLists.txt.

These steps are simple for unit testing if testing files that don't have a main function. Integration testing an entire node is a bit more complicated and requires creating creating a test node. See this: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Testing/Integration.html
1. Python unittest framework is used, but this will be registered in CMakeLists.txt to run as part of the colcon test format similar to GTest. The python test file will resemble a ROS2 python file, since we are essentially building and launching a ROS2 node for testing our C++ ROS code.
2. Create a python test launch file. See `test/test_square.py`. Ensure naming convention is `test/test_*.py` See test_square.py. Ensure that the relevant imports are present, such as unittest, launch, launch_ros, launch_testing.actions, and rclpy.
3. Define a generate_test_description to describe which nodes must be launched. Ensure that the package, executable, and node name are all correct.
4. To create a suite of test cases, create a class that inherits from unittest.TestCase. Each test case is a method prefixed with test_*. Make sure to add setup and teardown class methods that initialize and shut down rclpy. Additionally, setup and teardown instance methods run before and after every test method. This is useful to ensure a new node is used for each test case.
5. Post shutdown tests can be defined. They run after all nodes under test exit, and are generally used to ensure graceful shutdown.
6. Note, proc_output is a fixture provided by ROS2 that contains all process stdout and stderr. These are useful to capture logs from nodes.  
7. Add test dependencies in package.xml (as shown in the repo), and in CMakeLists.txt (also shown in the repo). To add particular python test file to colcon test, just add `add_ros_isolated_launch_test(test/<test_file>)` for each test in CMakeLists.txt
8. Run colcon test as usual using the same process as GTests

### CI/CD
Look into automating the whole CI/CD pipeline using something like GitHub actions. Most likely we will use GitLab CI since all the repos are housed on GitLab.

1. Create a `.github/workflows/<name>.yml` file. See `test.yml` for an example.
2. Since we are using a Docker image, we must first build the image using `docker build -t <image_name> -f <dockerfile_path> .`
3. We can run the docker image while passing in our bash commands using `docker run --rm -v "${{ github.workspace }}:/workspace" <image_name> bash -c "<commands>"`. --rm removes the container after the commands are run, and -v puts the current checked out workspace into the docker container.
4. The produced XML test results can generate reports using strictdoc.
5. Note, with GitLab CI, we can reuse built docker images for subsequent jobs without having to rebuild the image, if they run on a private hosted server. This would cut down on build times and potentially make CI faster.
