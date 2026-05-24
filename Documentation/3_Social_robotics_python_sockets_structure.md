# Phase 1 — Industrial Robot Control Using URScript and Python Sockets

## Abstract

This document presents the first phase of a modular social robotics architecture for controlling a UR5e industrial robot using Python socket communication and URScript commands.

The objective of this phase is to develop a simple, educational, and extensible framework that allows students to interact with the robot through predefined motion sequences described in YAML files.

The proposed architecture introduces essential robotics software engineering concepts such as:

- modularity,
- client-server communication,
- motion abstraction,
- and voice interaction,

while maintaining a structure that can later be migrated to ROS 2 and MoveIt 2.

---

# 1. Introduction

Industrial robots are commonly programmed using proprietary interfaces or direct scripting languages such as URScript in Universal Robots systems.

While this approach is effective for low-level robot control, modern robotics applications increasingly require modular software architectures capable of integrating:

- perception,
- artificial intelligence,
- voice interaction,
- and distributed communication.

The purpose of this first development phase is to create a lightweight educational framework that demonstrates the basic principles of social robotics interaction using a UR5e manipulator controlled through Python TCP sockets.

The proposed system enables a user to verbally request a robot action such as:

- a handshake,
- a high-five,
- or a home motion.

The software interprets the command, selects the corresponding YAML motion file, and sends the sequence to a robot execution server responsible for generating URScript commands.

The system intentionally avoids the complexity of ROS 2 in this initial phase while preserving a software structure compatible with future migration.

---

# 2. General Architecture

The architecture is based on a client-server model.

The server maintains the connection with the UR5e robot and executes motion sequences received from external clients.

```text
TCP CLIENT  --->  TCP SERVER  --->  UR5e Robot
```

The client sends a YAML file containing:

- robot poses,
- motion types,
- and execution parameters.

The server:

- receives the YAML description,
- parses the sequence,
- generates URScript commands,
- and transmits the commands to the robot controller.

This architecture allows multiple students or external applications to interact with the same robot through a centralized execution server.

---

# 3. Existing Software Structure

The current implementation includes:

- a voice interaction system,
- a command interpreter,
- a behavior manager,
- a robot execution server,
- and a low-level robot controller.

---

# 4. YAML-Based Motion Representation

Robot movements are defined using YAML files.

Example:

```yaml
sequence_name: hand_shake

steps:

  - name: approach_handshake

    motion: moveL

    target_xyz_mm: [-300, -300, 300]

    target_rpy_deg: [90, 0, 0]

    velocity: 0.15

    acceleration: 1.2

    time: 3.0

    blend: 0.0
```
> If time: -1, the motion will be executed at the specified velocity and acceleration without a time limit until the robot reaches the target pose.

This representation provides several advantages:

- separation between motion definition and software logic,
- improved readability,
- easy modification of robot behaviors,
- reusable motion libraries,
- simplified migration toward ROS 2.

The YAML structure already resembles the configuration-based approaches commonly used in ROS 2 robotic systems.

---

# 5. Proposed Modular Architecture

The proposed Python socket architecture is:

```text
social_robot_phase1/

├── main.py
├── config.py
│
├── voice.py
├── command_interpreter.py
├── behavior_manager_client.py
│
├── ur5e_motion_server.py
├── ur5e_robot_controller.py
│
├── utils/
│   └── yaml_loader.py
│
└── motions/
    ├── init.yaml
    ├── hand_shake.yaml
    └── give_me_5.yaml
```

This structure separates the system into functional components with clearly defined responsibilities.

---

# 6. Module Description

## 6.1 `main.py`

This file acts as the main application orchestrator.

It connects:

```text
voice
    ↓
command interpreter
    ↓
behavior manager client
```

Example workflow:

```text
voice.py
    ↓
command_interpreter.py
    ↓
behavior_manager_client.py
```

---

## 6.2 `voice.py`

This module manages human-robot voice interaction.

### Responsibilities

- Capture microphone audio.
- Convert speech to text.
- Generate spoken robot responses.

### Example Commands

```text
robot go home
robot shake my hand
robot give me five
```

This module introduces the first level of social interaction with the robot.

---

## 6.3 `command_interpreter.py`

This module converts natural language into internal robot commands.

Example:

```text
"robot shake my hand"
        ↓
"hand_shake"
```

### Recommended Strategy

1. Local keyword-based parser.
2. GPT fallback interpreter if no match is found.

This hybrid approach provides:

- fast execution,
- reduced API dependency,
- better robustness,
- simpler debugging.

---

## 6.4 `behavior_manager_client.py`

This module acts as the TCP client of the architecture.

Its responsibilities are:

