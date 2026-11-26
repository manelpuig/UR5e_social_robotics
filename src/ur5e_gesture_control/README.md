# UR5e gesture control

This optional ROS 2 Humble package defines a gesture as a list of pose targets.
Each step selects a movement type. The package is independent of the existing
classroom sequence server and does not change its nodes or launch files.

## Movement types

| Type | How it moves | Collision checking |
| --- | --- | --- |
| `moveJ` | IK finds joint angles; the joint controller interpolates to them over `duration`. | The direct path is **not** checked against the planning scene. |
| `moveL` | MoveIt computes a Cartesian path from the current pose to the target pose. | The Cartesian request enables collision checking. |
| `planned` | IK finds joint angles; MoveIt plans a joint trajectory to those angles. | MoveIt checks the robot and the planning scene during planning. |

These names describe the intended movements; they do not claim exact RoboDK or
UR controller equivalence. A joint-space path is not necessarily straight in
Cartesian space. MoveIt does not guarantee the shortest or smoothest path.

`moveJ` and `planned` use the current joint state as the IK seed by default.
Set `seed_from_joint_states: false` and provide six `seed_joints` in degrees
to use a different IK seed. A seed is a starting guess, not a guarantee of the
final configuration. The calculated angles are printed in degrees. `moveL`
starts from the current joint state and does not use a custom seed.

MoveL requests the whole Cartesian path with collision checking enabled. It
rejects a partial path, missing trajectory, invalid timing, or a joint change
larger than `max_joint_step_rad` between consecutive samples. This is a jump
check, not a singularity analysis. It slows the time-parameterized path using
the velocity and acceleration factors; it does not create valid timing if
MoveIt returns an untimed path. The node stops if any step fails. There is no
automatic fallback to another movement type.

## Gesture YAML

See [handshake_moveit.yaml](motions/handshake_moveit.yaml). Each step has a
name, `motion_type`, `target_xyz` in millimetres and `target_rpy` in degrees.
Targets are expressed in `target_frame`, normally `table`, and transformed to
`planning_frame`, normally `base_link`. `sleep_after` is used during execution.
`duration` applies to direct MoveJ; MoveIt determines the timing of `planned`
and `moveL`. `max_velocity` and `max_acceleration` are scaling factors in
`(0, 1]` for MoveIt trajectories; they do not limit direct MoveJ.

The format retains the existing pose fields. The old sequence node ignores
`motion_type`: if given this YAML, it will still use its original direct joint
motion for every step, not the movement types described here. This package
installs its own YAML and does not modify the classroom files.

## Build and start

Use the existing ROS 2 Humble workspace and its prepared `.venv-humble`:

```bash
cd ~/UR5e_social_robotics
source /opt/ros/humble/setup.bash
source .venv-humble/bin/activate
.venv-humble/bin/python /usr/bin/colcon build --packages-up-to ur5e_gesture_control
source install/setup.bash
ros2 pkg executables ur5e_gesture_control
```

Use the same ROS domain and source the environment in each new terminal. In
terminal 1, start the fake driver:

```bash
cd ~/UR5e_social_robotics
source /opt/ros/humble/setup.bash
source .venv-humble/bin/activate
source install/setup.bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=true launch_rviz:=false
```

In terminal 2, start MoveIt and RViz:

```bash
cd ~/UR5e_social_robotics
source /opt/ros/humble/setup.bash
source .venv-humble/bin/activate
source install/setup.bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur5e launch_rviz:=true
```

The gesture launch publishes `base_link` to `table` using the same static
transform as the existing sequence launch. Do not run another publisher of
this transform at the same time. The TF frame is not a collision object. The
optional `ur5e_test_scene_exe` from `ur5e_robot_controller` can add the test
table; its planning scene is shared with all clients of the same MoveIt.
Do not add it while the class uses that instance.

## Preview and execute

In terminal 3, source the environment as above and preview the complete gesture:

```bash
ros2 launch ur5e_gesture_control ur5e_gesture.launch.py \
  sequence_file:=handshake_moveit.yaml execute:=false
```

The node does not move the robot. It uses predicted end states for later
steps. For MoveJ it computes only the IK endpoint: it does not calculate,
display or validate the controller's interpolated path. MoveL and planned
steps publish each resulting trajectory for RViz. These are individual
displays, not a saved, approved full sequence. Since MoveJ is not checked,
the preview cannot establish that the whole gesture is collision-free.

