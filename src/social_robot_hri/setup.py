from setuptools import setup
import os
from glob import glob

package_name = 'social_robot_hri'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],
    zip_safe=True,
    maintainer='Manel Puig',
    maintainer_email='puigmanel@gmail.com',
    description='HRI input package for social robot voice, face and gesture interfaces',
    license='MIT',
    entry_points={
        'console_scripts': [
            'voice_node = social_robot_hri.voice_node:main',
            'voice_interpreter_node = social_robot_hri.voice_interpreter_node:main',
            'face_verification_node = social_robot_hri.face_verification_node:main',
            'gesture_node = social_robot_hri.gesture_node:main',
            'gesture_interpreter_node = social_robot_hri.gesture_interpreter_node:main',
        ],
    },
)
