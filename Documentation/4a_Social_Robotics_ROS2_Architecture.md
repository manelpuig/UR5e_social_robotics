# Simple ROS 2 Social Robotics Architecture for UR5e

## 1. Overview

This project implements a simple ROS 2 architecture for controlling a
**UR5e** robot through reusable social behaviors.

The goal is to keep the software modular and easy to understand while
following standard ROS 2 design principles.

The execution flow is:

``` text
Voice / GUI / Terminal
        ↓
Command
        ↓
Behavior Manager
        ↓
Sequence Server
        ↓
MoveIt 2
        ↓
UR5e
```

------------------------------------------------------------------------

## 2. ROS 2 Architecture

``` text
+-----------------------------+
| voice_node.py (optional)    |
+-----------------------------+
              |
              | /social_behavior
              v
+-----------------------------+
| behavior_manager_client_node|
+-----------------------------+
              |
              | Service: /ur5e/run_sequence
              v
+-----------------------------+
| ur5e_sequence_server.py     |
+-----------------------------+
              |
              v
+-----------------------------+
| ur5e_robot_controller       |
| MoveIt 2 + YAML execution   |
+-----------------------------+
              |
              v
            UR5e
```

The **Behavior Manager Client** only sends the **behavior name**, for
example:

``` text
handshake
```

The **Sequence Server** searches:

``` text
handshake.yaml
```

inside:

``` text
ur5e_robot_controller/config/
```

and launches the motion.

------------------------------------------------------------------------

## 3. Node Responsibilities

### `behavior_manager_client_node`

-   subscribes to `/social_behavior`
-   validates the command name
-   calls `/ur5e/run_sequence`

### `ur5e_sequence_server`

-   receives the requested behavior
-   checks that the YAML file exists
-   launches `ur5e_pose_sequence.launch.py`
-   prevents concurrent motion execution

### `ur5e_robot_controller`

-   loads the YAML sequence
-   computes inverse kinematics
-   executes trajectories using MoveIt 2

------------------------------------------------------------------------

## 4. Package Structure

``` text
src/
│
├── ur5e_interfaces/
│
├── ur5e_robot_controller/
│   ├── config/
│   │   ├── handshake.yaml
│   │   ├── give5.yaml
│   │   └── my_motion.yaml
│   ├── launch/
│   └── ur5e_pose_sequence.py
│
├── ur5e_motion_server/
│   └── ur5e_sequence_server.py
│
└── social_robot_behaviors/
    └── behavior_manager_client_node.py
```

------------------------------------------------------------------------

## 5. Testing the Controller

### Terminal 1 --- UR fake driver

``` bash
ros2 launch ur_robot_driver ur_control.launch.py \
ur_type:=ur5e \
robot_ip:=192.168.0.20 \
use_fake_hardware:=true \
launch_rviz:=false
```

### Terminal 2 --- MoveIt 2

``` bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
ur_type:=ur5e \
launch_rviz:=true
```

### Terminal 3 --- Execute a YAML sequence

``` bash
ros2 launch ur5e_robot_controller \
ur5e_pose_sequence.launch.py \
sequence_file:=give5.yaml
```

------------------------------------------------------------------------

## 6. Testing the Client--Server Architecture

### Terminal 3 --- Sequence Server

``` bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

(Optional)

``` bash
ros2 run ur5e_motion_server ur5e_pose_server
ros2 run ur5e_motion_server ur5e_fkine_server
```

### Terminal 4 --- Behavior Manager Client

``` bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

### Terminal 5 --- Publish a behavior

``` bash
ros2 topic pub --once /social_behavior \
std_msgs/msg/String \
"{data: 'handshake'}"

ros2 topic pub --once /social_behavior \
std_msgs/msg/String \
"{data: 'give5'}"
```

The robot executes the corresponding YAML sequence.

------------------------------------------------------------------------

## 7. Student Workflow

1.  Create a new YAML motion.
2.  Test it locally using the fake UR5e.
3.  Give the YAML file to the instructor.
4.  The instructor copies it into:

``` text
ur5e_robot_controller/config/
```

5.  Rebuild the package if required.
6.  Verify the motion.
7.  Execute the behavior through the client.

------------------------------------------------------------------------

## 8. Why This Architecture?

-   Clear separation of responsibilities.
-   Easy debugging.
-   One YAML library.
-   Safe validation before running on the real robot.
-   Easy to extend with voice, vision or gesture recognition.

The same client can later receive commands from speech recognition,
gesture recognition or any other ROS 2 node without modifying the motion
execution layer.
