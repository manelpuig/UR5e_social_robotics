#!/usr/bin/env python3

import math

import rclpy
from rclpy.duration import Duration as RclpyDuration
from rclpy.node import Node
from rclpy.time import Time

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from tf2_ros import Buffer, TransformException, TransformListener


def euler_from_quaternion(qx, qy, qz, qw):
    """Return roll, pitch and yaw (radians) from an XYZW quaternion."""
    sinr_cosp = 2.0 * (qw * qx + qy * qz)
    cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (qw * qy - qz * qx)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


class MoveUR5e(Node):

    def __init__(self):
        super().__init__("move_ur5e_joint_target")

        self.declare_parameter(
            "target_deg",
            [0.0, -90.0, 90.0, 0.0, 90.0, 0.0]
        )
        self.declare_parameter(
            "time_sec",
            5.0
        )
        self.declare_parameter(
            "controller_topic",
            "/scaled_joint_trajectory_controller/joint_trajectory"
        )
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("tcp_frame", "tool0")
        self.declare_parameter("tf_timeout_sec", 2.0)

        self.target_deg = self.get_parameter("target_deg").value
        self.time_sec = float(self.get_parameter("time_sec").value)
        self.controller_topic = str(
            self.get_parameter("controller_topic").value
        )
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.tcp_frame = str(self.get_parameter("tcp_frame").value)
        self.tf_timeout_sec = float(
            self.get_parameter("tf_timeout_sec").value
        )

        if len(self.target_deg) != 6:
            self.get_logger().error(
                "Parameter 'target_deg' must contain exactly 6 values"
            )
            raise RuntimeError("Invalid target_deg length")

        self.pub = self.create_publisher(
            JointTrajectory,
            self.controller_topic,
            10
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.get_logger().info(
            f"Publishing trajectory to: {self.controller_topic}"
        )

        self.start_timer = self.create_timer(1.0, self.send_trajectory)
        self.shutdown_timer = None

        self.sent = False
        self.done = False

    def send_trajectory(self):
        if self.sent:
            return

        target_rad = [math.radians(x) for x in self.target_deg]

        msg = JointTrajectory()
        msg.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        point = JointTrajectoryPoint()
        point.positions = target_rad

        secs = int(self.time_sec)
        nsecs = int((self.time_sec - secs) * 1e9)
        point.time_from_start = Duration(sec=secs, nanosec=nsecs)

        msg.points.append(point)

        self.pub.publish(msg)

        self.get_logger().info(f"Published target_deg = {self.target_deg}")
        self.get_logger().info(f"Published target_rad = {target_rad}")
        self.get_logger().info(f"Waiting {self.time_sec} s before closing node")

        self.sent = True
        self.start_timer.cancel()
        self.shutdown_timer = self.create_timer(self.time_sec, self.finish_node)

    def finish_node(self):
        self.get_logger().info("Motion time finished. Reading TCP pose from TF.")

        try:
            transform = self.tf_buffer.lookup_transform(
                self.base_frame,
                self.tcp_frame,
                Time(),
                timeout=RclpyDuration(seconds=self.tf_timeout_sec),
            )

            translation = transform.transform.translation
            rotation = transform.transform.rotation
            roll, pitch, yaw = euler_from_quaternion(
                rotation.x,
                rotation.y,
                rotation.z,
                rotation.w,
            )

            self.get_logger().info(
                f"TCP pose ({self.base_frame} -> {self.tcp_frame})"
            )
            self.get_logger().info(
                "  position [m]: "
                f"x={translation.x:.6f}, y={translation.y:.6f}, "
                f"z={translation.z:.6f}"
            )
            self.get_logger().info(
                "  quaternion [x, y, z, w]: "
                f"[{rotation.x:.6f}, {rotation.y:.6f}, "
                f"{rotation.z:.6f}, {rotation.w:.6f}]"
            )
            self.get_logger().info(
                "  RPY [deg]: "
                f"roll={math.degrees(roll):.3f}, "
                f"pitch={math.degrees(pitch):.3f}, "
                f"yaw={math.degrees(yaw):.3f}"
            )
        except TransformException as error:
            self.get_logger().error(
                f"Could not obtain transform {self.base_frame} -> "
                f"{self.tcp_frame}: {error}"
            )

        self.get_logger().info("Closing node.")
        if self.shutdown_timer is not None:
            self.shutdown_timer.cancel()
        self.done = True


def main(args=None):
    rclpy.init(args=args)
    node = MoveUR5e()

    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
