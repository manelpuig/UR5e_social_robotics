# Lab 1 --- Social Motion with the UR5e

## 1. Objective

In this laboratory you will design and execute a simple **social
motion** for a UR5e robot.

Examples include:

-   handshake
-   give five
-   waving
-   inviting a person
-   pointing
-   celebrating

You will:

1.  Create a new YAML motion sequence.
2.  Test it at home using the fake UR5e.
3.  Verify it with the instructor.
4.  Execute it on the real robot.

You do **not** need to modify the robot controller or the motion server.

------------------------------------------------------------------------

## 2. System architecture

The system uses:

-   a **topic** to request a social behavior;
-   a **service** to execute the corresponding robot motion.

``` mermaid
flowchart LR
    P["Command Publisher"]
    T(("/social_behavior"))
    C["Behavior Manager Client"]
    S["UR5e Sequence Server"]
    M["MoveIt 2"]
    R["UR5e"]

    P --> T
    T --> C
    C -- "/ur5e/run_sequence" --> S
    S --> M
    M --> R
```

The client **only sends the behavior name**, for example:

``` text
handshake
```

The Sequence Server locates:

``` text
handshake.yaml
```

and executes it through MoveIt 2.

------------------------------------------------------------------------

## 3. Student task

Create one original social behavior.

Requirements:

-   clear social meaning;
-   smooth movements;
-   safe initial pose;
-   safe final pose;
-   no collisions;
-   remain inside the robot workspace.

Create the YAML file in:

``` text
src/ur5e_motion_utils/ur5e_robot_controller/config/
```

Use descriptive names such as (add your group number in the social motion name):

``` text
groupX_wave.yaml
groupX_invite_person.yaml
groupX_show_agreement.yaml
```

------------------------------------------------------------------------

## 4. Home development

Develop and test your motion using the fake UR5e.

Recommended workflow:

``` text
Create YAML
      ↓
Build workspace
      ↓
Test with fake robot
      ↓
Correct the motion
```

When a **new YAML file** is created:

``` bash
cd ~/UR5e_social_robotics

colcon build --symlink-install

source install/setup.bash
```

Start the fake UR5e driver
```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e \
  robot_ip:=192.168.0.20 \
  use_fake_hardware:=true \
  launch_rviz:=false
```
> The IP address is required by the launch file but is not used to connect to a physical robot when fake hardware is enabled.

Start MoveIt 2 and RViz
```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e \
  launch_rviz:=true
```

Test the motion:

``` bash
ros2 launch ur5e_robot_controller \
        ur5e_pose_sequence.launch.py \
        sequence_file:=my_social_motion.yaml
```

------------------------------------------------------------------------

## 5. Laboratory workflow

When your motion works correctly:

1. Open a terminal on `/Documentation/Files/Send_motion` folder.

2. Run the Python program:

```bash
python3 send_social_motion.py
```
> Verify your PC-IP address on the python program

3. Enter the YAML filename when requested.

4. Enter the password for the `student` user on the professor PC.

If the copy is successful, you should see:

```text
File copied successfully.
```


## 6. Laboratory execution

On **PC-Professor** Start:

-   UR driver
```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e \
  robot_ip:=192.168.0.20 \
  use_fake_hardware:=false \
  launch_rviz:=false
```
> The External Control program must be loaded and started from the UR5e teach pendant when instructe

-   MoveIt 2
```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e \
  launch_rviz:=true
````

-   UR5e Sequence Server
```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

On **PC-Student** Start:
-   Behavior Manager Client
```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```
- Publish the desired behavior:

``` bash
ros2 topic pub --once /social_behavior std_msgs/msg/String \
"{data: 'my_social_motion'}"
```

Observe:

-   robot safety;
-   smoothness;
-   correct social meaning;
-   agreement between simulation and the real robot.

------------------------------------------------------------------------

## 7. Deliverables

Submit:

1.  Your YAML motion file.
2.  A short description of its social meaning.
3.  A short video using fake hardware.
4.  A short video using the real robot.
5.  A brief comparison between simulation and the real robot.

------------------------------------------------------------------------

## 8. Discussion

1.  Why is a ROS 2 topic used for the social command?
2.  Why does the server execute the YAML instead of the client?
3.  Why should every motion be tested with fake hardware first?
4.  How could voice recognition replace the terminal publisher?
5.  How could a camera trigger the same behavior?

## 9. Possible future extensions

The command publisher can later be replaced without modifying the motion server:

```text
Voice recognition
        ↓
/social_behavior
```

```text
Human gesture recognition
        ↓
/social_behavior
```

```text
RGB-D camera
        ↓
/social_behavior
```

```text
Graphical interface
        ↓
/social_behavior
```

```text
Large language model
        ↓
/social_behavior
```

All these interfaces can publish the same high-level behavior name.

This is one of the main advantages of a modular ROS 2 architecture.