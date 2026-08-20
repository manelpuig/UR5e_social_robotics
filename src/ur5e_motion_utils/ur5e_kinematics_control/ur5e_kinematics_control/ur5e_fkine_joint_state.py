#!/usr/bin/env python3

import math

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time

from sensor_msgs.msg import JointState
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


class UR5eFkineJointState(Node):

    def __init__(self):
        super().__init__("ur5e_fkine_joint_state")

        self.declare_parameter(
            "target_deg",
            [0.0, -90.0, 90.0, 0.0, 90.0, 0.0],
        )
        self.declare_parameter("joint_states_topic", "/joint_states")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("tcp_frame", "tool0")
        self.declare_parameter("publish_duration_sec", 1.0)
        self.declare_parameter("tf_timeout_sec", 2.0)

        self.target_deg = [
            float(value)
            for value in self.get_parameter("target_deg").value
        ]
        self.joint_states_topic = str(
            self.get_parameter("joint_states_topic").value
        )
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.tcp_frame = str(self.get_parameter("tcp_frame").value)
        self.publish_duration_sec = float(
            self.get_parameter("publish_duration_sec").value
        )
        self.tf_timeout_sec = float(
            self.get_parameter("tf_timeout_sec").value
        )

        if len(self.target_deg) != 6:
            raise RuntimeError(
                "Parameter 'target_deg' must contain exactly 6 values"
            )
        if self.publish_duration_sec <= 0.0:
            raise RuntimeError("Parameter 'publish_duration_sec' must be positive")

        self.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]
        self.target_rad = [math.radians(value) for value in self.target_deg]

        self.publisher = self.create_publisher(
            JointState,
            self.joint_states_topic,
            10,
        )
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.started_at = self.get_clock().now()
        self.done = False
        self.pose_printed = False
        self.publish_timer = self.create_timer(0.1, self.publish_joint_state)

        self.get_logger().info(f"Target joints [deg]: {self.target_deg}")
        self.get_logger().info(f"Target joints [rad]: {self.target_rad}")
        self.get_logger().info(
            f"Publishing target on {self.joint_states_topic}. "
            "Close joint_state_publisher_gui to avoid multiple publishers."
        )

    def publish_joint_state(self):
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = self.joint_names
        message.position = self.target_rad
        self.publisher.publish(message)

        elapsed = (self.get_clock().now() - self.started_at).nanoseconds * 1e-9
        if elapsed >= self.publish_duration_sec and not self.pose_printed:
            self.print_tcp_pose()

    def print_tcp_pose(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.base_frame,
                self.tcp_frame,
                Time(),
                timeout=Duration(seconds=self.tf_timeout_sec),
            )
        except TransformException as error:
            self.get_logger().error(
                f"Could not obtain transform {self.base_frame} -> "
                f"{self.tcp_frame}: {error}"
            )
            self.finish()
            return

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
        self.finish()

    def finish(self):
        self.pose_printed = True
        self.publish_timer.cancel()
        self.done = True


def main(args=None):
    rclpy.init(args=args)
    node = UR5eFkineJointState()

    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
