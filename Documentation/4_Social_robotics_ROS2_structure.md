# Simple ROS 2 Social Robotics Architecture for UR5e

# 1. Introduction

This document presents a simple ROS 2 architecture for a social robotics application using a UR5e industrial robot.

The architecture is intentionally designed to be a direct evolution of the previous Python socket-based implementation.

The main objective is preserving the same conceptual flow:

```text
Voice command
    ↓
Command interpretation
    ↓
Motion selection
    ↓
Robot execution
```

while replacing custom TCP socket communication with standard ROS 2 communication mechanisms.

---

# 2. From Python Sockets to ROS 2

The original Python socket architecture was:

```text
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
```

The ROS 2 equivalent architecture becomes:

```text
voice_node.py
        ↓
command_interpreter_node.py
        ↓
behavior_manager_node.py
        ↓
ur5e_sequence_server.py
        ↓
ur5e_pose_sequence_simple_exec
        ↓
MoveIt 2 / UR Driver
        ↓
UR5e Robot
```

The idea is exactly the same.

Only the communication mechanism changes:

| Python Version | ROS 2 Version |
|---|---|
| Function calls | Topics |
| TCP client/server | ROS 2 services |
| Python modules | ROS 2 nodes |
| Manual communication | ROS 2 middleware |

---

# 3. General ROS 2 Architecture

The proposed ROS 2 architecture is:

```text
+------------------------+
| voice_node             |
| Speech-to-text         |
+------------------------+
            |
            | /social_robot/spoken_text
            v
+------------------------+
| command_interpreter    |
| Natural language       |
| to robot command       |
+------------------------+
            |
            | /social_robot/command
            v
+------------------------+
| behavior_manager_node  |
| Maps command to        |
| YAML sequence          |
+------------------------+
            |
            | service client
            | /ur5e/run_sequence
            v
+------------------------+
| ur5e_sequence_server   |
| Executes YAML          |
| sequence               |
+------------------------+
            |
            v
+------------------------+
| ur5e_pose_sequence     |
| MoveIt 2 execution     |
+------------------------+
            |
            v
        UR5e Robot
```

---

# 4. Why Is `behavior_manager_node` Needed?

At first glance, it may seem unnecessary because:

```text
command_interpreter_node
```

already publishes the command:

```text
/social_robot/command
```

For example:

```text
hand_shake
```

However, the `behavior_manager_node` has a very important responsibility.

It separates:

```text
robot intention
```

from:

```text
robot motion implementation
```

---

# 5. Responsibility Separation

## 5.1 `command_interpreter_node`

This node only understands language.

Example:

```text
"robot shake my hand"
        ↓
hand_shake
```

This node should NOT know:

- where YAML files are stored,
- how motions are executed,
- which robot is used,
- or how MoveIt works.

Its only responsibility is:

```text
speech → command
```

---

## 5.2 `behavior_manager_node`

This node decides:

```text
which robot behavior should be executed
```

Example:

```text
hand_shake
        ↓
hand_shake.yaml
```

This node contains the motion library.

Example:

```yaml
commands:

  init: init.yaml

  hand_shake: hand_shake.yaml

  give_me_5: give_me_5.yaml
```

The node then calls the service:

```text
/ur5e/run_sequence
```

using:

```text
RunSequence.srv
```

---

# 6. Is `behavior_manager_node` Actually the Motion Client?

Yes.

Conceptually:

```text
behavior_manager_node
```

is the ROS 2 equivalent of:

```text
ur5e_motion_client
```

or the old:

```text
client.py
```

from the socket architecture.

It acts as:

- motion selector,
- motion client,
- and behavior coordinator.

Therefore, you could rename it as:

```text
ur5e_motion_client_node.py
```

if you prefer a more direct name.

However:

```text
behavior_manager_node
```

is usually a better robotics architecture name because later it can manage:

- gestures,
- voice responses,
- face tracking,
- emotional states,
- navigation behaviors,
- multimodal interactions.

---

# 7. Recommended Simple Node Responsibilities

## 7.1 `voice_node.py`

### Responsibilities

- Capture microphone audio.
- Convert speech to text.
- Publish spoken text.

### Publishes

```text
/social_robot/spoken_text
```

### Message Type

```text
std_msgs/String
```

---

## 7.2 `command_interpreter_node.py`

### Responsibilities

- Interpret spoken language.
- Detect valid commands.
- Publish robot command.

### Subscribes

```text
/social_robot/spoken_text
```

### Publishes

```text
/social_robot/command
```

### Example

```text
"robot shake my hand"
        ↓
"hand_shake"
```

---

## 7.3 `behavior_manager_node.py`

### Responsibilities

- Map command to YAML motion file.
- Call robot execution service.
- Coordinate robot behaviors.

### Subscribes

```text
/social_robot/command
```

### Service Client

```text
/ur5e/run_sequence
```

### Example

```text
hand_shake
        ↓
hand_shake.yaml
```

---

## 7.4 `ur5e_sequence_server.py`

### Responsibilities

- Receive execution request.
- Check robot busy state.
- Locate YAML sequence.
- Launch motion execution node.

### Service Server

```text
/ur5e/run_sequence
```

### Service Type

```srv
string sequence_name
---
bool success
string message
```

---

## 7.5 `ur5e_pose_sequence_simple_exec`

### Responsibilities

- Load YAML sequence.
- Compute robot kinematics.
- Execute poses using MoveIt 2.
- Send trajectories to the UR driver.

This is the low-level motion execution node.

---

# 8. Why This Architecture Is Good

This architecture provides:

- clear modularity,
- easy debugging,
- scalability,
- ROS 2 compatibility,
- clean separation of responsibilities,
- easy future expansion.

Later, new capabilities can be added without modifying the entire system.

For example:

```text
Face tracking
Emotion detection
Navigation
LLM reasoning
Gesture recognition
Multi-robot systems
```

can all be integrated while preserving the same architecture.

---

# 9. Final Simplified Concept

The complete system can be summarized as:

```text
voice_node
    ↓
command_interpreter_node
    ↓
behavior_manager_node
    ↓
ur5e_sequence_server
    ↓
MoveIt 2 executor
    ↓
UR5e robot
```

This architecture represents a clean and educational transition from simple Python socket programming toward professional ROS 2 robotics software engineering.