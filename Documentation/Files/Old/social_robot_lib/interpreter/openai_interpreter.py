import os
from openai import OpenAI
from social_robot_lib.config.settings import OPENAI_MODEL

client = OpenAI()

def interpret_with_gpt(text):

    if text is None:
        return "unknown"

    prompt = f"""
Classify this instruction into one command:

init
hand_shake
give_me_5
exit
unknown

Instruction: {text}

Answer only with the command name.
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        result = response.choices[0].message.content.strip().lower()
        return result

    except Exception:
        return "unknown"
