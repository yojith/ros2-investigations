import os
import sys
import time
import unittest

import launch
import launch_ros
import launch_testing.actions
import launch_testing.asserts
import rclpy

def generate_test_description():
    return (
        launch.LaunchDescription(
            [
                # Nodes under test
                launch_ros.actions.Node(
                    package='package_name',
                    namespace='',
                    executable='executable_name',
                    name='node_name',
                ),
                # Launch tests 0.5 s later
                launch.actions.TimerAction(
                    period=0.5, actions=[launch_testing.actions.ReadyToTest()]),
            ]
        ), {},
    )

# Active tests
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_square')

    def tearDown(self):
        self.node.destroy_node()

    def test_name(self):
        pass

# Post-shutdown tests
@launch_testing.post_shutdown_test()
class Shutdown(unittest.TestCase):
    def test_exit_codes(self, proc_info):
        """Check if the processes exited normally."""
        launch_testing.asserts.assertExitCodes(proc_info)
