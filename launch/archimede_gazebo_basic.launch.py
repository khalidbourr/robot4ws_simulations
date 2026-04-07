#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, ExecuteProcess, SetEnvironmentVariable, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = FindPackageShare('robot4ws_description')
    pkg_sim = FindPackageShare('robot4ws_simulations')
    pkg_plugins = FindPackageShare('robot4ws_gazebo_plugins')

    # Get package directory
    pkg_share_dir = get_package_share_directory('robot4ws_description')

    # Set Gazebo environment variables
    gz_resource_path = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        [EnvironmentVariable('GZ_SIM_RESOURCE_PATH', default_value=''),
         os.pathsep,
         PathJoinSubstitution([pkg_share, '..'])]
    )

    gz_plugin_path = SetEnvironmentVariable(
        'GZ_SIM_SYSTEM_PLUGIN_PATH',
        [EnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', default_value=''),
         os.pathsep,
         PathJoinSubstitution([pkg_plugins, '..', '..', 'lib'])]
    )

    # Declare arguments
    args = [
        DeclareLaunchArgument('model', default_value=PathJoinSubstitution([pkg_share, 'urdf', 'rover.urdf.xacro'])),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='false'),
        DeclareLaunchArgument('include_plugins', default_value='true'),
        DeclareLaunchArgument('start_gazebo', default_value='true', description='Start Gazebo simulator'),
        DeclareLaunchArgument('world_name', default_value='empty', description='Gazebo world name'),
        DeclareLaunchArgument('pos_x', default_value='-20.0'),
        DeclareLaunchArgument('pos_y', default_value='15.0'),
        DeclareLaunchArgument('pos_z', default_value='1.5'),
        DeclareLaunchArgument('pos_roll', default_value='-0.07'),
        DeclareLaunchArgument('pos_pitch', default_value='-0.09'),
        DeclareLaunchArgument('pos_yaw', default_value='2.74'),
        DeclareLaunchArgument('show_imu', default_value='false'),
        DeclareLaunchArgument('show_cameras', default_value='false'),
        DeclareLaunchArgument('show_laser_scan', default_value='false'),
        DeclareLaunchArgument('show_realsense', default_value='false'),
        DeclareLaunchArgument('rocker_differential', default_value='false'),
        DeclareLaunchArgument('include_terrain_slip_plugin', default_value='false'),
        DeclareLaunchArgument('add_velodyneHDL32E', default_value='false'),
        DeclareLaunchArgument('lidar_organize_cloud', default_value='false'),
        DeclareLaunchArgument('load_sensors_plugins', default_value='true'),

    ]


    # Robot description
    robot_description_content = ParameterValue(
        Command([
            'xacro ', LaunchConfiguration('model'),
            ' include_plugins:=', LaunchConfiguration('include_plugins'),
            ' show_cameras:=', LaunchConfiguration('show_cameras'),
            ' show_laser_scan:=', LaunchConfiguration('show_laser_scan'),
            ' visualize_imu:=', LaunchConfiguration('show_imu'),
            ' visualize_realsense:=', LaunchConfiguration('show_realsense'),
            ' rocker_differential:=', LaunchConfiguration('rocker_differential'),
            ' include_terrain_slip_plugin:=', LaunchConfiguration('include_terrain_slip_plugin'),
            ' add_velodyneHDL32E:=', LaunchConfiguration('add_velodyneHDL32E'),
            ' lidar_organize_cloud:=', LaunchConfiguration('lidar_organize_cloud'),
            ' load_sensors_plugins:=', LaunchConfiguration('load_sensors_plugins')
        ]),
        value_type=str
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }],
        output='screen'
    )

    # Gazebo - empty world (conditional)
    gz_sim = GroupAction(
        condition=IfCondition(LaunchConfiguration('start_gazebo')),
        actions=[
            ExecuteProcess(
                cmd=['gz', 'sim', 'empty.sdf', '-r'],
                output='screen'
            )
        ]
    )

    # Spawn entity
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'Archimede',
            '-topic', 'robot_description',
            '-x', LaunchConfiguration('pos_x'),
            '-y', LaunchConfiguration('pos_y'),
            '-z', LaunchConfiguration('pos_z'),
            '-R', LaunchConfiguration('pos_roll'),
            '-P', LaunchConfiguration('pos_pitch'),
            '-Y', LaunchConfiguration('pos_yaw')
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # Static TF
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0.158679999951',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'Archimede_footprint',
            '--child-frame-id', 'Archimede_base_link'
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # RViz
    rviz = GroupAction(
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        gz_resource_path,
        gz_plugin_path,
    ] + args + [
        robot_state_publisher,
        gz_sim,
        spawn_entity,
        static_tf,
        rviz
    ])