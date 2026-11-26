"""Shared ROS interfaces for the individual motions and gesture runner."""
import copy
import math
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from moveit_msgs.action import ExecuteTrajectory, MoveGroup
from moveit_msgs.msg import DisplayTrajectory, MoveItErrorCodes, RobotState
from moveit_msgs.srv import GetCartesianPath, GetPositionIK
from control_msgs.action import FollowJointTrajectory
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs

JOINTS = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
          'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

ACTION_STATUS = {
    0: 'UNKNOWN', 1: 'ACCEPTED', 2: 'EXECUTING', 3: 'CANCELING',
    4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED',
}


def describe_moveit_error(code):
    """Show the MoveIt code and its message name, if this ROS version knows it."""
    value = code.val
    names = [name for name in dir(MoveItErrorCodes)
             if name.isupper() and getattr(MoveItErrorCodes, name) == value]
    name = '/'.join(names) if names else 'UNKNOWN'
    detail = getattr(code, 'message', '')
    source = getattr(code, 'source', '')
    suffix = f', message={detail}' if detail else ''
    suffix += f', source={source}' if source else ''
    return f'{value} ({name}){suffix}'


def describe_controller_error(result):
    code = result.error_code
    constants = FollowJointTrajectory.Result
    names = [name for name in dir(constants)
             if name.isupper() and getattr(constants, name) == code]
    name = '/'.join(names) if names else 'UNKNOWN'
    detail = getattr(result, 'error_string', '')
    return f'{code} ({name})' + (f', message={detail}' if detail else '')


