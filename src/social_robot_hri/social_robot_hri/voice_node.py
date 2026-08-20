#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import speech_recognition as sr


class VoiceNode(Node):

    def __init__(self):
        super().__init__('voice_node')

        self.publisher_ = self.create_publisher(
            String,
            '/voice/text',
            10
        )

        self.declare_parameter('language', 'en-US')
        self.declare_parameter('timeout', 5.0)
        self.declare_parameter('phrase_time_limit', 4.0)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        with self.microphone as source:
            self.get_logger().info('Calibrating microphone...')
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

        self.get_logger().info('Voice node started.')
        self.get_logger().info('Say a command after the listening prompt.')

        self.timer = self.create_timer(0.5, self.read_command)

    def read_command(self):
        try:
            with self.microphone as source:
                self.get_logger().info('Listening...')
                audio = self.recognizer.listen(
                    source,
                    timeout=float(self.get_parameter('timeout').value),
                    phrase_time_limit=float(
                        self.get_parameter('phrase_time_limit').value
                    ),
                )
            text = self.recognizer.recognize_google(
                audio,
                language=str(self.get_parameter('language').value),
            )
        except sr.WaitTimeoutError:
            return
        except sr.UnknownValueError:
            self.get_logger().warn('Speech not understood.')
            return
        except sr.RequestError as error:
            self.get_logger().error(f'Speech-recognition service error: {error}')
            return

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
