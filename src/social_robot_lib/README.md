# social_robot_lib

This library contains the non‑ROS logic reused from the Level 3 social robot application.

It provides lightweight Python modules for:

- Speech recognition (listen to the user)
- Text‑to‑speech (robot voice feedback)
- Wakeword detection ("robot ...")
- Command interpretation (local parser + optional ChatGPT fallback)
- Face identification (simple single‑person recognition)
- Conversation helpers
- Shared data structures (Intent, PersonIdentity)

This library is intentionally **not a ROS2 package** in behavior terms.
It is a reusable Python module imported by:

- social_robot_behaviors (ROS2 orchestrator)
- ur5e_social_motion (robot motion execution layer)

Structure:

social_robot_lib/
 ├── config/settings.py
 ├── hri/
 ├── interpreter/
 ├── perception/
 ├── interaction/
 ├── models/

Typical usage example:

from social_robot_lib.hri.speech_listener import listen
from social_robot_lib.interaction.command_router import route_command

text = listen()
intent = route_command(text)

if intent.name == "hand_shake":
    print("Execute handshake behavior")

Designed to stay close to the Level 3 implementation with minimal complexity.
