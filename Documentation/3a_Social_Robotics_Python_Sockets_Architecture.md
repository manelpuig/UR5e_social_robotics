# Phase 1 --- UR5e Control Using Python Sockets

## 1. Overview

This project introduces a simple client--server architecture for
controlling a **UR5e** robot using **Python sockets** and **URScript**.

The objective is to teach the fundamentals of modular robotics software
before introducing ROS 2.

The execution flow is:

``` text
Voice / GUI / Terminal
        ↓
Command
        ↓
Behavior Manager
        ↓
TCP Motion Server
        ↓
UR5e Controller
        ↓
UR5e Robot
```

------------------------------------------------------------------------

## 2. Software Architecture

``` text
+---------------------------+
| voice.py (optional)       |
+---------------------------+
             |
             v
+---------------------------+
| command_interpreter.py    |
+---------------------------+
             |
             v
+---------------------------+
| behavior_manager_client.py|
+---------------------------+
             |
             | TCP socket
             v
+---------------------------+
| ur5e_motion_server.py     |
+---------------------------+
             |
             v
+---------------------------+
| ur5e_robot_controller.py  |
| URScript + TCP            |
+---------------------------+
             |
             v
           UR5e
```

The client sends the **behavior name** (or associated YAML motion),
while the server is responsible for executing the robot motion.

------------------------------------------------------------------------

## 3. Package Structure

``` text
social_robot_phase1/
│
├── main.py
├── config.py
├── voice.py
├── command_interpreter.py
├── behavior_manager_client.py
├── ur5e_motion_server.py
├── ur5e_robot_controller.py
│
├── utils/
│   └── yaml_loader.py
│
└── motions/
    ├── init.yaml
    ├── handshake.yaml
    ├── give5.yaml
    └── my_motion.yaml
```

------------------------------------------------------------------------

## 4. Module Responsibilities

### `voice.py` (optional)

-   Capture speech.
-   Convert speech to text.

### `command_interpreter.py`

-   Convert user commands into robot behaviors.

Example:

``` text
"robot shake my hand"
        ↓
handshake
```

### `behavior_manager_client.py`

-   Map behaviors to YAML motion files.
-   Send execution requests to the motion server.

### `ur5e_motion_server.py`

-   Accept TCP connections.
-   Receive execution requests.
-   Load the requested YAML file.
-   Execute one motion at a time.

### `ur5e_robot_controller.py`

-   Connect to the UR5e.
-   Generate URScript commands.
-   Execute `movej` and `movel`.

------------------------------------------------------------------------

## 5. YAML Motion Files

Robot motions are described using YAML files.

Example:

``` yaml
steps:
  - name: approach
    motion: movel
    target_xyz_mm: [-300, -300, 300]
    target_rpy_deg: [90, 0, 0]
    velocity: 0.15
    acceleration: 1.2
    time: 3.0
```

Using YAML separates the robot motion from the application logic and
makes behaviors easy to modify and reuse.

------------------------------------------------------------------------

## 6. Functional Workflow

``` text
main.py
      ↓
voice.py
      ↓
command_interpreter.py
      ↓
behavior_manager_client.py
      ↓ TCP socket
ur5e_motion_server.py
      ↓
ur5e_robot_controller.py
      ↓
UR5e Robot
```

------------------------------------------------------------------------

## 7. Running the System

### Terminal 1 --- Motion Server

``` bash
python ur5e_motion_server.py
```

### Terminal 2 --- Main Application

``` bash
python main.py
```

Example:

``` text
User:
"robot shake my hand"

↓

handshake

↓

handshake.yaml

↓

Robot executes the motion
```

------------------------------------------------------------------------

## 8. Educational Objectives

This architecture introduces:

-   modular software design;
-   TCP client--server communication;
-   YAML-based motion descriptions;
-   robot command abstraction;
-   human--robot interaction.

It is intentionally simple and provides a good foundation before
learning ROS 2.

------------------------------------------------------------------------

## 9. Limitations

Compared with ROS 2 and MoveIt 2, this approach has some limitations:

-   no collision checking;
-   no motion planning;
-   no inverse kinematics framework;
-   limited execution feedback;
-   limited scalability.

For these reasons, it should be considered an educational first step.

------------------------------------------------------------------------

## 10. Migration to ROS 2

The software organization closely matches the ROS 2 version:

  Python Sockets                 ROS 2
  ------------------------------ -----------------------------------
  `voice.py`                     `voice_node.py`
  `command_interpreter.py`       `command_interpreter_node.py`
  `behavior_manager_client.py`   `behavior_manager_client_node.py`
  `ur5e_motion_server.py`        `ur5e_sequence_server.py`
  `ur5e_robot_controller.py`     `ur5e_robot_controller`

This makes the transition from Python sockets to ROS 2 straightforward
while preserving the same software architecture.
