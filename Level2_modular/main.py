from config import CONFIG
from ur5e_social_motion import RobotController
from social_robot_hri import VoiceInterface
from chatgpt_interpreter import ChatGPTInterpreter
from social_robot_perception import FaceIdentifier


class SocialRobotApp:

    def __init__(self):
        self.robot = RobotController(
            use_real_robot=CONFIG.USE_REAL_ROBOT,
            robot_ip=CONFIG.ROBOT_IP,
            robot_port=CONFIG.ROBOT_PORT,
        )
        self.voice = VoiceInterface()
        self.gpt = ChatGPTInterpreter()
        self.face = FaceIdentifier()

        self.user = "friend"

    def start(self) -> None:
        try:
            self.voice.speak("Starting voice control.")
            self.user = self.face.identify_once()
            self.voice.speak(f"Hello {self.user}")

            while True:
                spoken = self.voice.listen()
                command = self.gpt.interpret(spoken)

                if command is None:
                    continue

                if command == "unknown":
                    print("Command not understood.")
                    continue

                if command == "exit":
                    self.voice.speak(f"Goodbye {self.user}")
                    self.voice.speak("Returning to safe init position.")
                    self.robot.go_to_init()
                    return

                result = self.robot.execute(command)
                if result:
                    self.voice.speak(result)
                    self.voice.speak(f"I am ready for the next command {self.user}")
        finally:
            self.robot.shutdown()


if __name__ == "__main__":
    app = SocialRobotApp()
    app.start()
