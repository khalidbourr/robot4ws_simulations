#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():
    pkg_sim = FindPackageShare('robot4ws_simulations')
    
    # Declare arguments
    args = [
        DeclareLaunchArgument('start_gazebo', default_value='true', description='Start Gazebo simulator'),
        DeclareLaunchArgument('use_joystick', default_value='false'),
        DeclareLaunchArgument('use_keyboard', default_value='true'),
        DeclareLaunchArgument('include_terrain_slip_plugin', default_value='false'),
        DeclareLaunchArgument('neural_network_model', default_value='none'),
        DeclareLaunchArgument('include_wheels_terramechanic_model', default_value='false'),
        DeclareLaunchArgument('world_name', default_value='only_walls.sdf'),
        DeclareLaunchArgument('rocker_differential', default_value='false'),
        DeclareLaunchArgument('p310_env', default_value=os.environ.get('PYTHON_VENV', os.path.join(os.path.expanduser('~'), 'p310Venv/bin/python3.10'))),
        DeclareLaunchArgument('add_velodyneHDL32E', default_value='false'),
        DeclareLaunchArgument('lidar_organize_cloud', default_value='false'),
        DeclareLaunchArgument('load_sensors_plugins', default_value='true'),
    ]

    # Include main gazebo simulation
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([pkg_sim, 'launch', 'archimede_gazebo_simulation_with_kinematics.launch.py'])
        ]),
        launch_arguments={
            'start_gazebo': LaunchConfiguration('start_gazebo'),
            'world_name': LaunchConfiguration('world_name'),
            'include_terrain_slip_plugin': LaunchConfiguration('include_terrain_slip_plugin'),
            'neural_network_model': LaunchConfiguration('neural_network_model'),
            'include_wheels_terramechanic_model': LaunchConfiguration('include_wheels_terramechanic_model'),
            'rocker_differential': LaunchConfiguration('rocker_differential'),
            'add_velodyneHDL32E': LaunchConfiguration('add_velodyneHDL32E'),
            'lidar_organize_cloud': LaunchConfiguration('lidar_organize_cloud'),
            'load_sensors_plugins': LaunchConfiguration('load_sensors_plugins')
        }.items()
    )

    # Joystick teleop (conditional)
    joystick_teleop = GroupAction(
        condition=IfCondition(LaunchConfiguration('use_joystick')),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('robot4ws-teleop-joystick'),
                        'launch',
                        'controller.launch.py'
                    ])
                ]),
                launch_arguments={
                    'env': LaunchConfiguration('p310_env')
                }.items()                
            )
        ]
    )

    # Keyboard teleop (conditional)
    keyboard_teleop = GroupAction(
        condition=IfCondition(LaunchConfiguration('use_keyboard')),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('robot4ws_teleop_keyboard'),
                        'launch',
                        'teleop.launch.py'
                    ])
                ]),
                launch_arguments={
                    'env': LaunchConfiguration('p310_env')
                }.items()
            )
        ]
    )

    return LaunchDescription(
        args + [
            gazebo_sim,
            joystick_teleop,
            keyboard_teleop
        ]
    )