"""Plan a collision-aware joint path to an IK solution."""
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint
from ur5e_gesture_control.motion_common import JOINTS, describe_moveit_error, end_state


def move(context, step, start, execute):
    joints = context.inverse_kinematics(context.target(step), start, step)
    goal = MoveGroup.Goal()
    goal.request.group_name = context.group
    goal.request.start_state = start
    goal.request.num_planning_attempts = 5
    goal.request.allowed_planning_time = 5.0
    goal.request.max_velocity_scaling_factor = context.velocity
    goal.request.max_acceleration_scaling_factor = context.acceleration
    constraints = Constraints()
    for name, value in zip(JOINTS, joints):
        constraint = JointConstraint()
        constraint.joint_name = name
        constraint.position = value
        constraint.tolerance_above = 0.001
        constraint.tolerance_below = 0.001
        constraint.weight = 1.0
        constraints.joint_constraints.append(constraint)
    goal.request.goal_constraints.append(constraints)
    goal.planning_options.plan_only = True
    result = context.action(context.planner, goal)
    if result.error_code.val != 1 or not result.planned_trajectory.joint_trajectory.points:
        raise RuntimeError(f'Planning failed or trajectory empty: {describe_moveit_error(result.error_code)}')
    trajectory = result.planned_trajectory
    context.show(start, trajectory)
    if execute:
        context.execute_trajectory(trajectory)
    return end_state(start, trajectory)


def main():
    from ur5e_gesture_control.ur5e_gesture import main_for_mode
    main_for_mode('planned')
