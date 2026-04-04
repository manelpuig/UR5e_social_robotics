import re
from openai import OpenAI

from config import CONFIG


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
            "start position",
        ]):
            return "init"

        if any(k in text for k in [
            "hand shake",
            "shake hand",
            "handshake",
            "shake my hand",
            "lets shake hands",
            "greet me",
        ]):
            return "hand_shake"

        if any(k in text for k in [
            "give me five",
            "give me 5",
            "high five",
            "give me a high five",
            "lets do a high five",
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
""".strip()

        try:
            response = self.client.responses.create(
                model=CONFIG.GPT_MODEL,
                instructions=instructions,
                input=text,
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
