import rclpy
from rclpy.node import Node

from social_robot_lib.hri.speech_listener import listen
from social_robot_lib.hri.tts_engine import speak
from social_robot_lib.hri.wakeword import detect_wakeword

from social_robot_lib.perception.face_identifier import identify_person

from social_robot_lib.interaction.command_router import route_command
from social_robot_lib.interaction.conversation_manager import (
    greeting,
    confirmation,
)

from social_robot_behaviors.init_behavior import execute_init_behavior
from social_robot_behaviors.handshake_behavior import execute_handshake_behavior
from social_robot_behaviors.highfive_behavior import execute_highfive_behavior


class SocialBehaviorManager(Node):

    def __init__(self):
        super().__init__("social_behavior_manager")
        self.get_logger().info("Social behavior manager started")

        self.run_main_loop()

    def run_main_loop(self):
        person = identify_person()
        speak(greeting(person))

        while rclpy.ok():
            text = listen()

            if text is None:
                continue

            activated, command_text = detect_wakeword(text)

            if not activated:
                continue

            self.get_logger().info(f"Command detected: {command_text}")

            command = route_command(command_text)
            self.get_logger().info(f"Intent: {command}")

            speak(confirmation(command))

            self.execute_behavior(command)

            if command == "exit":
                break

    def execute_behavior(self, command: str):
        if command == "init":
            execute_init_behavior(logger=self.get_logger())

        elif command == "hand_shake":
            execute_handshake_behavior(logger=self.get_logger())

        elif command == "give_me_5":
            execute_highfive_behavior(logger=self.get_logger())

        elif command == "exit":
            self.get_logger().info("Exit command received")

        else:
            self.get_logger().info("Unknown command")


def main(args=None):
    rclpy.init(args=args)

    node = SocialBehaviorManager()

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()