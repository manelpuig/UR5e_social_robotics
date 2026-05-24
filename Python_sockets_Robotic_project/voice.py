#!/usr/bin/env python3

import speech_recognition as sr
import pyttsx3

from config import LANGUAGE, TTS_RATE
from typing import Optional


class VoiceInterface:

    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Faster voice detection
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

        # Initialize TTS only once
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", TTS_RATE)

        # Calibrated once at startup
        self.microphone = sr.Microphone()
        with self.microphone as source:
            print("[VOICE] Calibrating ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[VOICE] Ready.")

    def speak(self, text: str):
        print(f"[TTS] {text}")

        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self) -> Optional[str]:
        with self.microphone as source:
            print("\n[VOICE] Speak now...")

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=4
                )

            except sr.WaitTimeoutError:
                print("No speech detected.")
                return None

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