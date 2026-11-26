# Face and Voice HRI Demo with ROS 2

## Objective

Execute a social motion using face verification and voice control:

1. verify that the person is authorised;
2. listen to a voice command;
3. accept only commands that start with `robot`;
4. execute the requested motion with ROS 2.

The face is checked once when the HRI system starts. After authorisation, voice requests are enabled.

## Architecture

```text
Teacher PC - HRI client and robot server

Orbbec RGB topic -> face verification -----------------+
                                                       |
microphone -> speech recognition -> keyword "robot"   |
                              -> /social_behavior/request
                                                       |
                                                       v
                                              authorised request
                                              -> /social_behavior
                                                       |
                                                       v
                                              Behavior Manager
                                                       |
                                      ROS 2 /ur5e/run_sequence
                                                       |
                                                       v
                              sequence server -> MoveIt 2 -> UR5e
```

All nodes run on the Teacher PC because its camera, microphone and speakers are next to the robot. The person stands in front of the robot and interacts directly with this equipment. No Student PC is used in this demo.

Face and voice recognition are interaction tools. They are not robot safety systems.

## Before starting

The ROS 2 workspace and Orbbec driver are assumed to be installed. Rebuild the HRI and behavior packages as shown below so their Python executables use the virtual environment. Restart the Behavior Manager after building.

The `.venv-humble` environment must already be prepared as explained in [UR5e ROS 2 setup](Files/References/UR5e_ROS2_Setup.md). All Teacher terminals must use the same `ROS_DOMAIN_ID`.

Check these items:

- the Teacher PC has a camera, microphone, speakers and Internet connection;
- the authorised reference image is correct;
- `handshake.yaml` and `give5.yaml` are installed on the Teacher PC;
- the motions were already approved with fake hardware;
- no Python socket server is running.

Place the authorised user’s photo in `Documentation/Files/Camera&Microphone` and pass its filename as `authorised_user`. The example image is:

```text
~/UR5e_social_robotics/Documentation/Files/Camera&Microphone/Manel.png
```

## 1. Prepare Teacher PC container

In one Host terminal, launch the custom ROS2 Humble Container:
```bash
xhost +local:root
chmod +x entrypoint_pc.sh
docker compose up -d
```

In Teacher container terminal, build the repository with the virtual environment's Python:

```bash
.venv-humble/bin/python -m colcon build
```

Both executable headers should point to `/root/UR5e_social_robotics/.venv-humble/bin/python`. Activating the virtual environment alone does not change the interpreter recorded in previously built executables.

Open the `.bashrc` file and copy these lines at the end:
```bash
# ROS 2 Humble
source /opt/ros/humble/setup.bash
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash

# Project workspace
source /root/UR5e_social_robotics/install/setup.bash

# Python virtual environment for ROS HRI and YOLO
source /root/UR5e_social_robotics/.venv-humble/bin/activate

cd /root/UR5e_social_robotics
```

### Start the Orbbec Gemini 2

For driver installation, see the [Orbbec Gemini 2 installation guide](Files/Camera%26Microphone/Gemini2_installation.md).

In a dedicated Teacher container terminal, start the camera driver and leave it running for both the fake-hardware test and the real-robot demo:

```bash
ros2 launch orbbec_camera gemini2.launch.py \
  color_width:=640 color_height:=480 color_fps:=15 \
  depth_width:=640 depth_height:=400 depth_fps:=15 \
  depth_registration:=true enable_point_cloud:=false enable_ir:=false
```

From another prepared terminal, check that the RGB topic is publishing frames:

```bash
ros2 topic hz /camera/color/image_raw
```

Once a rate is shown, press Ctrl+C to stop the topic check. The HRI face verification node subscribes to this RGB topic through the `image_topic` launch argument.

## 2. Test with fake hardware

Teacher terminal 1:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=true launch_rviz:=false
```

Teacher terminal 2:

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e launch_rviz:=true
```

Teacher terminal 3:

