import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()


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
