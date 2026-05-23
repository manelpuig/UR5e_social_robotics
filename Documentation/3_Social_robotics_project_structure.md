# Phase 1 — Industrial Robot Control Using URScript and Python Sockets

## Abstract

This document presents the first phase of a modular social robotics architecture for controlling a UR5e industrial robot using Python socket communication and URScript commands. The objective of this phase is to develop a simple, educational, and extensible framework that allows students to interact with the robot through predefined motion sequences described in YAML files. The proposed architecture introduces essential robotics software engineering concepts such as modularity, client-server communication, motion abstraction, and voice interaction, while maintaining a structure that can later be migrated to ROS 2 and MoveIt 2.

---

# 1. Introduction

Industrial robots are commonly programmed using proprietary interfaces or direct scripting languages such as URScript in Universal Robots systems. While this approach is effective for low-level robot control, modern robotics applications increasingly require modular software architectures capable of integrating perception, artificial intelligence, voice interaction, and distributed communication.

The purpose of this first development phase is to create a lightweight educational framework that demonstrates the basic principles of social robotics interaction using a UR5e manipulator controlled through Python TCP sockets.

The proposed system enables a user to verbally request a robot action such as a handshake or a high-five. The software interprets the command, selects the corresponding YAML motion file, and sends the sequence to a robot execution server responsible for generating URScript commands.

The system intentionally avoids the complexity of ROS 2 in this initial phase while preserving a software structure compatible with future migration.

---

# 2. General Architecture

The architecture is based on a client-server model.

The server maintains the connection with the UR5e robot and executes motion sequences received from external clients.

```text
Client  --->  TCP Server  --->  UR5e Robot
```

The client sends a YAML file containing a sequence of robot poses and motion parameters.

The server:

- receives the YAML description,
- parses the sequence,
- generates URScript commands,
- and transmits the commands to the robot controller.

This architecture allows multiple students or external applications to interact with the same robot through a centralized execution server.

---

# 3. Existing Software Structure

The current implementation already includes two main programs:

## 3.1 Robot Execution Server

The server program performs the following tasks:

- Opens the TCP socket connection with the UR5e robot.
- Receives YAML motion descriptions from clients.
- Parses the YAML structure.
- Executes joint and Cartesian movements.
- Protects the robot using a mutex lock to avoid simultaneous execution requests.

The current implementation includes support for:

- `movej`
- `movel`
- TCP configuration
- motion blending
- velocity and acceleration control

The server also ensures that only one client can control the robot at a given time.

## 3.2 Client Program

The client program is intentionally simple.

Its responsibilities are:

- Read a YAML motion file.
- Send the file content to the server.
- Wait for the execution response.

Example execution:

```bash
python3 client.py handshake.yaml
```

This design allows students to focus on robot behavior generation without modifying the low-level robot communication code.

---

# 4. YAML-Based Motion Representation

Robot movements are defined using YAML files.

An example motion sequence is shown below:

```yaml
sequence_name: hand_shake

steps:

  - name: approach_handshake

    motion: moveL

    target_xyz_mm: [400, 100, 300]

    target_rpy_deg: [180, 0, 90]

    velocity: 0.15

    acceleration: 1.2

    time: 3.0

    blend: 0.0
```

This representation provides several advantages:

- Separation between motion definition and software logic.
- Improved readability.
- Easy modification of robot behaviors.
- Reusability of motion libraries.
- Simplified migration toward ROS 2.

The YAML structure already resembles the configuration-based approaches commonly used in ROS 2 robotic systems.

---

# 5. Proposed Modular Architecture

To simplify future migration to ROS 2, the Phase 1 software should be divided into independent modules.

The proposed structure is:

```text
social_robot_phase1/

├── server.py
├── client.py
├── voice_interface.py
├── command_interpreter.py
├── motion_library.py
├── yaml_loader.py
├── robot_controller.py
├── config.py

├── motions/
│   ├── init.yaml
│   ├── hand_shake.yaml
│   └── give_me_5.yaml
```

This structure separates the system into functional components with clearly defined responsibilities.

---

# 6. Module Description

## 6.1 `server.py`

This module implements the TCP robot execution server.

Responsibilities:

- Accept external TCP connections.
- Receive YAML sequences.
- Validate execution access.
- Execute robot motions sequentially.
- Send execution results to the client.

This module represents the central coordination element of the architecture.

---

## 6.2 `client.py`

The client sends motion requests to the server.

Responsibilities:

- Open the YAML file.
- Send the YAML content.
- Wait for the server response.

The client abstracts all low-level robot communication details from the user.

---

## 6.3 `voice_interface.py`

This module manages human-robot voice interaction.

Responsibilities:

- Capture microphone audio.
- Convert speech to text.
- Generate spoken robot responses.

Example commands:

```text
robot go home
robot shake my hand
robot give me five
```

This module introduces the first level of social interaction with the robot.

