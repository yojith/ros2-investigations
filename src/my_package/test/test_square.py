import os
import sys
import time
import unittest

import launch
import launch_ros
import launch_testing.actions
import launch_testing.asserts
import rclpy
from std_msgs.msg import Int32, String

def generate_test_description():
    return (
        launch.LaunchDescription(
            [
                # Nodes under test
                launch_ros.actions.Node(
                    package='my_package',
                    namespace='',
                    executable='square',
                    name='square_node',
                ),
                # Launch tests 0.5 s later
                launch.actions.TimerAction(
                    period=0.5, actions=[launch_testing.actions.ReadyToTest()]),
            ]
        ), {},
    )

# Active tests
class TestSquare(unittest.TestCase):
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

    def test_positive(self, proc_output):
        """Check square of positive number"""
        msgs_rx = []
        subscription = self.node.create_subscription(String, "/output", lambda msg: msgs_rx.append(msg), 10)
        publisher = self.node.create_publisher(Int32, "/input", 10)

        try:
            # Make sure that SquareNode connects to the topic before we interact
            end_time = time.monotonic() + 5
            while time.monotonic() < end_time and (publisher.get_subscription_count() == 0 or subscription.get_publisher_count() == 0):
                rclpy.spin_once(self.node, timeout_sec=0.1)

            self.assertNotEqual(publisher.get_subscription_count(), 0, "Square node did not connect to /input in time")
            self.assertNotEqual(subscription.get_publisher_count(), 0, "Square node did not connect to /output in time")

            out_msg = Int32()
            out_msg.data = 5
            publisher.publish(out_msg)

            # Listen to the topic for 5s
            end_time = time.monotonic() + 5
            while time.monotonic() < end_time and len(msgs_rx) == 0:
                # spin to get subscriber callback executed
                rclpy.spin_once(self.node, timeout_sec=1)

            self.assertTrue(len(msgs_rx) != 0, "No output message received")
            self.assertEqual(msgs_rx[0].data, "The output is 25")
        finally:
            self.node.destroy_subscription(subscription)
            self.node.destroy_publisher(publisher)

# Post-shutdown tests
@launch_testing.post_shutdown_test()
class SquareShutdown(unittest.TestCase):
    def test_exit_codes(self, proc_info):
        """Check if the processes exited normally."""
        launch_testing.asserts.assertExitCodes(proc_info)
