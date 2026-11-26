"""Direct joint motion: IK followed by a controller joint target."""
from control_msgs.action import FollowJointTrajectory
from moveit_msgs.msg import RobotTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from ur5e_gesture_control.motion_common import JOINTS, describe_controller_error, end_state


def move(context, step, start, execute):
    joints = context.inverse_kinematics(context.target(step), start, step)
    duration = float(step.get('duration', context.common.get('duration', 3.0)))
    if duration <= 0:
        raise ValueError('MoveJ duration must be positive')
    trajectory = RobotTrajectory()
    trajectory.joint_trajectory.joint_names = JOINTS
    point = JointTrajectoryPoint()
    point.positions = joints
    point.velocities = [0.0] * len(JOINTS)
    point.time_from_start.sec = int(duration)
    point.time_from_start.nanosec = int((duration % 1) * 1e9)
    trajectory.joint_trajectory.points.append(point)
    context.get_logger().warn('MoveJ is direct: its path is NOT collision checked.')
    if execute:
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = trajectory.joint_trajectory
        result = context.action(context.controller, goal)
        if result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
            raise RuntimeError(f'Controller failed: {describe_controller_error(result)}')
    else:
        context.get_logger().info('Preview: IK endpoint only; controller interpolation is not displayed.')
    return end_state(start, trajectory)


def main():
    from ur5e_gesture_control.ur5e_gesture import main_for_mode
    main_for_mode('moveJ')
