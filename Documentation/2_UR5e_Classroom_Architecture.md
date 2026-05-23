# UR5e Educational Client–Server Architecture for Classroom Robotics

## Overview

This project defines a unified educational architecture for controlling a UR5e collaborative robot in a classroom environment composed of:

* 1 Professor PC connected to the real UR5e robot through Ethernet
* 5 Student PCs connected through the local network
* A centralized and supervised robot control architecture

The main objective is to teach students the evolution from low-level robot control using Python sockets and URScript to advanced robot control using ROS 2.

The same client–server philosophy is maintained throughout the entire learning process.

---

# Educational Philosophy

The proposed methodology follows a progressive robotics learning strategy:

## Stage 1 — Direct URScript Control using Python Sockets

Students first learn how industrial robots can be controlled at a low level using:

* Python
* TCP/IP sockets
* URScript commands

In this stage:

* Student PCs act as clients
* The Professor PC acts as a centralized server
* The Professor PC validates and forwards commands to the UR5e robot

This approach allows students to:

* Understand robot networking
* Learn industrial robot communication basics
* Send real robot movements with simple Python scripts

Example educational concepts:

* Socket programming
* TCP client/server architecture
* URScript motion commands
* Robot safety supervision
* Sequential motion execution
* YAML-based motion definitions

Although this approach is simple and very educational, students quickly discover several limitations:

* Limited modularity and scalability
* Difficult synchronization between modules
* No standardized communication framework
* Difficult integration of sensors and AI modules
* Abrupt robot motions
* Non-optimized trajectories

Although TCP sockets are still used internally in industrial communication systems, professional robotics applications are usually implemented using:

* Robotics middleware
* Distributed node architectures
* Motion planning frameworks
* Standardized robot interfaces
* Real-time controllers
* Modular software ecosystems
These limitations naturally motivate the transition toward ROS 2, MoveIt 2, and modern robotics software engineering principles..

---

# Stage 2 — Advanced Robot Control using ROS 2

After understanding low-level robot communication, students migrate to a ROS 2 architecture.

The educational objective is to demonstrate how ROS 2 solves many limitations of direct socket programming.

In this stage:

* Student PCs continue acting as clients
* The Professor PC continues acting as the centralized robot server
* Communication is now implemented using ROS 2 topics, services, and actions
* The UR5e is controlled through the ROS 2 UR driver and MoveIt 2

Students learn:

* Distributed robotics systems
* ROS 2 nodes and packages
* Topics, services, and actions
* Robot state publishing
* TF transformations
* Motion planning with MoveIt 2
* Trajectory execution
* Sensor integration
* AI integration
* Modular robotics software architectures

ROS 2 provides a more scalable, modular, robust, and professional implementation of the same architecture.

---

# Unified Client–Server Philosophy

A central aspect of the proposed teaching methodology is maintaining the same conceptual architecture during the entire course.

Both approaches share the same structure:

| Layer              | Python + URScript         | ROS 2                        |
| ------------------ | ------------------------- | ---------------------------- |
| Student PC         | Socket client             | ROS 2 client nodes           |
| Professor PC       | Socket server             | ROS 2 centralized supervisor |
| Communication      | TCP sockets               | ROS 2 DDS middleware         |
| Motion commands    | URScript strings          | ROS 2 actions/services       |
| Robot control      | Direct URScript execution | MoveIt 2 + UR driver         |
| Safety supervision | Server-side validation    | ROS 2 supervision nodes      |

This continuity helps students:

* Understand the evolution of robotics architectures
* Compare low-level vs high-level robot control
* Understand why ROS 2 exists
* Appreciate modular and distributed systems
* Learn industrial robotics software engineering progressively

---

# Real-Time and Low-Latency Requirements

## Ubuntu Low-Latency Kernel Recommendation

For both robot control approaches — Python sockets with URScript and ROS 2 with the UR driver — the Professor PC should use an Ubuntu low-latency kernel.

