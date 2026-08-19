# Social Robotics Project with the UR5e

## Objective

The objective of this project is to implement and test a social motion on the UR5e using two client-server architectures:

1. Python sockets and URScript.
2. ROS 2 and MoveIt 2.

Each group will reuse the social motion designed and simulated in RoboDK during Activity 1. The software, clients, servers, and robot controllers are already prepared. Students only need to define and adjust the intermediate robot poses in the required YAML motion files.

Examples include waving, greeting, giving a high five, pointing, inviting a person, or celebrating.

## Project Sequence

```text
RoboDK motion from Activity 1
              |
              v
Session 1: Python sockets + URScript
              |
              v
Session 2: ROS 2 + MoveIt 2
              |
              v
Session 3: improve or create another motion
```

The same social behavior will be used in Sessions 1 and 2. This makes it possible to compare the two architectures without changing the objective of the motion.

## Student Task

Students do not need to program or modify the communication architecture. Their work is limited to:

- selecting safe initial, intermediate, and final poses;
- writing the poses in the corresponding YAML format;
- simulating and correcting the motion;
- sending the behavior name from the prepared client;
- evaluating the motion on the real robot.

The Python sockets and ROS 2 YAML formats are different. Students will use the same intermediate poses but adapt them to the provided example file for each architecture.

## General Safety Rules

- Simulate and validate every motion before using the real robot.
- Use a safe initial and final pose.
- Keep all poses inside the robot workspace.
- Avoid collisions, joint limits, sudden movements, and excessive speed.
- Do not execute a motion without instructor approval.
- Keep the emergency stop accessible during every experiment.

## Session 1 - Python Sockets and URScript

### Before class: work at home

1. Select the social motion developed in RoboDK during Activity 1.
2. Describe its social meaning.
3. Identify its safe initial, intermediate, and final poses.
4. Create the Python sockets YAML file using an existing file as a template.
5. Save it in `Python_sockets_Robotic_project/motions/` with a descriptive group name, for example `groupX_wave.yaml`.
6. Check the YAML file and the client-server request locally.
7. Verify the motion poses with the available simulation tools before coming to the laboratory.

### In class: experimental work

1. Present the social motion and its YAML file to the instructor.
2. Review the poses, velocities, accelerations, and workspace.
3. Connect the prepared Python client on the student computer to the Python server on the instructor computer.
4. Request the behavior by its name.
5. Perform the first supervised execution on the real UR5e at reduced speed.
6. Record any unsafe pose, abrupt movement, or difference from the RoboDK simulation.

## Session 2 - ROS 2 and MoveIt 2

### Before class: work at home

1. Use the same social motion and intermediate poses from Session 1.
2. Create the ROS 2 YAML file using an existing ROS 2 motion as a template.
3. Save it in `src/ur5e_motion_utils/ur5e_robot_controller/config/` with the same behavior name.
4. Build the ROS 2 workspace in The Construct.
5. Start the fake UR5e driver, MoveIt 2, and RViz.
6. Simulate the complete sequence in The Construct.
7. Correct any planning, workspace, collision, or smoothness problem.

### In class: experimental work

1. Transfer the validated ROS 2 YAML file to the instructor computer using `Documentation/Files/Send_motion/send_social_motion.py`.
2. Connect the prepared ROS 2 Behavior Manager Client on the student computer to the Sequence Server on the instructor computer.
3. Publish the behavior name on `/social_behavior`.
4. The client requests `/ur5e/run_sequence`, and the server executes the YAML sequence through MoveIt 2.
5. Perform several supervised trials on the real UR5e.
6. Compare the sockets execution with the ROS 2 execution.

## Session 3 - Motion Improvement or Extension

### Before class: work at home

1. Improve the main motion using the observations from Sessions 1 and 2.
2. Adjust the intermediate poses, duration, pauses, or social expressiveness.
3. Simulate the final ROS 2 version again in The Construct.
4. If the main motion is already complete, prepare and simulate a second social motion.

### In class: experimental work

1. Present and execute the final version using the ROS 2 architecture.
2. Evaluate its safety, smoothness, repeatability, and social meaning.
3. Explain the improvements made during the project.
4. Compare RoboDK, Python sockets, ROS 2 simulation, and real-robot execution.
5. If time permits, test the second motion after instructor approval.

## Final Deliverables

Each group must submit:

1. The Python sockets YAML motion file.
2. The ROS 2 YAML motion file.
3. A short description of the social meaning and intermediate poses.
4. Evidence of the ROS 2 simulation in The Construct.
5. A short video of the final experiment with the real UR5e.
6. A brief comparison between Python sockets and ROS 2.

## Supporting Documentation

- `3a_Social_Robotics_Python_Sockets_Architecture.md`: Python sockets architecture.
- `3b_Lab_Social_Robotics_UR5e_Python_Sockets.md`: Python sockets laboratory instructions.
- `4a_Social_Robotics_ROS2_Architecture.md`: ROS 2 architecture.
- `4b_Lab_Social_Motion_UR5e_ROS2.md`: ROS 2 simulation and laboratory instructions.
