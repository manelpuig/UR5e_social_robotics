# Social Robotics Project with the UR5e

## Objective

Create and test one social motion using two client-server architectures:

1. Python sockets with RoboDK and URScript.
2. ROS 2 services with MoveIt 2.

Use the same intermediate poses in both implementations so that the architectures can be compared.

## Before the laboratory

1. Choose a motion such as waving, greeting, giving five, or pointing.
2. Define safe initial, intermediate, and final poses.
3. Create the Python sockets YAML in `Python_sockets_Robotic_project/motions/`.
4. Register it in `behavior_manager_client.py` and `command_interpreter.py`.
5. Verify the client and server locally with RoboDK.
6. Create the ROS 2 YAML in `src/ur5e_motion_utils/ur5e_robot_controller/config/`.
7. Build the workspace and verify the motion with fake hardware and MoveIt 2.

See `3_Python_Sockets_Architecture.md` and `4_ROS2_Architecture.md` for architecture and verification commands.

## Session 1 — Python sockets

Teacher PC:

```bash
cd ~/UR5e_social_robotics/Python_sockets_Robotic_project
python3 ur5e_motion_server.py
```

Student PC:

```bash
cd ~/UR5e_social_robotics/Python_sockets_Robotic_project
python3 main.py
```

The Student PC must use the Teacher PC IP in `config.py`. The teacher starts only the server; `ur5e_robot_controller.py` is imported automatically.

## Session 2 — ROS 2 and MoveIt 2

1. After instructor approval, transfer the validated YAML directly to the installed config directory on the Teacher PC with `Documentation/Files/Send_motion/send_social_motion.py`. See `4_ROS2_Architecture.md` for the destination and configuration.
2. On the Teacher PC, start the real UR driver, MoveIt 2, and `ur5e_sequence_server`.
3. On the Student PC, start `social_behavior.launch.py`.
4. Publish the behavior name on `/social_behavior`.
5. Compare the resulting motion with the sockets version.

The real driver uses:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=false launch_rviz:=false
```

The External Control program must be loaded and started from the UR5e teach pendant.

## Safety

- Obtain instructor approval before using the real robot.
- Test every motion in simulation first.
- Use low velocity and acceleration for the first execution.
- Keep the workspace clear and the emergency stop accessible.
- Stop immediately if the motion is unexpected.

## Deliverables

1. Python sockets YAML file.
2. ROS 2 YAML file.
3. Short description of the motion and its poses.
4. Evidence of simulation and real-robot execution.
5. Brief comparison of Python sockets/URScript and ROS 2/MoveIt 2.
