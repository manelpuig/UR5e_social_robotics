from setuptools import setup

package_name = 'social_robot_behaviors'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='High-level social robot behaviors such as handshake and high-five.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'behavior_manager = social_robot_behaviors.behavior_manager:main',
            'handshake_behavior = social_robot_behaviors.handshake_behavior:main',
            'highfive_behavior = social_robot_behaviors.highfive_behavior:main',
        ],
    },
)