---

## 6.4 `command_interpreter.py`

This module converts natural language into internal robot commands.

Example:

```text
"robot shake my hand"
        ↓
"hand_shake"
```

The recommended implementation strategy is:

1. Local keyword-based parser.
2. GPT fallback interpreter if no match is found.

This hybrid approach provides:

- fast execution,
- reduced API dependency,
- better robustness,
- and simpler debugging.

---

## 6.5 `motion_library.py`

This module maps high-level commands to YAML motion files.

Example:

```python
MOTIONS = {

    "init": "motions/init.yaml",

    "hand_shake": "motions/hand_shake.yaml",

    "give_me_5": "motions/give_me_5.yaml"
}
```

This abstraction layer separates:

```text
user intention  →  robot motion
```

The same conceptual architecture will later be reused in ROS 2 behavior management nodes.

---

## 6.6 `yaml_loader.py`

This module validates YAML motion files before execution.

Validation includes:

- syntax verification,
- required fields,
- valid motion types,
- Cartesian pose completeness,
- joint vector size.

This module improves safety and prevents malformed motion sequences.

---

## 6.7 `robot_controller.py`

This module handles low-level robot communication.

Responsibilities:

- Open TCP socket connection.
- Send URScript commands.
- Convert units and coordinates.
- Execute `movej`.
- Execute `movel`.

The module must remain independent from:

- voice interaction,
- GPT,
- perception,
- user interfaces.

Its only responsibility is robot motion execution.

---

## 6.8 `config.py`

Centralized configuration module.

Example:

```python
SERVER_IP = "0.0.0.0"

SERVER_PORT = 5000

ROBOT_IP = "192.168.1.4"

ROBOT_PORT = 30002

ACTIVATION_WORD = "robot"

LANGUAGE = "en-US"
```

Centralized configuration simplifies deployment and maintenance.

---

# 7. Functional Workflow

The complete system workflow is illustrated below:

```text
User Speech
      ↓
voice_interface.py
      ↓
command_interpreter.py
      ↓
motion_library.py
      ↓
client.py
      ↓
server.py
      ↓
robot_controller.py
      ↓
UR5e Robot
```

Example interaction:

```text
User:
"robot shake my hand"

Interpreter:
hand_shake

Motion library:
motions/hand_shake.yaml

Client:
sends YAML sequence

Server:
executes sequence

Robot:
performs handshake motion
```

---

# 8. Educational Advantages

The proposed architecture introduces students to several important robotics concepts:

- modular software design,
- robot communication protocols,
- YAML-based configuration,
- client-server architectures,
- human-robot interaction,
- software abstraction,
- safe shared robot access.

The simplicity of the architecture makes it suitable for teaching robotics software engineering principles.

---

# 9. Limitations of the Proposed Approach

Although effective for educational purposes, this architecture presents several limitations.

The robot is controlled through direct URScript socket communication without a complete robotics middleware.

Main limitations include:

- absence of MoveIt 2 motion planning,
- no collision checking,
- no integrated inverse kinematics solver,
- no singularity analysis,
- limited trajectory optimization,
- limited execution feedback,
- difficult synchronization between modules,
- no distributed robotics infrastructure,
- limited scalability,
- difficult integration of heterogeneous sensors.

Therefore, this phase should be considered an introductory software architecture rather than a professional industrial robotics framework.

---

# 10. Migration Toward ROS 2

One of the main objectives of this design is preserving compatibility with future ROS 2 migration.

The proposed mapping is:

| Phase 1 Module | ROS 2 Equivalent |
|---|---|
| `voice_interface.py` | voice node |
| `command_interpreter.py` | NLP interpreter node |
| `motion_library.py` | behavior manager node |
| `yaml_loader.py` | configuration utility |
| `robot_controller.py` | MoveIt 2 execution node |
| `server.py` | ROS 2 action/service server |
| `client.py` | ROS 2 action/service client |

The future ROS 2 architecture may become:

```text
voice_node
      ↓
command_interpreter_node
      ↓
behavior_manager_node
      ↓
motion_execution_node
      ↓
MoveIt 2
      ↓
UR ROS 2 Driver
      ↓
UR5e Robot
```

This migration path allows students to progressively evolve from simple Python robotics applications toward professional ROS 2 robotic systems.

---

# 11. Conclusion

This document presented the first phase of a modular social robotics framework for controlling a UR5e robot using Python sockets and URScript communication.

The proposed architecture prioritizes:

- simplicity,
- modularity,
- educational clarity,
- and future scalability.

The system introduces voice interaction, YAML-based motion abstraction, and modular software organization while remaining accessible to students with limited robotics software experience.

Although the architecture lacks advanced robotics capabilities such as collision-aware planning and distributed middleware integration, it provides an excellent foundation for understanding robot software organization and preparing future migration toward ROS 2 and MoveIt 2.