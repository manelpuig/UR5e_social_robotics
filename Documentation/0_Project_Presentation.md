# Social Robotics with the UR5e

## Project introduction

This project is about designing a social movement for a robot arm and learning how software sends that movement to a robot.

The robot is a **UR5e collaborative robot arm**. Example behaviours are waving, giving five, pointing, and offering a handshake.

The goal is not only to make the arm move. The movement must have a clear meaning, work in simulation, and be checked for safety.

### What will we learn?

- How to describe a robot movement as a sequence of steps.
- How to use YAML files to store movement data.
- How software on one computer can request a robot behaviour.
- How to test a movement in simulation before using a real robot.
- How Python sockets and ROS 2 solve similar communication problems in different ways.

## How does a behaviour reach the robot?

```text
Student computer
      │ requests a behaviour
      ▼
Teacher computer
      │ checks and runs the approved movement
      ▼
Simulation first, then the real UR5e only with teacher approval
```

In the classroom, students do not connect directly to the real UR5e. The teacher computer manages access to the robot and supervises any real movement.

## Two ways to build the project

We will implement a similar social behaviour using two architectures:

| Project stage  | Student request                                                                  | Simulation and execution                                        |
| -------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Python sockets | The client sends the complete YAML sequence to a TCP server.                     | RoboDK, then the real UR5e only with approval.                  |
| ROS 2          | The student publishes a behaviour name. The server loads the matching YAML file. | Fake UR5e with MoveIt 2, then the real UR5e only with approval. |

The two YAML files may describe similar poses, but their formats and execution methods are different.

In ROS 2, a **topic** carries the requested behaviour name. A **service** asks the server to run that behaviour. The server finds the YAML file and starts the sequence.

## From an idea to a tested movement

1. Choose what the movement means to a person.
2. Choose safe starting, middle, and ending poses.
3. Create a YAML sequence for each architecture.
4. Test the complete sequence in simulation.
5. Check the motion and fix problems.
6. Ask the teacher to review it before any real-robot test.

The ROS 2 handshake example already in the repository has five steps: start pose, approach, handshake pose, retreat, and return to the start pose. It moves to a fixed pose; it does not detect or follow a person's hand.

## What will you submit?

1. A Python sockets YAML file.
2. A ROS 2 YAML file.
3. A short description of the social meaning and chosen poses.
4. Evidence that both versions worked in simulation.
5. Evidence of a supervised real-robot test, **if the teacher approves one**.
6. A short comparison of the two architectures.

In the comparison, explain:

- What the student computer sends in each version.
- Where the server finds the YAML file.
- How the teacher computer manages robot access.
- How the software reports success or errors.
- What ROS 2 provides compared with the custom TCP protocol.

## Safety comes first

- Test every movement in simulation first.
- Keep the work area clear and use slow, smooth movements.
- Check the start, middle, and end poses.
- Never run an unapproved movement on the real UR5e.
- A real-robot test needs teacher approval and supervision.
- Voice and face recognition are not safety systems.

The ROS 2 pose sequence uses inverse kinematics to find joint targets. A successful IK result does not by itself prove that the full path is collision-free.

## Suggested timing for the introduction

| Time       | Topic                                                     |
| ---------- | --------------------------------------------------------- |
| 0–3 min   | The project challenge and social behaviours               |
| 3–8 min   | What students will learn                                  |
| 8–14 min  | The two architectures and how a request reaches the robot |
| 14–20 min | Design, simulation, and safety                            |
| 20–25 min | Final deliverables                                        |
| 25–30 min | Fork and clone check                                      |

The guided handshake simulation below is a separate practical activity. It may take **30–45 minutes**, depending on how the classroom environment has been prepared.

# Guided practical activity: fork, clone, and simulate a handshake

## Before the activity

The teacher should prepare a The Construct environment that:

- runs **Ubuntu 22.04 and ROS 2 Humble**;
- has the project's ROS 2 dependencies installed and can build the workspace;
- includes the UR driver and MoveIt 2;
- supports a graphical view such as RViz, so students can see the fake robot move.

