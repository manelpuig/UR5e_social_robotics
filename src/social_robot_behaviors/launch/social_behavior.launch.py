from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='social_robot_behaviors',
            executable='social_behavior_manager',
            output='screen'
        )

    ])