class MotionContext(Node):
    def __init__(self, common):
        super().__init__('ur5e_gesture_motion')
        self.common = common
        self.group = common.get('group_name', 'ur_manipulator')
        self.link = common.get('ik_link', 'tool0')
        self.frame = common.get('planning_frame', 'base_link')
        self.target_frame = common.get('target_frame', 'table')
        self.velocity = float(common.get('max_velocity', 0.1))
        self.acceleration = float(common.get('max_acceleration', 0.1))
        if not (0 < self.velocity <= 1 and 0 < self.acceleration <= 1):
            raise ValueError('Scaling factors must be in (0, 1]')
        self.joints = None
        self.joint_version = 0
        self.create_subscription(JointState, '/joint_states', self._on_joints, qos_profile_sensor_data)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.ik = self.create_client(GetPositionIK, '/compute_ik')
        self.cartesian = self.create_client(GetCartesianPath, '/compute_cartesian_path')
        self.planner = ActionClient(self, MoveGroup, '/move_action')
        # Node.executor belongs to rclpy; keep the action client under its own name.
        self.trajectory_executor = ActionClient(self, ExecuteTrajectory, '/execute_trajectory')
        self.controller = ActionClient(self, FollowJointTrajectory, common.get(
            'controller_action', '/scaled_joint_trajectory_controller/follow_joint_trajectory'))
        self.display = self.create_publisher(DisplayTrajectory, '/display_planned_path', 10)

    def _on_joints(self, msg):
        if all(name in msg.name for name in JOINTS) and len(msg.name) == len(msg.position):
            self.joints = msg
            self.joint_version += 1

    def state(self, newer_than=None):
        deadline = time.monotonic() + 10
        while rclpy.ok() and time.monotonic() < deadline:
            if self.joints is not None and (newer_than is None or self.joint_version > newer_than):
                state = RobotState()
                state.joint_state = copy.deepcopy(self.joints)
                return state
            rclpy.spin_once(self, timeout_sec=0.1)
        raise RuntimeError('No fresh complete /joint_states received')

    def wait(self, future, timeout=30.0):
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        if not future.done():
            raise RuntimeError('ROS request timed out')
        if future.exception() is not None:
            raise RuntimeError(f'ROS request failed: {future.exception()}')
        return future.result()

    def service(self, client, request):
        if not client.wait_for_service(timeout_sec=10.0):
            raise RuntimeError(f'Service unavailable: {client.srv_name}')
        return self.wait(client.call_async(request))

    def action(self, client, goal):
        if not client.wait_for_server(timeout_sec=10.0):
            raise RuntimeError('Action server unavailable')
        handle = self.wait(client.send_goal_async(goal))
        if not handle.accepted:
            raise RuntimeError('Action goal rejected')
        # Do not time out while a robot trajectory may still be executing.
        rclpy.spin_until_future_complete(self, result_future := handle.get_result_async())
        if not result_future.done() or result_future.exception() is not None:
            raise RuntimeError('Action result unavailable')
        result = result_future.result()
        if result.status != 4:
            status = ACTION_STATUS.get(result.status, 'UNKNOWN')
            details = ''
            if isinstance(goal, (MoveGroup.Goal, ExecuteTrajectory.Goal)):
                details = f'; MoveIt error: {describe_moveit_error(result.result.error_code)}'
            elif isinstance(goal, FollowJointTrajectory.Goal):
                details = f'; controller error: {describe_controller_error(result.result)}'
            raise RuntimeError(f'Action status {result.status} ({status}){details}')
        return result.result

    def target(self, step):
        xyz = step['target_xyz']
        rpy = step['target_rpy']
        if len(xyz) != 3 or len(rpy) != 3:
            raise ValueError('target_xyz and target_rpy must each have three values')
        roll, pitch, yaw = [math.radians(float(v)) / 2 for v in rpy]
        cr, sr = math.cos(roll), math.sin(roll)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cy, sy = math.cos(yaw), math.sin(yaw)
        pose = PoseStamped()
        pose.header.frame_id = self.target_frame
        pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = [float(v) / 1000 for v in xyz]
        pose.pose.orientation.x = sr * cp * cy - cr * sp * sy
        pose.pose.orientation.y = cr * sp * cy + sr * cp * sy
        pose.pose.orientation.z = cr * cp * sy - sr * sp * cy
        pose.pose.orientation.w = cr * cp * cy + sr * sp * sy
        deadline = time.monotonic() + 10
        while rclpy.ok() and time.monotonic() < deadline:
            if self.buffer.can_transform(self.frame, self.target_frame, rclpy.time.Time()):
                transform = self.buffer.lookup_transform(self.frame, self.target_frame, rclpy.time.Time())
                pose.pose = tf2_geometry_msgs.do_transform_pose(pose.pose, transform)
                pose.header.frame_id = self.frame
                return pose
            rclpy.spin_once(self, timeout_sec=0.1)
        raise RuntimeError(f'Transform unavailable: {self.frame} <- {self.target_frame}')

    def inverse_kinematics(self, pose, start, step):
        request = GetPositionIK.Request()
        request.ik_request.group_name = self.group
        request.ik_request.ik_link_name = self.link
        request.ik_request.pose_stamped = pose
        request.ik_request.robot_state = copy.deepcopy(start)
        if not step.get('seed_from_joint_states', self.common.get('seed_from_joint_states', True)):
            seed = step.get('seed_joints', self.common.get('seed_joints'))
            if seed is None or len(seed) != 6:
                raise ValueError('Six seed_joints are required when using a custom seed')
            positions = dict(zip(request.ik_request.robot_state.joint_state.name,
                                 request.ik_request.robot_state.joint_state.position))
            positions.update(zip(JOINTS, [math.radians(float(v)) for v in seed]))
            js = request.ik_request.robot_state.joint_state
            js.position = [positions[n] for n in js.name]
        timeout = float(self.common.get('ik_timeout_sec', 1.0))
        if timeout <= 0:
            raise ValueError('ik_timeout_sec must be positive')
        request.ik_request.timeout.sec = int(timeout)
        request.ik_request.timeout.nanosec = int((timeout % 1) * 1e9)
        result = self.service(self.ik, request)
        if result.error_code.val != 1:
            raise RuntimeError(f'IK failed: {describe_moveit_error(result.error_code)}')
        positions = dict(zip(result.solution.joint_state.name, result.solution.joint_state.position))
        values = [float(positions[name]) for name in JOINTS]
        self.get_logger().info('IK goal (degrees): ' + str([round(math.degrees(v), 2) for v in values]))
        return values

    def show(self, start, trajectory):
        msg = DisplayTrajectory()
        msg.trajectory_start = start
        msg.trajectory.append(trajectory)
        self.display.publish(msg)

    def execute_trajectory(self, trajectory):
        goal = ExecuteTrajectory.Goal()
        goal.trajectory = trajectory
        result = self.action(self.trajectory_executor, goal)
        if result.error_code.val != 1:
            raise RuntimeError(f'MoveIt execution failed: {describe_moveit_error(result.error_code)}')


def end_state(start, trajectory):
    state = copy.deepcopy(start)
    jt = trajectory.joint_trajectory
    positions = dict(zip(state.joint_state.name, state.joint_state.position))
    positions.update(zip(jt.joint_names, jt.points[-1].positions))
    state.joint_state.position = [positions[n] for n in state.joint_state.name]
    return state
