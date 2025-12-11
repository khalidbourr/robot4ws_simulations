#!/usr/bin/env python3
"""
Dynamic Archimede Rover Bridges Launch File
Bridges Gazebo sensor data to ROS2 topics with parameterized world name
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_bridge_node(context, *args, **kwargs):
    """Generate bridge node with dynamic world name and model name"""
    world_name = LaunchConfiguration('world_name').perform(context)
    model_name = LaunchConfiguration('model_name').perform(context)

    bridge_arguments = [
        # Clock and TF (no world namespace)
        'clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
        'tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',

        # Odometry (no world namespace)
        'Archimede/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
        'Archimede/odom_with_covariance@nav_msgs/msg/Odometry@gz.msgs.OdometryWithCovariance',

        # Joint states (no world namespace)
        'Archimede/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',

        # Command velocity (no world namespace)
        'Archimede/cmd_vel_motors@actuator_msgs/msg/Actuators@gz.msgs.Actuators',

        # IMU (no world namespace)
        'Archimede/imu@sensor_msgs/msg/Imu@gz.msgs.IMU',

        # Laser scan (no world namespace)
        'Archimede/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',

        # Velodyne point cloud (no world namespace)
        '/Archimede/velodyne/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',

        # RealSense camera with world namespace (without remapping - bridge will use full topic names)
        f'/world/{world_name}/model/{model_name}/link/Archimede_base_link/sensor/rs_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
        f'/world/{world_name}/model/{model_name}/link/Archimede_base_link/sensor/rs_camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
        f'/world/{world_name}/model/{model_name}/link/Archimede_base_link/sensor/rs_camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
        f'/world/{world_name}/model/{model_name}/link/Archimede_base_link/sensor/rs_camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
    ]

    return [
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='archimede_bridge',
            arguments=bridge_arguments,
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'world_name',
            default_value='vibrant_terrain',
            description='Gazebo world name (e.g., vibrant_terrain, empty, default)'
        ),
        DeclareLaunchArgument(
            'model_name',
            default_value='Archimede',
            description='Model instance name in Gazebo'
        ),
        OpaqueFunction(function=generate_bridge_node)
    ])
