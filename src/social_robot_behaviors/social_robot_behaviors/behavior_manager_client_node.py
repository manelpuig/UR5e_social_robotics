#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from ur5e_interfaces.srv import RunSequence
import re


class BehaviorManagerClientNode(Node):

    def __init__(self):

        super().__init__("behavior_manager_client_node")

        # ---------------------------------------------------------
        # Parameters
        # ---------------------------------------------------------

        self.declare_parameter(
            "service_name",
            "/ur5e/run_sequence"
        )

        self.service_name = self.get_parameter(
            "service_name"
        ).value

        # ---------------------------------------------------------
        # Service client
        # ---------------------------------------------------------

        self.sequence_client = self.create_client(
            RunSequence,
            self.service_name
        )

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

        self.get_logger().info(
            f"Waiting for service: {self.service_name}"
        )

    # =============================================================
    # Topic callback
    # =============================================================

    def behavior_callback(self, msg: String):

        behavior_name = msg.data.strip()

        self.get_logger().info(
            f"Received social behavior: {behavior_name}"
        )

        if not re.fullmatch(r"[A-Za-z0-9_-]+", behavior_name):

            self.get_logger().error(
                f"Invalid behavior name: {behavior_name}"
            )

            return

        if not self.sequence_client.service_is_ready():

            self.get_logger().error(
                f"Service not available: {self.service_name}"
            )

            return

        request = RunSequence.Request()
        request.sequence_name = behavior_name

        self.get_logger().info(
            f"Requesting sequence: {behavior_name}"
        )

        future = self.sequence_client.call_async(request)

        future.add_done_callback(
            self.sequence_response_callback
        )

    # =============================================================
    # Service response callback
    # =============================================================

    def sequence_response_callback(self, future):

        try:

            response = future.result()

        except Exception as exc:

            self.get_logger().error(
                f"Service call failed: {exc}"
            )

            return

        if response.success:

            self.get_logger().info(
                f"Sequence accepted: {response.message}"
            )

        else:

            self.get_logger().error(
                f"Sequence rejected: {response.message}"
            )


def main(args=None):

    rclpy.init(args=args)

    node = BehaviorManagerClientNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()