```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

Teacher terminal 4:

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

### Check the microphone

To properly install the `Jabra SPEAK 510 USB` microphone, open a new terminal and install:
```bash
apt update
apt install -y alsa-utils
```
To identify the `speaker_device`, type:
```bash
aplay -l
```

To identify the `microphone_index`:
- list the microphones
```bash
python "Documentation/Files/Camera&Microphone/voice_transcription_node.py" --list-mics
```
- test the Jabra microphone. 

```bash
python "Documentation/Files/Camera&Microphone/voice_transcription_node.py" --mic 6
```
- Replace `6` with the index shown next to `Jabra SPEAK 510 USB`.
- At `Listening...`, say **robot give me five** and check the `Transcription:`
line. 
- Press Ctrl+C to release the microphone, then launch the demo in the same
terminal. The default index is `6`. Use the index you just tested if it differs.

```bash
ros2 launch social_robot_hri face_voice_hri.launch.py \
  authorised_user:=Manel.png \
  image_topic:=/camera/color/image_raw \
  microphone_index:=6 \
  speaker_device:=plughw:CARD=USB,DEV=0 \
  speech_voice:=en-gb
```

## 3. Verify the face gate

1. First show a non-authorised person to the camera.
2. Check that the window shows `UNKNOWN` and no motion request reaches `/social_behavior`.
3. Show the authorised person to the camera.
4. Check that the window shows `AUTHORISED`.
5. Check that the terminal reports `User authorised. HRI requests are enabled.`

Press `Q` in the verification window to cancel. To use a local OpenCV camera instead of the Orbbec ROS topic, omit `image_topic` and pass the appropriate `camera_index`.

## 4. Verify voice control

With fake hardware running, you can test the voice interpreter without
speaking into the microphone. After authorisation, run this in a separate
terminal and check that `/social_behavior` receives `handshake`.

```bash
ros2 topic pub --once /voice/text std_msgs/msg/String "{data: 'robot handshake'}"
```

The activation word must be the first word. Say:

```text
handshake
```

Nothing must move because the word `robot` is missing.

Now say:

```text
robot handshake
```

Check that:

- `/voice/text` receives the sentence;
- `/social_behavior` receives `handshake`;
- the Teacher server accepts the sequence;
- the complete motion is visible in RViz.

Then test:

```text
robot give me five
```

The expected behavior is `give5`. You can also say “robot high five”. The Teacher PC uses `espeak-ng` to announce
the face verification result and each command. Start unrecognised command
attempts with “robot” to hear “I have not understood”. During a sequence, new
motion commands and speech feedback are suppressed. When the sequence returns,
the node says “Manel, I am listening” once, using the name from the photo filename.
Use `speech_voice:=en-gb` in the launch command to try British pronunciation.
If verification is cancelled with `Q` before a match, it announces that the
person is unauthorised.

If the prompts are silent, use `aplay -l` inside the Teacher container to find
the playback device. Install `alsa-utils` if `aplay` is missing. For a Jabra listed
as card `USB`, device `0`, test playback with:

```bash
espeak-ng --stdout 'Hello Manel' | aplay -D 'plughw:CARD=USB,DEV=0'
```

Once audible, append `speaker_device:=plughw:CARD=USB,DEV=0` to the launch
command. The speaker device is independent of `microphone_index`.

## 5. Execute on the real UR5e

Stop the fake robot and HRI nodes. Keep the Orbbec camera driver running. Continue only with instructor approval.

Teacher terminal 1:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=false launch_rviz:=false
```

On the teach pendant, load the program containing **External Control** and press **Play**.

Teacher terminal 2:

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e launch_rviz:=true
```

Teacher terminal 3:

```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

Teacher terminal 4 - restart the Behavior Manager:

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

Teacher terminal 5 - restart face and voice control:

```bash
ros2 launch social_robot_hri face_voice_hri.launch.py \
  authorised_user:=Manel.png \
  image_topic:=/camera/color/image_raw \
  microphone_index:=6
```

After the authorised face is accepted, say one command at a time:

```text
robot handshake
robot give me five
```

Wait until one motion finishes before saying the next command. Stop the experiment immediately if the real movement differs from the fake-hardware test.

## Future extension

This demo can be extended with AI-based gesture identification using YOLO Pose and a 3D camera. A person could offer a hand instead of speaking.

The next guide, [Gesture HRI with YOLO Pose and a 3D Camera](5_Gesture_HRI_with_YOLO_Pose_and_3D_Camera.md), describes the current experimental design and launch commands. The complete gesture nodes are not finished or validated yet.
