from social_robot_lib.interpreter.local_parser import parse_command
from social_robot_lib.interpreter.openai_interpreter import interpret_with_gpt

def route_command(text):

    command = parse_command(text)

    if command != "unknown":
        return command

    return interpret_with_gpt(text)
