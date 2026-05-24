#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from ur5e_interfaces.srv import RunJoints


class UR5eFkineClient(Node):

    def __init__(self):
        super().__init__("ur5e_fkine_client")

        self.declare_parameter("service_name", "/ur5e_fkine_server")

        self.declare_parameter(
            "joints",
            [-60.0, -60.0, -100.0, 170.0, -60.0, 0.0]
        )

        self.declare_parameter("execute", True)
        self.declare_parameter("max_velocity", 0.1)
        self.declare_parameter("max_acceleration", 0.1)

        service_name = self.get_parameter("service_name").value

        self.client = self.create_client(
            RunJoints,
            service_name
        )

    def call_server(self):
        service_name = self.get_parameter("service_name").value

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                f"Waiting for service {service_name}..."
            )

        req = RunJoints.Request()

        req.joints_deg = [
            float(v) for v in self.get_parameter("joints").value
        ]

        req.execute = bool(
            self.get_parameter("execute").value
        )

        req.max_velocity = float(
            self.get_parameter("max_velocity").value
        )

        req.max_acceleration = float(
            self.get_parameter("max_acceleration").value
        )

        self.get_logger().info(f"joints_deg: {req.joints_deg}")
        self.get_logger().info(f"execute: {req.execute}")
        self.get_logger().info(f"max_velocity: {req.max_velocity}")
        self.get_logger().info(f"max_acceleration: {req.max_acceleration}")

        future = self.client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()

        if response is None:
            self.get_logger().error("Service call failed.")
            return

        self.get_logger().info(f"success: {response.success}")
        self.get_logger().info(f"message: {response.message}")


def main(args=None):
    rclpy.init(args=args)

    node = UR5eFkineClient()
    node.call_server()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()