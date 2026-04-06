import rclpy
from rclpy.node import Node

from social_robot_lib.hri.speech_listener import listen
from social_robot_lib.hri.tts_engine import speak
from social_robot_lib.hri.wakeword import detect_wakeword

from social_robot_lib.perception.face_identifier import identify_person

from social_robot_lib.interaction.command_router import route_command
from social_robot_lib.interaction.conversation_manager import (
    greeting,
    confirmation
)


class SocialBehaviorManager(Node):

    def __init__(self):
        super().__init__('social_behavior_manager')

        self.get_logger().info("Social behavior manager started")

        self.run_main_loop()


    def run_main_loop(self):

        # Step 1: detect person
        person = identify_person()

        greet_text = greeting(person)
        speak(greet_text)

        while rclpy.ok():

            # Step 2: listen
            text = listen()

            if text is None:
                continue

            activated, command_text = detect_wakeword(text)

            if not activated:
                continue

            self.get_logger().info(f"Command detected: {command_text}")

            # Step 3: interpret command
            command = route_command(command_text)

            self.get_logger().info(f"Intent: {command}")

            # Step 4: confirm action
            speak(confirmation(command))

            # Step 5: execute motion
            self.execute_motion(command)

            if command == "exit":
                break


    def execute_motion(self, command):

        """
        This function will later call ur5e_social_motion.
        For now it prints the requested behavior.
        """

        if command == "init":
            self.get_logger().info("Executing INIT motion")

        elif command == "hand_shake":
            self.get_logger().info("Executing HANDSHAKE motion")

        elif command == "give_me_5":
            self.get_logger().info("Executing HIGH FIVE motion")

        elif command == "exit":
            self.get_logger().info("Exit command received")

        else:
            self.get_logger().info("Unknown command")


def main(args=None):

    rclpy.init(args=args)

    node = SocialBehaviorManager()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()