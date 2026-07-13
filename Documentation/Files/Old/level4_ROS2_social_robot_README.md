# Level4 ROS2 Social Robot Architecture

This document describes the structure of the
**level4_ROS2_social_robot** project.\
The goal of this version is to migrate the Level 3 social robot
application into a clean, modular ROS 2 architecture while keeping the
system simple and educational.

------------------------------------------------------------------------

# Overview

The system is divided into three main layers:

1.  Interaction Layer (voice + perception)
2.  Behavior Layer (decision making)
3.  Motion Layer (robot execution with MoveIt2)

The robot pipeline is:

Speech → Intent → Behavior → Motion Sequence (YAML) → IK → MoveIt2 →
Robot

------------------------------------------------------------------------

# Package Structure

The workspace contains three main components:

    social_robot_lib
    social_robot_behaviors
    ur5e_social_motion

Each package has a clear responsibility.

------------------------------------------------------------------------

# social_robot_lib

This is a pure Python library (not a ROS node package).

It contains reusable modules from Level 3:

-   speech recognition
-   text-to-speech
-   wakeword detection
-   command interpretation
-   face identification
-   conversation logic

Example modules:

    hri/speech_listener.py
    hri/tts_engine.py
    interaction/command_router.py
    perception/face_identifier.py

This keeps ROS logic separate from AI interaction logic.

------------------------------------------------------------------------

# social_robot_behaviors

This package contains the main ROS2 node:

    social_behavior_manager

Responsibilities:

-   detect person
-   greet user
-   listen to speech
-   detect wakeword
-   interpret command
-   trigger robot behavior

Example flow:

    "robot handshake"
    → route_command()
    → execute_handshake_behavior()
    → run_handshake_sequence()

Each behavior is implemented as a small module:

    init_behavior.py
    handshake_behavior.py
    highfive_behavior.py

These modules delegate motion execution to the motion package.

------------------------------------------------------------------------

# ur5e_social_motion

This package executes robot motion using MoveIt2.

Responsibilities:

-   load YAML motion sequences
-   execute pose steps sequentially
-   compute IK
-   send joint targets to MoveIt2

Main files:

    sequence_runner.py
    social_motions.py
    ur5e_move_to_pose_exe.py

Execution pipeline:

    run_handshake_sequence()
    → load YAML
    → iterate steps
    → run_pose_motion()
    → compute IK
    → execute trajectory

------------------------------------------------------------------------

# YAML Motion Sequences

Each social motion is defined as a sequence of steps.

Example:

    sequence:
      - step_name: approach_handshake
        target_xyz_mm: [350, 0, 450]
        target_rpy_deg: [90, 0, 90]

      - step_name: handshake_pose
        target_xyz_mm: [360, 0, 430]
        target_rpy_deg: [90, 0, 90]

Advantages:

-   easy to modify motions
-   readable by students
-   reusable
-   hardware independent

------------------------------------------------------------------------

# Reference Frame Convention

Motion targets are defined in a **table reference frame** instead of
base_link.

Conversion to base_link is done internally before IK computation.

This makes configuration intuitive and consistent with RoboDK workflows.

------------------------------------------------------------------------

# Launch Strategy

Two types of launch files exist:

Generic launcher:

    ur5e_pose_sequence.launch.py

Behavior launchers:

    ur5e_social_handshake.launch.py
    ur5e_social_highfive.launch.py
    ur5e_social_init.launch.py

The generic launcher allows executing any YAML sequence.

------------------------------------------------------------------------

# Execution Flow Example

Example command:

    robot handshake

Pipeline:

    speech_listener
    → wakeword detection
    → command_router
    → handshake_behavior
    → run_handshake_sequence()
    → YAML steps
    → IK solver
    → MoveIt2 execution

------------------------------------------------------------------------

# Design Goals

This Level4 ROS2 architecture provides:

-   modular structure
-   separation between interaction and motion
-   YAML-based motion definition
-   compatibility with MoveIt2
-   reusable Level3 Python modules
-   simple structure for teaching environments

The system remains lightweight while introducing professional ROS2
architecture principles.
