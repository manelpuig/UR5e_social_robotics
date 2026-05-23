from robodk.robolink import *
from robodk.robomath import *

import os
import time
import re
import cv2
import numpy as np
import face_recognition
import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv
import socket

#Load environment variables from .env file (if exists)
load_dotenv()

# =====================================================
# CONFIGURATION CLASS
# =====================================================

class CONFIG:

    USE_REAL_ROBOT = True
    ROBOT_IP = "192.168.1.4"
    ROBOT_PORT = 30002

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GPT_MODEL = "gpt-5.4-mini"

    # Activation word
    ACTIVATION_WORD = "robot"

    # Speech
    LANGUAGE = "en-US"
    TTS_RATE = 170

    # RoboDK
    RDK_FILE = "src/roboDK/Social_UR5e.rdk"

    # Known faces
    KNOWN_FACES = {
        "Manel": "Documentation/Files/pictures/Manel_ref.png"
    }

    # Camera
    CAMERA_INDEX = 0


# =====================================================
# ROBOT CONTROLLER
# =====================================================

class RobotController:

    def __init__(self,
                 use_real_robot=True,
                 robot_ip="192.168.1.4",
                 robot_port=30002):

        self.use_real_robot = use_real_robot
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.robot_socket = None
        self.real_robot_connected = False

        print("Loading RoboDK...")
        self.rdk = Robolink()
        time.sleep(2)

        self.rdk.AddFile(os.path.abspath(CONFIG.RDK_FILE))
        print("Loading RoboDK project...")
        time.sleep(2)

        # Important: do NOT recreate Robolink() here
        self.robot = self.rdk.Item("UR5e")
        self.base = self.rdk.Item("UR5e Base")
        self.tool = self.rdk.Item("Hand")

        self.init_target = self.rdk.Item("Init")
        self.app_shake_target = self.rdk.Item("App_shake")
        self.shake_target = self.rdk.Item("Shake")
        self.app_give5_target = self.rdk.Item("App_give5")
        self.give5_target = self.rdk.Item("Give5")

        self.robot.setPoseFrame(self.base)
        self.robot.setPoseTool(self.tool)
        self.robot.setSpeed(20)

        if self.use_real_robot:
            self.connect_robot()
            if self.real_robot_connected:
                self.set_tcp_from_robodk(wait_time=1.0)

    # -------------------------------------------------
    # SOCKET COMMUNICATION
    # -------------------------------------------------

    def connect_robot(self):
        """Open a TCP socket to the real UR robot."""
        try:
            self.robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.robot_socket.settimeout(2.0)
            self.robot_socket.connect((self.robot_ip, self.robot_port))
            self.real_robot_connected = True
            print(f"Connected to real robot at {self.robot_ip}:{self.robot_port}")
            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"Connection to real robot failed: {e}")
            self.robot_socket = None
            self.real_robot_connected = False
            return False

    def send_script(self, script: str, wait_time: float = 0.0) -> bool:
        """
        Send one URScript command to the real robot.
        Returns True if sent correctly, False otherwise.
        """
        if not (self.real_robot_connected and self.robot_socket):
            print("Real robot not connected. Script not sent.")
            return False

        try:
            self.robot_socket.sendall((script.strip() + "\n").encode("utf-8"))
            print(f"[URSCRIPT] {script}")
            if wait_time > 0:
                time.sleep(wait_time)
            return True
        except Exception as e:
            print(f"Error sending script: {e}")
            self.real_robot_connected = False
            return False

    def close_robot_connection(self):
        """Close the TCP socket to the real robot."""
        if self.robot_socket:
            try:
                self.robot_socket.close()
                print("Socket connection to robot closed.")
            except Exception as e:
                print(f"Error closing robot socket: {e}")
            finally:
                self.robot_socket = None
                self.real_robot_connected = False

    # -------------------------------------------------
    # TARGET-BASED MOTION HELPERS
    # -------------------------------------------------

    def movej_target(self, target, time_param=5.0, accel=1.2, speed=0.75, blend=0.0):
        """
        Joint move to a RoboDK target.
        In real mode -> send movej by socket.
        In simulation mode -> RoboDK MoveJ.
        """
        if self.real_robot_connected and self.robot_socket:
            try:
                joints_deg = target.Joints().tolist()[0]
                joints_rad = np.radians(joints_deg)

                script = (
                    f"movej([{joints_rad[0]:.6f},{joints_rad[1]:.6f},{joints_rad[2]:.6f},"
                    f"{joints_rad[3]:.6f},{joints_rad[4]:.6f},{joints_rad[5]:.6f}], "
                    f"a={accel}, v={speed}, t={time_param}, r={blend})"
                )
                return self.send_script(script, wait_time=time_param)
            except Exception as e:
                print(f"Error preparing movej command: {e}")
                return False
        else:
            try:
                print("Simulating MoveJ in RoboDK.")
                self.robot.MoveJ(target, True)
                return True
            except Exception as e:
                print(f"Simulation MoveJ failed: {e}")
                return False

    def movel_target(self, target, time_param=5.0, accel=1.2, speed=0.25, blend=0.0):
        """
        Linear move to a RoboDK target.
        In real mode -> send movel by socket.
        In simulation mode -> RoboDK MoveL.
        """
        if self.real_robot_connected and self.robot_socket:
            try:
                x, y, z, rx, ry, rz = Pose_2_UR(target.Pose())

                script = (
                    f"movel(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
                    f"{rx:.6f},{ry:.6f},{rz:.6f}], "
                    f"a={accel}, v={speed}, t={time_param}, r={blend})"
                )
                return self.send_script(script, wait_time=time_param)
            except Exception as e:
                print(f"Error preparing movel command: {e}")
                return False
        else:
            try:
                print("Simulating MoveL in RoboDK.")
                self.robot.MoveL(target, True)
                return True
            except Exception as e:
                print(f"Simulation MoveL failed: {e}")
                return False

    def set_tcp_from_robodk(self, wait_time=1.0):
        """
        Read TCP from RoboDK tool and send set_tcp() to the real robot.
        In simulation mode just set the tool in RoboDK.
        """
        if self.real_robot_connected and self.robot_socket:
            try:
                x, y, z, rx, ry, rz = Pose_2_UR(self.robot.PoseTool())
                script = (
                    f"set_tcp(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
                    f"{rx:.6f},{ry:.6f},{rz:.6f}])"
                )
                return self.send_script(script, wait_time=wait_time)
            except Exception as e:
                print(f"Error sending set_tcp: {e}")
                return False
        else:
            try:
                print("Setting TCP in RoboDK simulation.")
                self.robot.setPoseTool(self.tool)
                time.sleep(wait_time)
                return True
            except Exception as e:
                print(f"Error setting TCP in simulation: {e}")
                return False

    # -------------------------------------------------
    # HIGH-LEVEL COMMANDS
    # -------------------------------------------------

    def execute(self, command):

        if command == "init":
            ok = self.movej_target(self.init_target, time_param=5.0)
            return "Init finished" if ok else "Init failed"

        if command == "hand_shake":
            ok1 = self.movel_target(self.app_shake_target, time_param=3.0)
            ok2 = self.movel_target(self.shake_target, time_param=1.0)
            ok3 = self.movel_target(self.app_shake_target, time_param=1.0)
            return "Hand shake finished" if (ok1 and ok2 and ok3) else "Hand shake failed"

        if command == "give_me_5":
            ok1 = self.movel_target(self.app_give5_target, time_param=3.0)
            ok2 = self.movel_target(self.give5_target, time_param=1.0)
            ok3 = self.movel_target(self.app_give5_target, time_param=1.0)
            return "Give me five finished" if (ok1 and ok2 and ok3) else "Give me five failed"

        return None

    def go_to_init(self):
        """Move robot to safe Init pose."""
        try:
            return self.movej_target(self.init_target, time_param=5.0)
        except Exception as e:
            print(f"Error moving to Init: {e}")
            return False

    def shutdown(self):
        """Close robot socket and RoboDK cleanly."""
        try:
            self.close_robot_connection()
        except Exception as e:
            print(f"Error closing robot connection: {e}")

        try:
            print("Closing RoboDK...")
            self.rdk.CloseRoboDK()
        except Exception as e:
            print(f"Error closing RoboDK: {e}")
