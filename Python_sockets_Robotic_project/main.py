from voice import VoiceInterface
from command_interpreter import VoiceInterpreter
from behavior_manager_client import BehaviorManager


def main():
    voice = VoiceInterface()
    interpreter = VoiceInterpreter()
    behavior = BehaviorManager()

    voice.speak("Voice control started.")

    while True:
        text = voice.listen()
        command = interpreter.interpret(text)

        if command is None:
            continue

        if command == "unknown":
            voice.speak("Command not understood.")
            continue

        if command == "exit":
            voice.speak("Goodbye.")
            break

        success = behavior.execute_command(command)

        if success:
            voice.speak("Motion executed.")
        else:
            voice.speak("Motion failed.")


if __name__ == "__main__":
    main()