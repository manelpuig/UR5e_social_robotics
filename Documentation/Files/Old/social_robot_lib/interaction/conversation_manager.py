def greeting(name):

    if name:
        return f"Hello {name}"

    return "Hello"

def confirmation(command):

    messages = {
        "init": "Going to initial position",
        "hand_shake": "Starting handshake",
        "give_me_5": "Give me five!",
        "exit": "Goodbye"
    }

    return messages.get(command, "I did not understand")
