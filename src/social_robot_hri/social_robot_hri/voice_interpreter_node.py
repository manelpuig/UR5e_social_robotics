#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class VoiceInterpreterNode(Node):

    def __init__(self):
        super().__init__('voice_interpreter_node')

        self.declare_parameter('activation_word', 'robot')
        self.declare_parameter('output_topic', '/social_behavior')

        self.subscription = self.create_subscription(
            String,
            '/voice/text',
            self.voice_callback,
            10
        )

        self.publisher_ = self.create_publisher(
            String,
            str(self.get_parameter('output_topic').value),
            10
        )

        self.get_logger().info('Voice interpreter node started.')

    def voice_callback(self, msg: String):
        text = msg.data.lower().strip()

        command = self.interpret_text(text)

        if command is None:
            self.get_logger().warn(f'Unknown voice command: {text}')
            return

        out_msg = String()
        out_msg.data = command
        self.publisher_.publish(out_msg)

        self.get_logger().info(
            f'Voice text "{text}" interpreted as command "{command}"'
        )

    def interpret_text(self, text: str):

        activation_word = str(
            self.get_parameter('activation_word').value
        ).lower().strip()

        if activation_word:
            if not text.startswith(activation_word):
                return None
            text = text[len(activation_word):].strip()

        if 'init' in text or 'home' in text:
            return 'init'

        if 'shake' in text or 'hand' in text:
            return 'handshake'

        if 'five' in text or 'give me five' in text or 'give5' in text:
            return 'give5'

        if 'stop' in text:
            return 'stop'

        return None


def main(args=None):
    rclpy.init(args=args)
    node = VoiceInterpreterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
