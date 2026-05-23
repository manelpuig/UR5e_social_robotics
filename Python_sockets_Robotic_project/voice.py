#!/usr/bin/env python3

import time
import speech_recognition as sr
import pyttsx3

from config import LANGUAGE, TTS_RATE
from typing import Optional


class VoiceInterface:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def speak(self, text: str):
        print(f"[TTS] {text}")

        engine = pyttsx3.init()
        engine.setProperty("rate", TTS_RATE)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

        time.sleep(0.3)

    def listen(self) -> Optional[str]:
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(
                audio,
                language=LANGUAGE
            )
            print(f"[USER] {text}")
            return text

        except sr.UnknownValueError:
            print("Speech not understood.")
            return None

        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None