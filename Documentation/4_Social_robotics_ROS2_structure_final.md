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
main.py
        ↓
voice_interface.py
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

The ROS 2 equivalent architecture becomes:

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
+----------------------------------+
| voice_node.py                    |
| Speech-to-text                   |
+----------------------------------+
                 |
                 | /social_robot/spoken_text
                 v
+----------------------------------+
| command_interpreter_node.py      |
| Natural language                 |
| to robot command                 |
+----------------------------------+
                 |
                 | /social_robot/command
                 v
+----------------------------------+
| behavior_manager_client_node.py  |
| Maps command to                  |
| YAML sequence                    |
+----------------------------------+
                 |
                 | ROS2 service client
                 | /ur5e/run_sequence
                 v
+----------------------------------+
| ur5e_sequence_server.py          |
| Executes YAML                    |
| sequence                         |
+----------------------------------+
                 |
                 v
+----------------------------------+
| ur5e_robot_controller            |
| MoveIt2 / pymoveit2              |
+----------------------------------+
                 |
                 v
              UR5e
```

---

# 4. Why Is `behavior_manager_client_node.py` Needed?

At first glance, it may seem unnecessary because:

```text
command_interpreter_node.py
```

already publishes the command:

```text
/social_robot/command
```

For example:

```text
hand_shake
```

However, the `behavior_manager_client_node.py` has a very important responsibility.

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

## 5.1 `command_interpreter_node.py`

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

## 5.2 `behavior_manager_client_node.py`

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

# 6. Is `behavior_manager_client_node.py` Actually the Motion Client?

Yes.

Conceptually:

```text
behavior_manager_client_node.py
```

is the ROS 2 equivalent of:

```text
behavior_manager_client.py
```

from the Python socket architecture.

It acts as:

- motion selector,
- motion client,
- and behavior coordinator.

The node receives high-level robot commands and transforms them into robot execution requests.

This architecture allows future integration of:

- gesture recognition,
- voice interaction,
- face tracking,
- emotional states,
- navigation behaviors,
- multimodal interaction systems.

---

# 7. Recommended ROS 2 Package Structure

The recommended ROS 2 workspace organization is:

```text
src/
│
├── pymoveit2/
│
├── ur5e_interfaces/
│   └── srv/
│       └── RunSequence.srv
│
├── ur5e_robot_controller/
│   ├── ur5e_pose_sequence_exec.py
│   ├── ur5e_move_to_pose_exec.py
│   ├── ur5e_move_to_joints_exec.py
│   │
│   └── utils/
│       └── yaml_loader.py
│
├── ur5e_motion_server/
│   └── ur5e_sequence_server.py
│
├── social_robot_behaviors/
│   └── behavior_manager_client_node.py
│
├── social_robot_voice/
│   └── voice_node.py
│
├── social_robot_interpreter/
│   └── command_interpreter_node.py
│
└── social_robot_gesture/
    └── gesture_interpreter_node.py
```

---

# 8. Recommended Simple Node Responsibilities

## 8.1 `voice_node.py`

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

## 8.2 `command_interpreter_node.py`

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

## 8.3 `behavior_manager_client_node.py`

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

## 8.4 `ur5e_sequence_server.py`

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

## 8.5 `ur5e_robot_controller`

### Responsibilities

- Load YAML sequence.
- Compute robot kinematics.
- Execute robot trajectories using MoveIt 2.
- Send trajectories to the UR ROS 2 driver.

This package represents the low-level robot controller layer.

It is the ROS 2 equivalent of:

```text
ur5e_robot_controller.py
```

from the Python socket architecture.

---
**ur5e_robot_controller Test**

- Terminal 1 — UR fake driver
````bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur5e robot_ip:=192.168.0.20 use_fake_hardware:=true launch_rviz:=false
````
- Terminal 2 - launch MoveIt2
````bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur5e launch_rviz:=true
````
- Terminal 3 - launch go to pose
````bash
ros2 launch ur5e_robot_controller ur5e_pose.launch.py \
  target_xyz:="[-100.0, -300.0, 300.0]" \
  target_rpy:="[90.0, 0.0, 0.0]" \
  seed_from_joint_states:=false \
  seed_joints:="[-90.0, -90.0, 90.0, 0.0, 90.0, 0.0]"
````
- Terminal 4 — launch pose sequence
````bash
ros2 launch ur5e_robot_controller ur5e_pose_sequence.launch.py sequence_file:=give5.yaml
````
**Client-server test**

- Terminal 3 — server
````bash
ros2 run ur5e_motion_server ur5e_sequence_server
ros2 run ur5e_motion_server ur5e_pose_server
ros2 run ur5e_motion_server ur5e_fkine_server
````
- Terminal 4 — client
````bash
ros2 launch social_robot_behaviors social_behavior.launch.py
````
````bash
ros2 run social_robot_behaviors ur5e_pose_client --ros-args \
  -p service_name:=/ur5e/run_pose \
  -p target_xyz:="[-100.0, -300.0, 300.0]" \
  -p target_rpy:="[90.0, 0.0, 0.0]" \
  -p seed_from_joint_states:=false \
  -p seed_joints:="[-90.0, -90.0, 90.0, 0.0, 90.0, 0.0]" \
  -p execute:=true \
  -p max_velocity:=0.1 \
  -p max_acceleration:=0.1
````
````bash
ros2 run social_robot_behaviors ur5e_fkine_client --ros-args \
  -p service_name:=/ur5e/run_fkine \
  -p joints:="[-90.0, -90.0, 90.0, 0.0, 90.0, 0.0]" \
  -p execute:=true \
  -p max_velocity:=0.1 \
  -p max_acceleration:=0.1
````

- Terminal 5 — publish behavior
````bash
ros2 topic pub /social_behavior std_msgs/msg/String "{data: 'hand_shake'}" --once
ros2 topic pub /social_behavior std_msgs/msg/String "{data: 'give5'}" --once
````
> In rviz2 you will see the sequence executed


# 9. Future Gesture-Based Interaction

The package:

```text
social_robot_gesture
```

is reserved for future gesture-based interaction using:

```text
YOLO pose estimation
```

for example:

```text
yolo11n-pose.pt
```

This package will:

- detect human gestures,
- classify social robot interactions,
- convert gestures into robot commands.

Example:

```text
Detected gesture:
high-five
        ↓
Published command:
give_me_5
```

The node will publish the same command topic:

```text
/social_robot/command
```

used by the voice interaction pipeline.

This allows:

- voice interaction,
- gesture interaction,
- and future multimodal interaction systems

to coexist using the same architecture.

---

# 10. Why This Architecture Is Good

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

# 11. Final Simplified Concept

The complete system can be summarized as:

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

This architecture represents a clean and educational transition from simple Python socket programming toward professional ROS 2 robotics software engineering.educational transition from simple Python socket programming toward professional ROS 2 robotics software engineering.