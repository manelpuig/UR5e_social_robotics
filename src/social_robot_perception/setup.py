from setuptools import setup
from glob import glob
import os

package_name = 'social_robot_perception'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='Perception package for hand detection and 3D hand target estimation.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hand_detector_yolo = social_robot_perception.hand_detector_yolo:main',
            'hand_pose_3d_estimator = social_robot_perception.hand_pose_3d_estimator:main',
            'hand_target_selector = social_robot_perception.hand_target_selector:main',
        ],
    },
)