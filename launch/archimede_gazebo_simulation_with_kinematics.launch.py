#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
import time

def generate_launch_description():
    pkg_sim = FindPackageShare('robot4ws_simulations')
    pkg_kinematics = FindPackageShare('robot4ws_kinematics')

    # Declare arguments
    args = [
        DeclareLaunchArgument('start_gazebo', default_value='true', description='Start Gazebo simulator'),
        DeclareLaunchArgument('include_plugins', default_value='true'),
        DeclareLaunchArgument('include_kinematics', default_value='true'),
        DeclareLaunchArgument('include_terrain_slip_plugin', default_value='false'),
        DeclareLaunchArgument('neural_network_model', default_value='none'),
        DeclareLaunchArgument('include_wheels_terramechanic_model', default_value='false'),
        DeclareLaunchArgument('world_name', default_value='only_walls.sdf'),
        DeclareLaunchArgument('rocker_differential', default_value='false'),
        DeclareLaunchArgument('add_velodyneHDL32E', default_value='false'),
        DeclareLaunchArgument('lidar_organize_cloud', default_value='false'),
        DeclareLaunchArgument('load_sensors_plugins', default_value='true'),
    ]

    # Include basic gazebo launch
    gazebo_basic = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([pkg_sim, 'launch', 'archimede_gazebo_basic.launch.py'])
        ]),
        launch_arguments={
        'start_gazebo': LaunchConfiguration('start_gazebo'),
        'world_name': LaunchConfiguration('world_name'),
        'include_plugins': LaunchConfiguration('include_plugins'),
        'include_terrain_slip_plugin': LaunchConfiguration('include_terrain_slip_plugin'),
        'rocker_differential': LaunchConfiguration('rocker_differential'),
        'add_velodyneHDL32E': LaunchConfiguration('add_velodyneHDL32E'),
        'lidar_organize_cloud': LaunchConfiguration('lidar_organize_cloud'),
        'load_sensors_plugins': LaunchConfiguration('load_sensors_plugins')
        }.items()
    )

    # Include kinematics launch - DELAYED
    kinematics_delayed = TimerAction(
        period=5.0,  # [seconds] Wait for Gazebo to fully initialize
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([pkg_kinematics, 'launch', 'kinematics.launch.py'])
                ]),
            )
        ]
    )

    return LaunchDescription(
        args + [
            gazebo_basic,
            kinematics_delayed  # ← Now launches after delay
        ]
    )