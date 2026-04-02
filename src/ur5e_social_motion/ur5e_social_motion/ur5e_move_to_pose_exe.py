#!/usr/bin/env python3

import math
import sys

import rclpy
from rclpy.node import Node


class UR5eMoveToPoseNode(Node):
    def __init__(self):
        super().__init__("ur5e_move_to_pose")

        self.declare_parameter("step_name", "unnamed_step")
        self.declare_parameter("target_xyz_m", [0.0, 0.0, 0.0])
        self.declare_parameter("target_rpy_deg", [0.0, 0.0, 0.0])

        self.declare_parameter("seed_joints_deg", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter("use_seed_joints", False)

        self.declare_parameter("execute", True)
        self.declare_parameter("group_name", "ur_manipulator")
        self.declare_parameter("ik_link_name", "tool0")
        self.declare_parameter("reference_frame", "table")

        self.step_name = self.get_parameter("step_name").value
        self.target_xyz_m = list(self.get_parameter("target_xyz_m").value)
        self.target_rpy_deg = list(self.get_parameter("target_rpy_deg").value)
        self.seed_joints_deg = list(self.get_parameter("seed_joints_deg").value)
        self.use_seed_joints = bool(self.get_parameter("use_seed_joints").value)
        self.execute = bool(self.get_parameter("execute").value)
        self.group_name = self.get_parameter("group_name").value
        self.ik_link_name = self.get_parameter("ik_link_name").value
        self.reference_frame = self.get_parameter("reference_frame").value

        self._validate_inputs()

        self.target_rpy_rad = [math.radians(v) for v in self.target_rpy_deg]
        self.seed_joints_rad = [math.radians(v) for v in self.seed_joints_deg] if self.use_seed_joints else []

        self._print_summary()

        if self.execute:
            self.get_logger().info("Execution is enabled, but motion backend is not connected yet.")
        else:
            self.get_logger().info("Execution disabled for this step.")

        self._finished = False
        self._timer = self.create_timer(0.5, self._finish_once)

    def _validate_inputs(self):
        if len(self.target_xyz_m) != 3:
            raise ValueError("Parameter 'target_xyz_m' must contain exactly 3 values.")

        if len(self.target_rpy_deg) != 3:
            raise ValueError("Parameter 'target_rpy_deg' must contain exactly 3 values.")

        if len(self.seed_joints_deg) != 6:
            raise ValueError("Parameter 'seed_joints_deg' must contain exactly 6 values.")

    def _print_summary(self):
        self.get_logger().info("=" * 60)
        self.get_logger().info(f"Step name         : {self.step_name}")
        self.get_logger().info(f"Reference frame   : {self.reference_frame}")
        self.get_logger().info(f"Group name        : {self.group_name}")
        self.get_logger().info(f"IK link name      : {self.ik_link_name}")
        self.get_logger().info(f"Target XYZ [m]    : {[round(v, 4) for v in self.target_xyz_m]}")
        self.get_logger().info(f"Target RPY [deg]  : {self.target_rpy_deg}")
        self.get_logger().info(f"Target RPY [rad]  : {[round(v, 4) for v in self.target_rpy_rad]}")
        self.get_logger().info(f"Use seed joints   : {self.use_seed_joints}")

        if self.use_seed_joints:
            self.get_logger().info(f"Seed joints [deg] : {self.seed_joints_deg}")
            self.get_logger().info(f"Seed joints [rad] : {[round(v, 4) for v in self.seed_joints_rad]}")

        self.get_logger().info(f"Execute           : {self.execute}")
        self.get_logger().info("=" * 60)

    def _finish_once(self):
        if self._finished:
            return

        self._finished = True
        self.get_logger().info(f"Finished step: {self.step_name}")
        self.destroy_timer(self._timer)
        self.destroy_node()


def main():
    rclpy.init()
    node = UR5eMoveToPoseNode()

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            if node._finished:
                break
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()

    sys.exit(0)


if __name__ == "__main__":
    main()