#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class VoiceNode(Node):

    def __init__(self):
        super().__init__('voice_node')

        self.publisher_ = self.create_publisher(
            String,
            '/voice/text',
            10
        )

        self.get_logger().info('Voice node started.')
        self.get_logger().info('Type voice commands manually for now.')

        self.timer = self.create_timer(0.5, self.read_command)

    def read_command(self):
        text = input('Voice text > ')

        msg = String()
        msg.data = text
        self.publisher_.publish(msg)

        self.get_logger().info(f'Published voice text: {text}')


def main(args=None):
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()