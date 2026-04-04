import time
import pyttsx3
import speech_recognition as sr

from config import CONFIG


class VoiceInterface:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def speak(self, text: str) -> None:
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
                language=CONFIG.LANGUAGE,
            )
            print(f"[USER] {text}")
            return text
        except Exception:
            return None
