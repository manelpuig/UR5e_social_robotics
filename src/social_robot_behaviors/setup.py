from setuptools import setup
import os
from glob import glob

package_name = 'social_robot_behaviors'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='manel',
    maintainer_email='manel@example.com',
    description='Social robot behavior orchestrator node',
    license='Apache-2.0',

    data_files=[

        # package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # package.xml
        ('share/' + package_name, ['package.xml']),

        # launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],

    entry_points={
        'console_scripts': [
            'social_behavior_manager = social_robot_behaviors.social_behavior_manager:main',
        ],
    },
)