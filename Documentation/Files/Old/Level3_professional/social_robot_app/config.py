import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CONFIG:
    # Absolute path to repository root:
    # .../UR5e_social_robotics
    REPO_ROOT = Path(__file__).resolve().parents[2]

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

    # RoboDK resources
    RDK_FILE = str(REPO_ROOT / "resources" / "roboDK" / "Social_UR5e.rdk")

    # Known faces
    KNOWN_FACES = {
        "Manel": str(REPO_ROOT / "resources" / "pictures" / "Manel_ref.png")
    }

    # Camera
    CAMERA_INDEX = 0