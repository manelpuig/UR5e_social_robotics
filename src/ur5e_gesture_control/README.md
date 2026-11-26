# UR5e gesture control

This ROS 2 Humble package runs YAML gestures independently of the classroom
sequence server. See [handshake_moveit.yaml](motions/handshake_moveit.yaml).

| Motion type | Behavior |
| --- | --- |
| `moveJ` | IK followed by a direct joint-controller movement. The path is **not collision checked**. |
| `moveL` | MoveIt computes a complete Cartesian path with collision checking and a joint-jump check. |
| `planned` | IK followed by a MoveIt joint-space plan that considers the planning scene. |

YAML positions are in millimetres and orientations in degrees. `moveJ` and
`planned` use the current joints as the IK seed unless `seed_from_joint_states`
is false and `seed_joints` is provided. A seed does not guarantee a particular
posture. `duration` applies to direct `moveJ`; MoveIt times the other motions.
The old sequence node ignores `motion_type` and retains its original behavior.

## Build

On the prepared ROS 2 Humble workspace:

```bash
cd ~/UR5e_social_robotics
source /opt/ros/humble/setup.bash
source .venv-humble/bin/activate
.venv-humble/bin/python /usr/bin/colcon build --packages-up-to ur5e_gesture_control
source install/setup.bash
```

Source the same environment in each terminal and use the same ROS domain.
Start the fake driver in terminal 1:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=true launch_rviz:=false
```

Start MoveIt and RViz in terminal 2:

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur5e launch_rviz:=true
```

## Test with a table and cylinder

In terminal 3, start the table and its `base_link` to `table` TF:

```bash
ros2 run ur5e_gesture_control scene_table
```

In terminal 4, add the cylinder:

```bash
ros2 run ur5e_gesture_control scene_cylinder --ros-args \
  -p x_cm:=-5.0 -p y_cm:=-39.0 -p height_cm:=25.0 -p radius_cm:=3.5
```

`x_cm` and `y_cm` use the `table` frame. All dimensions are in centimetres;
the cylinder base is on the table plane. The box is 1 x 1 x 0.05 m. Stop any
other table TF publisher or test-scene node before starting these nodes.
The planning scene is shared by all clients of this MoveIt instance.

In terminal 5, preview the gesture without moving:

```bash
ros2 launch ur5e_gesture_control ur5e_gesture.launch.py \
  sequence_file:=handshake_moveit.yaml execute:=false publish_table_tf:=false
```

Inspect the scene and paths in RViz. Preview computes only the MoveJ endpoint,
not the controller's path. It uses each predicted endpoint as the next start.
Testing a single step with `step_name:=handshake` instead starts from the
robot's current state.

To execute with fake hardware, use the same launch with `execute:=true`. It
replans; it does not execute the previously displayed preview. MoveJ is not
collision checked. Start with fake hardware and inspect the result before any
real robot test.

To change the cylinder, stop its node with Ctrl+C and run it again with new
parameters. At the end, stop the cylinder and then the table while MoveIt is
still running; each node removes its object. If cleanup fails, stop the relevant
node and run:

```bash
ros2 run ur5e_gesture_control scene_cylinder --ros-args -p remove_only:=true
ros2 run ur5e_gesture_control scene_table --ros-args -p remove_only:=true
```

If MoveIt reports an error, inspect its terminal for details such as collision
pairs. The gesture node also reports action and MoveIt/controller error codes.

## Future improvements

- Validate the direct MoveJ trajectory against the planning scene.
- Inspect and execute the same saved plan rather than replanning.
- Add an explicit fallback for a failed step.
- Compare IK solutions and plans using joint travel, obstacle clearance and
  singularity criteria; explore waypoints around obstacles.