To test one step from the current robot state:

```bash
ros2 launch ur5e_gesture_control ur5e_gesture.launch.py \
  sequence_file:=handshake_moveit.yaml step_name:=handshake execute:=false
```

With fake hardware only, run the gesture:

```bash
ros2 launch ur5e_gesture_control ur5e_gesture.launch.py \
  sequence_file:=handshake_moveit.yaml execute:=true
```

The node recalculates every movement before execution. It does not execute a
previously approved preview. Watch the terminal for each step and `Gesture
finished.` Stop if a movement is unexpected. Direct MoveJ may cross the table
even when MoveIt knows about it. Do not treat a successful fake-hardware test
as authorization to use a real robot.

The individual executables can test a named step. They require an absolute
installed YAML path and an already available `base_link` to `table` TF:

```bash
ros2 run ur5e_gesture_control ur5e_movej --ros-args \
  -p sequence_file:="$HOME/UR5e_social_robotics/install/ur5e_gesture_control/share/ur5e_gesture_control/motions/handshake_moveit.yaml" \
  -p step_name:=home_start -p execute:=false
```

Use `ur5e_movel` with `step_name:=handshake` or `ur5e_planned` with
`step_name:=approach_handshake`. Each executable requires the selected step to
have the matching `motion_type`.

## Test a planned step with an obstacle

The independent `ur5e_test_scene` executable adds a table and a vertical
cylinder to the shared MoveIt planning scene. It does not change the robot
model or start automatically with the gesture. The table is 1 x 1 x 0.05 m,
with its top at `base_link` z=0. The cylinder is 0.50 m high, radius 0.035 m,
centred at `(0.05, 0.39, 0.25)` m in `base_link`. Its axis is vertical and
its bottom is at the table surface. This trial position is closer to
`home_start` than the original midpoint position. Check both endpoint robot
configurations for collision in RViz; this position has not been validated
against the robot model and may not intersect the planned trajectory.

Build and source the package as described above. Start the fake driver, MoveIt
and RViz, then run this in another sourced terminal:

```bash
ros2 run ur5e_gesture_control ur5e_test_scene
```

Keep that terminal open. Wait for `Table and cylinder added` and check both
objects in RViz. Stop the original `ur5e_robot_controller` test scene first;
its table and this table should not be present at the same time. The new node
also refuses to replace its own existing IDs. The scene is shared by all
clients of this MoveIt instance, so do not run this test during the class.

In another sourced terminal, preview the complete gesture:

```bash
ros2 launch ur5e_gesture_control ur5e_gesture.launch.py \
  sequence_file:=handshake_moveit.yaml execute:=false
```

The `approach_handshake` plan starts from the predicted `home_start` endpoint.
Inspect its path around the cylinder in RViz and compare it with a preview
without the cylinder. It may take a different path, fail if no plan is found,
or already avoid the cylinder without any change. A successful preview does
not check the direct MoveJ path. If the initial state or a target collides
with an object, planning can fail; inspect the robot and scene in RViz.
Testing only `step_name:=approach_handshake` starts from the actual joint
state, not the predicted `home_start` state.

When finished, press Ctrl+C in the test-scene terminal while MoveIt is still
running. Check that both objects disappear in RViz. If cleanup fails or the
process is killed, with MoveIt still running and the scene node stopped, run:

```bash
ros2 run ur5e_gesture_control ur5e_test_scene --ros-args -p remove_only:=true
```

This removes only `gesture_test_table` and `gesture_test_cylinder`. Do not use
the cleanup command while another instance of this test scene is active.

## Future improvements

1. Check the actual direct joint trajectory against the planning scene, with
   a model consistent with the controller's interpolation.
2. Preserve a full plan for inspection and explicitly execute the same plan,
   checking start state and scene validity before execution.
3. Offer an explicit fallback from a failed MoveJ or MoveL to free planning,
   before moving and only when the gesture permits a different path.
4. Generate and compare several plans and IK solutions, scoring joint travel,
   TCP path length, obstacle clearance and proximity to singularities.
5. Experiment with user-defined waypoints, then automatic waypoint candidates
   and resumption of a Cartesian path around an obstacle or singularity.

These are future ideas, not features of this first version. Test progressively
in simulation and validate robot geometry, collision objects, controller limits
and installation safety before considering real hardware.