- map commands to YAML files,
- load robot motion sequences,
- validate YAML files,
- send execution requests to the server.

Example:

```text
hand_shake
        ↓
motions/hand_shake.yaml
        ↓
TCP request
        ↓
ur5e_motion_server.py
```

Example motion library:

```python
MOTIONS = {

    "init": "motions/init.yaml",

    "hand_shake": "motions/handshake.yaml",

    "give_me_5": "motions/give5.yaml"
}
```

This module separates:

```text
robot intention
```

from:

```text
robot motion implementation
```

---

## 6.5 `ur5e_motion_server.py`

This module implements the TCP robot execution server.

### Responsibilities

- Accept TCP connections.
- Receive YAML sequences.
- Validate execution access.
- Protect the robot using a mutex lock.
- Execute robot motions sequentially.
- Send execution results to the client.

This module represents the central coordination element of the architecture.

---

## 6.6 `utils/yaml_loader.py`

This module validates YAML motion files before execution.

### Validation Includes

- syntax verification,
- required fields,
- valid motion types,
- Cartesian pose completeness,
- joint vector size.

This module improves safety and prevents malformed motion sequences.

---

## 6.7 `ur5e_robot_controller.py`

This module handles low-level robot communication.

### Responsibilities

- Open TCP socket connection with the UR5e.
- Send URScript commands.
- Convert units and coordinates.
- Execute `movej`.
- Execute `movel`.
- Configure TCP parameters.
- Interface with RoboDK.

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

ROBOT_IP = "192.168.0.20"

ROBOT_PORT = 30002

ACTIVATION_WORD = "robot"

LANGUAGE = "en-US"
```

Centralized configuration simplifies deployment and maintenance.

---

# 7. Functional Workflow

The complete system workflow is illustrated below:

```text
main.py
      ↓
voice.py
      ↓
command_interpreter.py
      ↓
behavior_manager_client.py
      ↓ TCP CLIENT
ur5e_motion_server.py
      ↓
ur5e_robot_controller.py
      ↓
UR5e Robot
```

---

# 8. Example Interaction

- In a new terminal on the python directory, run the motion server:

```bash
python ur5e_motion_server.py
```
- In another terminal, run the main application:

```bash
python main.py
```
- Speak the command:
```text
User:
"robot shake my hand"

Interpreter:
hand_shake

Behavior manager:
motions/hand_shake.yaml

TCP client:
sends YAML sequence

Motion server:
executes sequence

Robot:
performs handshake motion
```

---

# 9. Educational Advantages

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

# 10. Limitations of the Proposed Approach

Although effective for educational purposes, this architecture presents several limitations.

The robot is controlled through direct URScript socket communication without a complete robotics middleware.

## Main Limitations

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

# 11. Migration Toward ROS 2

One of the main objectives of this design is preserving compatibility with future ROS 2 migration.

The proposed mapping is:

| Python Phase 1 | ROS 2 Equivalent |
|---|---|
| `main.py` | launch file |
| `voice.py` | `voice_node.py` |
| `command_interpreter.py` | `command_interpreter_node.py` |
| `behavior_manager_client.py` | `behavior_manager_client_node.py` |
| `utils/yaml_loader.py` | `utils/yaml_loader.py` |
| `ur5e_motion_server.py` | `ur5e_sequence_server.py` |
| `ur5e_robot_controller.py` | `ur5e_robot_controller/` |

The future ROS 2 architecture becomes:

```text
voice_node.py
    ↓
command_interpreter_node.py
    ↓
behavior_manager_client_node.py
    ↓ ROS2 SERVICE CLIENT
ur5e_sequence_server.py
    ↓
ur5e_robot_controller
    ↓
MoveIt2 / UR Driver
    ↓
UR5e
```

This migration path allows students to progressively evolve from simple Python robotics applications toward professional ROS 2 robotic systems.

---

# 12. Conclusion

This document presented the first phase of a modular social robotics framework for controlling a UR5e robot using Python sockets and URScript communication.

The proposed architecture prioritizes:

- simplicity,
- modularity,
- educational clarity,
- future scalability,
- and direct compatibility with ROS 2 concepts.

The system introduces:

- voice interaction,
- YAML-based motion abstraction,
- client-server communication,
- and modular software organization

while remaining accessible to students with limited robotics software experience.

Although the architecture lacks advanced robotics capabilities such as collision-aware planning and distributed middleware integration, it provides an excellent foundation for understanding robot software organization and preparing future migration toward ROS 2 and MoveIt 2.nced robotics capabilities such as collision-aware planning and distributed middleware integration, it provides an excellent foundation for understanding robot software organization and preparing future migration toward ROS 2 and MoveIt 2.