#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class GestureInterpreterNode(Node):

    def __init__(self):
        super().__init__('gesture_interpreter_node')
        self.get_logger().info('Gesture interpreter placeholder started.')
        self.get_logger().info('Future node to convert gestures into robot commands.')


def main(args=None):
    rclpy.init(args=args)
    node = GestureInterpreterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()