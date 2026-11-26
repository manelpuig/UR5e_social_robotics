"""Compute a complete Cartesian path from the actual or preview state."""
import math
from moveit_msgs.srv import GetCartesianPath
from ur5e_gesture_control.motion_common import JOINTS, describe_moveit_error, end_state


def move(context, step, start, execute):
    request = GetCartesianPath.Request()
    request.header.frame_id = context.frame
    request.start_state = start
    request.group_name = context.group
    request.link_name = context.link
    request.waypoints = [context.target(step).pose]
    request.max_step = float(context.common.get('cartesian_step_m', 0.01))
    request.jump_threshold = 0.0
    request.avoid_collisions = True
    if request.max_step <= 0:
        raise ValueError('cartesian_step_m must be positive')
    result = context.service(context.cartesian, request)
    if result.error_code.val != 1 or result.fraction < 0.999999:
        raise RuntimeError(f'Incomplete Cartesian path: fraction={result.fraction:.3f}, MoveIt error={describe_moveit_error(result.error_code)}')
    trajectory = result.solution
    jt = trajectory.joint_trajectory
    if not jt.points or not all(j in jt.joint_names for j in JOINTS):
        raise RuntimeError('Cartesian path has no complete joint trajectory')
    # Reject sudden changes, including a jump at the start of the path.
    limit = float(context.common.get('max_joint_step_rad', 0.3))
    if limit <= 0:
        raise ValueError('max_joint_step_rad must be positive')
    previous = dict(zip(start.joint_state.name, start.joint_state.position))
    last_time = -1.0
    # Slow the already time-parameterized trajectory for both scaling factors.
    scale = min(context.velocity, math.sqrt(context.acceleration))
    for index, point in enumerate(jt.points):
        current = dict(zip(jt.joint_names, point.positions))
        for joint in JOINTS:
            delta = abs(current[joint] - previous[joint])
            if delta > limit:
                raise RuntimeError(
                    f'Cartesian joint jump at point {index}, {joint}: '
                    f'{previous[joint]:.4f} -> {current[joint]:.4f} rad; '
                    f'difference={delta:.4f} rad, limit={limit:.4f} rad'
                )
        previous = current
        t = point.time_from_start.sec + point.time_from_start.nanosec * 1e-9
        if t <= last_time:
            raise RuntimeError('Cartesian trajectory has invalid timing')
        last_time = t
        scaled = t / scale
        point.time_from_start.sec = int(scaled)
        point.time_from_start.nanosec = int((scaled % 1) * 1e9)
        point.velocities = [v * scale for v in point.velocities]
        point.accelerations = [a * scale * scale for a in point.accelerations]
    if last_time <= 0:
        raise RuntimeError('Cartesian trajectory has no usable timing')
    context.show(start, trajectory)
    if execute:
        context.execute_trajectory(trajectory)
    return end_state(start, trajectory)


def main():
    from ur5e_gesture_control.ur5e_gesture import main_for_mode
    main_for_mode('moveL')
