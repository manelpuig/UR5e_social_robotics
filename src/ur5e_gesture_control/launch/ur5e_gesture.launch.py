from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    path = PathJoinSubstitution([FindPackageShare('ur5e_gesture_control'), 'motions',
                                 LaunchConfiguration('sequence_file')])
    table = Node(package='tf2_ros', executable='static_transform_publisher',
                 name='gesture_table_tf', output='screen',
                 condition=IfCondition(LaunchConfiguration('publish_table_tf')),
                 arguments=['0', '0', '0', '0', '0', '1', '0', 'base_link', 'table'])
    gesture = Node(package='ur5e_gesture_control', executable='ur5e_gesture', output='screen',
                   parameters=[{'sequence_file': path,
                                'step_name': ParameterValue(LaunchConfiguration('step_name'), value_type=str),
                                'execute': ParameterValue(LaunchConfiguration('execute'), value_type=bool)}])
    return LaunchDescription([
        DeclareLaunchArgument('sequence_file', default_value='handshake_moveit.yaml'),
        DeclareLaunchArgument('step_name', default_value=''),
        DeclareLaunchArgument('execute', default_value='false'),
        DeclareLaunchArgument('publish_table_tf', default_value='true'),
        table,
        TimerAction(period=2.0, actions=[gesture]),
        RegisterEventHandler(OnProcessExit(target_action=gesture,
                             on_exit=[EmitEvent(event=Shutdown(reason='Gesture finished'))])),
    ])
