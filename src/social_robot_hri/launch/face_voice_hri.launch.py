#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    reference_image = LaunchConfiguration('reference_image')
    camera_index = LaunchConfiguration('camera_index')

    return LaunchDescription([
        DeclareLaunchArgument(
            'reference_image',
            description='Absolute path to the authorised-user image',
        ),
        DeclareLaunchArgument('camera_index', default_value='0'),
        Node(
            package='social_robot_hri',
            executable='voice_node',
            name='voice_node',
            output='screen',
        ),
        Node(
            package='social_robot_hri',
            executable='voice_interpreter_node',
            name='voice_interpreter_node',
            output='screen',
            parameters=[{'output_topic': '/social_behavior/request'}],
        ),
        Node(
            package='social_robot_hri',
            executable='face_verification_node',
            name='face_verification_node',
            output='screen',
            parameters=[{
                'reference_image': reference_image,
                'camera_index': ParameterValue(camera_index, value_type=int),
            }],
        ),
    ])
