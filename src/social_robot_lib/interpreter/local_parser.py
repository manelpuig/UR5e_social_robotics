from social_robot_lib.config.settings import SUPPORTED_COMMANDS

def parse_command(text):
    if text is None:
        return "unknown"

    text = text.lower()

    for command, keywords in SUPPORTED_COMMANDS.items():
        for keyword in keywords:
            if keyword in text:
                return command

    return "unknown"