The activity uses **fake hardware only**. If the correct ROS 2 packages or a graphical view are not available, stop and ask the teacher to prepare the environment. Do not switch to a real robot.

Students need a GitHub account and access to The Construct.

## Part 1 — Create a personal fork and clone it

1. Open the [project repository on GitHub](https://github.com/manelpuig/UR5e_social_robotics).
2. Sign in to GitHub and select **Fork**. Create the fork in your own account.
3. Open the prepared ROS 2 Humble environment in The Construct and open a terminal.
4. Replace `GITHUB_USERNAME` with your GitHub username, then clone your fork:

   ```bash
   git clone https://github.com/GITHUB_USERNAME/UR5e_social_robotics.git
   cd UR5e_social_robotics
   ```
5. Check that the clone points to your fork:

   ```bash
   git remote -v
   git status
   ```

   The URL shown by `git remote -v` should contain your GitHub username.
6. Show the teacher your GitHub fork and the `git remote -v` output.

## Part 2 — Build the ROS 2 workspace

The project setup uses a virtual environment named `.venv-humble`. The classroom image should have it prepared before this activity.

From the repository folder, build the workspace:

```bash
source /opt/ros/humble/setup.bash
cd ~/UR5e_social_robotics
source .venv-humble/bin/activate
.venv-humble/bin/python /usr/bin/colcon build \
  --symlink-install \
  --base-paths src
source install/setup.bash
```

Check that this is a Humble environment:

```bash
echo "$ROS_DISTRO"
```

It should print `humble`. If the build fails, stop and ask the teacher to check the environment before continuing.

## Part 3 — Start the fake UR5e and the project nodes

Open **five terminals** in The Construct. In each terminal, prepare the project environment:

```bash
source /opt/ros/humble/setup.bash
cd ~/UR5e_social_robotics
source .venv-humble/bin/activate
source install/setup.bash
```

### Terminal 1 — Start the fake robot driver

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e \
  robot_ip:=192.168.0.20 \
  use_fake_hardware:=true \
  launch_rviz:=false
```

`use_fake_hardware:=true` is essential. This starts simulated hardware and does not connect to a physical UR5e. Keep the terminal running.

### Terminal 2 — Start MoveIt 2 and RViz

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e \
  launch_rviz:=true
```

Wait until the UR5e model appears and MoveIt 2 is ready.

### Terminal 3 — Start the sequence server

```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

Look for a message that says the sequence server is ready and check that its motion directory contains `handshake.yaml`.

### Terminal 4 — Start the behaviour client

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

Keep the terminal running.

### Terminal 5 — Request the handshake

```bash
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: 'handshake'}"
```

## What should happen?

The fake UR5e should perform the sequence shown in [`handshake.yaml`](../src/social_robot_behaviors/motions/handshake.yaml):

1. Move to the starting pose.
2. Move to the handshake approach pose.
3. Move to the handshake pose.
4. Retreat to the approach pose.
5. Return to the starting pose.

Watch the robot in RViz and check the terminal output for errors. The sequence represents a handshake movement, but it does not detect a person, make physical contact, or control a gripper.

If the motion fails, do not try it on a real robot. Save the error message and ask the teacher for help. Stop the ROS 2 nodes with `Ctrl+C` when the test is finished.

## Quick check before leaving

- [ ] I created a fork in my GitHub account.
- [ ] I cloned my fork in The Construct.
- [ ] `git remote -v` shows my fork.
- [ ] I used fake hardware.
- [ ] I saw the handshake sequence in RViz or recorded the error for the teacher.

## More information

- [Classroom architecture](2_UR5e_Classroom_Architecture.md)
- [Python sockets architecture](3_Python_Sockets_Architecture.md)
- [ROS 2 architecture](4_ROS2_Architecture.md)
- [Project responsibilities and deliverables](5_SocialRobotics_Project.md)
- [UR5e setup and Python environment](1_UR5e_setup.md)
- [ROS 2 practical guide](../src/1_Instructions_ros2_SocialRobotics_Project.md)
- [Python sockets practical guide](../Python_sockets_Robotic_project/1_Instructions_python_SocialRobotics_Project.md)
