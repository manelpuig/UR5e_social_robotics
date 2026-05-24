#!/usr/bin/env python3

import os

from ament_index_python.packages import (
    get_package_share_directory
)

from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    package_dir = get_package_share_directory(
        "social_robot_behaviors"
    )

    params_file = os.path.join(
        package_dir,
        "config",
        "behavior_client_params.yaml"
    )

    behavior_node = Node(
        package="social_robot_behaviors",
        executable="behavior_manager_client_node",
        name="behavior_manager_client_node",
        output="screen",
        parameters=[params_file]
    )

    return LaunchDescription([
        behavior_node
    ])