#!/usr/bin/env python3

import subprocess

import rclpy
from rclpy.node import Node

from ur5e_interfaces.srv import RunJoints


class UR5eFkineServer(Node):

    def __init__(self):
        super().__init__("ur5e_fkine_server")

        self.declare_parameter("launch_package", "ur5e_robot_controller")
        self.declare_parameter("launch_file", "ur5e_fkine.launch.py")

        self.launch_package = self.get_parameter("launch_package").value
        self.launch_file = self.get_parameter("launch_file").value

        self.srv = self.create_service(
            RunJoints,
            "/ur5e/run_fkine",
            self.run_fkine_callback,
        )

        self.get_logger().info("UR5e fkine server ready.")
        self.get_logger().info("Service: /ur5e/run_fkine")
        self.get_logger().info(
            f"Launch target: {self.launch_package} {self.launch_file}"
        )

    def run_fkine_callback(self, request, response):

        try:
            joints_deg = [float(v) for v in request.joints_deg]

            cmd = [
                "ros2",
                "launch",
                self.launch_package,
                self.launch_file,

                f"joints:={joints_deg}",
                f"execute:={str(request.execute).lower()}",
                f"max_velocity:={float(request.max_velocity)}",
                f"max_acceleration:={float(request.max_acceleration)}",
            ]

            self.get_logger().info("Executing fkine using launch command:")
            self.get_logger().info(" ".join(cmd))

            subprocess.Popen(cmd)

            response.success = True
            response.message = "Fkine launch started."

        except Exception as e:
            response.success = False
            response.message = f"Exception: {e}"

        return response


def main():

    rclpy.init()

    node = UR5eFkineServer()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()