#!/usr/bin/env python3

import subprocess

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from ament_index_python.packages import get_package_share_directory

from social_robot_behaviors.behavior_manager_client import (
    BehaviorManagerClient,
)


class BehaviorManagerClientNode(Node):

    def __init__(self):

        super().__init__("behavior_manager_client_node")

        # ---------------------------------------------------------
        # Parameters
        # ---------------------------------------------------------

        self.declare_parameter(
            "motions_package",
            "ur5e_robot_controller"
        )

        self.declare_parameter(
            "motions_dir",
            "config"
        )

        self.declare_parameter(
            "motion_launch_package",
            "ur5e_robot_controller"
        )

        self.declare_parameter(
            "motion_launch_file",
            "ur5e_pose_sequence.launch.py"
        )

        # ---------------------------------------------------------
        # Resolve paths
        # ---------------------------------------------------------

        motions_package = self.get_parameter(
            "motions_package"
        ).value

        motions_dir = self.get_parameter(
            "motions_dir"
        ).value

        motions_path = (
            get_package_share_directory(motions_package)
            + f"/{motions_dir}"
        )

        # ---------------------------------------------------------
        # Behavior manager
        # ---------------------------------------------------------

        self.behavior_manager = BehaviorManagerClient(
            motions_dir=motions_path
        )

        # ---------------------------------------------------------
        # Launch configuration
        # ---------------------------------------------------------

        self.motion_launch_package = self.get_parameter(
            "motion_launch_package"
        ).value

        self.motion_launch_file = self.get_parameter(
            "motion_launch_file"
        ).value

        # ---------------------------------------------------------
        # Subscriber
        # ---------------------------------------------------------

        self.subscription = self.create_subscription(
            String,
            "/social_behavior",
            self.behavior_callback,
            10
        )

        self.get_logger().info(
            "Behavior Manager Client Node Started"
        )

    # =============================================================
    # Callback
    # =============================================================

    def behavior_callback(self, msg: String):

        command = msg.data.strip()

        self.get_logger().info(
            f"Received command: {command}"
        )

        motion_file = self.behavior_manager.get_motion_file(
            command
        )

        if motion_file is None:

            self.get_logger().error(
                f"Unknown behavior: {command}"
            )

            return

        self.execute_motion(motion_file)

    # =============================================================
    # Execute motion
    # =============================================================

    def execute_motion(self, motion_file: str):

        self.get_logger().info(
            f"Executing motion: {motion_file}"
        )

        command = [
            "ros2",
            "launch",
            self.motion_launch_package,
            self.motion_launch_file,
            f"sequence_file:={motion_file}"
        ]

        subprocess.Popen(command)


def main(args=None):

    rclpy.init(args=args)

    node = BehaviorManagerClientNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()