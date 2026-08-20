from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "target_deg",
            default_value="[0.0, -90.0, 90.0, 0.0, 90.0, 0.0]"
        ),
        DeclareLaunchArgument(
            "time_sec",
            default_value="5.0"
        ),
        DeclareLaunchArgument(
            "controller_topic",
            default_value="/joint_trajectory_controller/joint_trajectory"
        ),
        DeclareLaunchArgument("base_frame", default_value="base_link"),
        DeclareLaunchArgument("tcp_frame", default_value="tool0"),
        DeclareLaunchArgument("tf_timeout_sec", default_value="2.0"),

        Node(
            package="ur5e_kinematics_control",
            executable="ur5e_joint_target_exec",
            output="screen",
            parameters=[{
                "target_deg": LaunchConfiguration("target_deg"),
                "time_sec": LaunchConfiguration("time_sec"),
                "controller_topic": LaunchConfiguration("controller_topic"),
                "base_frame": LaunchConfiguration("base_frame"),
                "tcp_frame": LaunchConfiguration("tcp_frame"),
                "tf_timeout_sec": LaunchConfiguration("tf_timeout_sec"),
            }],
        )
    ])