# =====================================================
# VOICE INTERFACE
# =====================================================

class VoiceInterface:

    def __init__(self):

        self.recognizer = sr.Recognizer()

    def speak(self, text):

        print(f"[TTS] {text}")

        engine = pyttsx3.init("sapi5")
        engine.setProperty("rate", CONFIG.TTS_RATE)

        voices = engine.getProperty("voices")

        if voices:
            engine.setProperty("voice", voices[0].id)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

        time.sleep(0.4)

    def listen(self):

        with sr.Microphone() as source:

            print("Listening...")

            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = self.recognizer.listen(source)

        try:

            text = self.recognizer.recognize_google(
                audio,
                language=CONFIG.LANGUAGE
            )

            print(f"[USER] {text}")

            return text

        except:
            return None


# =====================================================
# CHATGPT COMMAND INTERPRETER
# =====================================================

class ChatGPTInterpreter:
    """Use local parsing first, and GPT only as fallback."""

    def __init__(self):

        if not CONFIG.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not found. GPT fallback disabled.")

        self.client = OpenAI(api_key=CONFIG.OPENAI_API_KEY) if CONFIG.OPENAI_API_KEY else None
        print("OPENAI_API_KEY loaded:", CONFIG.OPENAI_API_KEY is not None)

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = text.replace("-", " ")
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def local_interpret(self, text: str | None) -> str | None:
        """Fast local parser without API."""
        if text is None:
            return None

        text = self.normalize_text(text)

        if not text.startswith(CONFIG.ACTIVATION_WORD):
            return None

        text = text[len(CONFIG.ACTIVATION_WORD):].strip()

        if any(k in text for k in ["exit", "quit", "stop"]):
            return "exit"

        if any(k in text for k in [
            "init",
            "home",
            "go home",
            "initial position",
            "start position"
        ]):
            return "init"

        if any(k in text for k in [
            "hand shake",
            "shake hand",
            "handshake",
            "shake my hand",
            "lets shake hands",
            "greet me"
        ]):
            return "hand_shake"

        if any(k in text for k in [
            "give me five",
            "give me 5",
            "high five",
            "give me a high five",
            "lets do a high five"
        ]):
            return "give_me_5"

        return "unknown"

    def gpt_interpret(self, text: str | None) -> str | None:
        """Fallback parser using OpenAI API."""
        if self.client is None:
            return "unknown"
        
        if text is None:
            return None

        text = self.normalize_text(text)

        if not text.startswith(CONFIG.ACTIVATION_WORD):
            return None

        instructions = """
                        You are a command interpreter for a social robot.

                        Allowed commands:
                        init
                        hand_shake
                        give_me_5
                        exit
                        unknown

                        Return only one command word.
                        """

        try:
            response = self.client.responses.create(
                model=CONFIG.GPT_MODEL,
                instructions=instructions,
                input=text
            )

            command = response.output_text.strip()
            print("[GPT]", command)

            allowed = {"init", "hand_shake", "give_me_5", "exit", "unknown"}

            if command in allowed:
                return command

            return "unknown"

        except Exception as e:
            print(f"[GPT ERROR] {e}")
            return "unknown"

    def interpret(self, text: str | None) -> str | None:
        """
        1. Try local parser
        2. If local parser returns unknown, try GPT
        3. If GPT fails, return unknown
        """
        local_command = self.local_interpret(text)

        if local_command is None:
            return None

        if local_command != "unknown":
            print("[LOCAL]", local_command)
            return local_command

        print("[LOCAL] unknown -> trying GPT fallback")
        return self.gpt_interpret(text)

