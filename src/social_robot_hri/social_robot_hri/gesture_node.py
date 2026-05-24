#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class GestureNode(Node):

    def __init__(self):
        super().__init__('gesture_node')
        self.get_logger().info('Gesture node placeholder started.')
        self.get_logger().info('Future node for YOLO-pose detection.')


def main(args=None):
    rclpy.init(args=args)
    node = GestureNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()