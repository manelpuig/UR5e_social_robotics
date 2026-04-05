from setuptools import setup, find_packages

setup(
    name="social_robot_app",
    version="0.1.0",
    description="Professional modular Level-2 Python architecture for a UR5e social robot",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "face_recognition",
        "SpeechRecognition",
        "pyttsx3",
        "openai",
        "python-dotenv",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "social-robot-app = social_robot_app.main:main",
        ],
    },
)
