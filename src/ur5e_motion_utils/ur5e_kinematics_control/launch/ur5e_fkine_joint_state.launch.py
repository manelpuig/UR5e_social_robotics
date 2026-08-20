from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "target_deg",
            default_value="[0.0, -90.0, 90.0, 0.0, 90.0, 0.0]",
        ),
        DeclareLaunchArgument(
            "joint_states_topic",
            default_value="/joint_states",
        ),
        DeclareLaunchArgument("base_frame", default_value="base_link"),
        DeclareLaunchArgument("tcp_frame", default_value="tool0"),
        DeclareLaunchArgument("publish_duration_sec", default_value="1.0"),
        DeclareLaunchArgument("tf_timeout_sec", default_value="2.0"),
        Node(
            package="ur5e_kinematics_control",
            executable="ur5e_fkine_joint_state_exec",
            output="screen",
            parameters=[{
                "target_deg": LaunchConfiguration("target_deg"),
                "joint_states_topic": LaunchConfiguration("joint_states_topic"),
                "base_frame": LaunchConfiguration("base_frame"),
                "tcp_frame": LaunchConfiguration("tcp_frame"),
                "publish_duration_sec": LaunchConfiguration(
                    "publish_duration_sec"
                ),
                "tf_timeout_sec": LaunchConfiguration("tf_timeout_sec"),
            }],
        ),
    ])
