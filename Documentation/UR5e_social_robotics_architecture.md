## Social Robotics architecture

ROS 2 workspace for social robotics applications with UR5e.

## Packages

- `ur5e_social_motion`: motion execution and pose sequences
- `social_robot_hri`: HRI app, voice, GPT interface, robot controller
- `social_robot_perception`: hand detection and 3D target estimation
- `social_robot_behaviors`: high-level social behaviors

## Workspace structure

```text
UR5e_social_robotics/
└── src/
    ├── ur5e_social_motion/
    ├── social_robot_hri/
    ├── social_robot_perception/
    └── social_robot_behaviors/
```