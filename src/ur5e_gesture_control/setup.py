from glob import glob
from setuptools import find_packages, setup

package_name = 'ur5e_gesture_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/motions', glob('motions/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Independent UR5e gesture motion examples',
    license='MIT',
    entry_points={'console_scripts': [
        'ur5e_gesture = ur5e_gesture_control.ur5e_gesture:main',
        'ur5e_movej = ur5e_gesture_control.ur5e_movej:main',
        'ur5e_movel = ur5e_gesture_control.ur5e_movel:main',
        'ur5e_planned = ur5e_gesture_control.ur5e_planned:main',
        'ur5e_test_scene = ur5e_gesture_control.ur5e_test_scene:main',
    ]},
)