Recommended systems:

* Ubuntu 22.04 LTS
* Linux low-latency kernel

Installation:

```bash
sudo apt install linux-lowlatency
```

After installation, the system should be rebooted.

Verify the active kernel:

```bash
uname -r
```

Expected output example:

```text
6.8.0-71-lowlatency
```

---

## Real-Time Scheduling Permissions

It is also recommended to configure real-time scheduling permissions.

Create realtime group:

```bash
sudo groupadd realtime
sudo usermod -aG realtime $USER
```

Create configuration file:

```bash
sudo nano /etc/security/limits.d/99-realtime.conf
```

Add:

```text
@realtime soft rtprio 99
@realtime hard rtprio 99
@realtime soft priority 99
@realtime hard priority 99
@realtime soft memlock unlimited
@realtime hard memlock unlimited
```

Reboot the system:

```bash
sudo reboot
```

These settings allow ROS 2 controllers and industrial robot drivers to use high-priority scheduling with reduced execution jitter.

This configuration is commonly recommended for:

* Universal Robots ROS 2 Driver
* MoveIt 2
* ros2_control
* Industrial robotic applications
* Real-time robot communication

---

## Why Low Latency is Important

Industrial robot control requires deterministic and stable communication timing.

The UR5e robot continuously exchanges real-time motion information with the control PC.

This includes:

* Joint states
* Trajectory commands
* Velocity updates
* RTDE communication packets
* Motion interpolation
* Safety state monitoring

A standard desktop kernel may introduce:

* Scheduling delays
* Communication jitter
* Unstable execution timing
* Delayed motion updates
* Driver communication interruptions

These problems can produce:

* Non-smooth robot motion
* RTDE communication warnings
* Driver reconnections
* Delayed trajectory execution
* Motion instability
* Reduced control frequency

The low-latency kernel significantly improves scheduling responsiveness and reduces communication jitter.


# Classroom Network Architecture

## Hardware Configuration

* 1 UR5e collaborative robot
* 1 Professor PC connected to the robot via Ethernet
* 5 Student PCs connected through LAN/WiFi

## Logical Architecture

```text
+----------------+
|  Student PC 1  |
+----------------+
         \
+----------------+        +-------------------+        +-------------+
|  Student PC 2  | -----> |   Professor PC    | -----> |    UR5e     |
+----------------+        |  Central Server   |        |   Robot     |
         /                +-------------------+        +-------------+
+----------------+
|  Student PC 3  |
+----------------+
```

The Professor PC acts as:

* Motion supervisor
* ROS 2 server
* Safety gateway
* Trajectory validator
* Motion planner
* Robot communication bridge

---

# Progressive Learning Strategy

The teaching sequence is intentionally progressive:

## Phase 1 — Industrial Robot Basics

Students learn:

* TCP/IP networking
* Python sockets
* URScript
* Basic motion commands
* Modular Python applications
* YAML-based robot sequences
* Motion servers
* Distributed client applications

## Phase 2 — ROS 2 Robotics

Students learn:

* ROS 2 nodes
* Topics and services
* MoveIt 2
* Robot drivers
* TF transformations
* Navigation and perception
* AI integration

## Phase 3 — Social and Intelligent Robotics

Students integrate:

* YOLO object detection
* Gesture recognition
* Voice interaction
* Human–robot interaction
* AI-based behaviors
* Autonomous social robot applications


# Conclusion

This educational architecture provides a progressive transition from direct industrial robot programming using Python sockets and URScript toward professional robotics development using ROS 2 and MoveIt 2.

The key idea is maintaining the same client–server philosophy during the entire learning process.

Students first understand how robot communication works internally using low-level socket programming and later discover how ROS 2 provides a scalable and professional distributed robotics framework.

The final result is a robust educational framework for teaching:

* Industrial robotics
* Distributed systems
* ROS 2
* AI robotics
* Human–robot interaction
* Professional robotics software engineering
