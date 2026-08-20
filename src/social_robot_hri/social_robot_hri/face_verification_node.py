#!/usr/bin/env python3
"""Authorise once by face, then gate HRI behavior requests."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from social_robot_hri.face_verification import FaceVerifier


class FaceVerificationNode(Node):
    def __init__(self):
        super().__init__('face_verification_node')
        self.declare_parameter('reference_image', '')
        self.declare_parameter('camera_index', 0)
        self.declare_parameter('tolerance', 0.6)
        self.declare_parameter('input_topic', '/social_behavior/request')
        self.declare_parameter('output_topic', '/social_behavior')

        reference_image = str(self.get_parameter('reference_image').value)
        if not reference_image:
            raise RuntimeError('Set the reference_image ROS parameter.')

        verifier = FaceVerifier(
            reference_image,
            camera_index=int(self.get_parameter('camera_index').value),
            tolerance=float(self.get_parameter('tolerance').value),
        )
        self.authorised = verifier.verify()
        if not self.authorised:
            self.get_logger().error('Face verification failed. Requests are blocked.')
        else:
            self.get_logger().info('User authorised. HRI requests are enabled.')

        self.publisher_ = self.create_publisher(
            String, str(self.get_parameter('output_topic').value), 10
        )
        self.subscription = self.create_subscription(
            String,
            str(self.get_parameter('input_topic').value),
            self.request_callback,
            10,
        )

    def request_callback(self, msg):
        if not self.authorised:
            self.get_logger().warn('Rejected behavior request: user not authorised.')
            return
        self.publisher_.publish(msg)
        self.get_logger().info(f'Authorised behavior: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = FaceVerificationNode()
        rclpy.spin(node)
    except (RuntimeError, FileNotFoundError) as error:
        print(f'[FACE] {error}')
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
