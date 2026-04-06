from social_robot_lib.config.settings import WAKEWORD

def detect_wakeword(text):
    if text is None:
        return False, None

    text = text.lower()

    if WAKEWORD in text:
        command = text.replace(WAKEWORD, "").strip()
        return True, command

    return False, text
