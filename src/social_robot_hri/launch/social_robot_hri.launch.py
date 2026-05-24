#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    voice_node = Node(
        package='social_robot_hri',
        executable='voice_node',
        name='voice_node',
        output='screen'
    )

    voice_interpreter_node = Node(
        package='social_robot_hri',
        executable='voice_interpreter_node',
        name='voice_interpreter_node',
        output='screen'
    )

    return LaunchDescription([
        voice_interpreter_node,
        voice_node,
    ])