# =====================================================
# FACE IDENTIFIER
# =====================================================

class FaceIdentifier:

    def __init__(self):

        self.encodings = []
        self.names = []

        for name, path in CONFIG.KNOWN_FACES.items():

            if not os.path.exists(path):
                continue

            img = face_recognition.load_image_file(path)

            enc = face_recognition.face_encodings(img)

            if enc:
                self.encodings.append(enc[0])
                self.names.append(name)

    def identify_once(self):

        cap = cv2.VideoCapture(CONFIG.CAMERA_INDEX)

        time.sleep(1)

        ret, frame = cap.read()

        cap.release()

        if not ret:
            return "friend"

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        enc = face_recognition.face_encodings(rgb)

        if not enc:
            return "friend"

        matches = face_recognition.compare_faces(
            self.encodings,
            enc[0]
        )

        for i, match in enumerate(matches):

            if match:
                return self.names[i]

        return "friend"


# =====================================================
# MAIN APPLICATION
# =====================================================

class SocialRobotApp:

    def __init__(self):

        self.robot = RobotController(
            use_real_robot=CONFIG.USE_REAL_ROBOT,
            robot_ip=CONFIG.ROBOT_IP,
            robot_port=CONFIG.ROBOT_PORT
        )
        self.voice = VoiceInterface()
        self.gpt = ChatGPTInterpreter()
        self.face = FaceIdentifier()

        self.user = "friend"

    def start(self):

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
                    self.voice.speak(
                        f"I am ready for the next command {self.user}"
                    )
        finally:
            self.robot.shutdown()
# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    app = SocialRobotApp()
    app.start()