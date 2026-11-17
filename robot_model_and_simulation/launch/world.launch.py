import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution

def generate_launch_description():

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='simple_world.sdf',
        description='Name of the Gazebo world file to load'
    )

    pkg_dir = get_package_share_directory('assign2')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Gazebo resource paths
    gazebo_models_path = os.path.expanduser('~/gazebo_models')

    aruco_models_path = os.path.join(
    pkg_dir,
    'aruco_boxes_models'
    )

    current_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')

    resource_paths = [
    aruco_models_path,
    gazebo_models_path
    ]

    os.environ['GZ_SIM_RESOURCE_PATH'] = os.pathsep.join(
    resource_paths + ([current_path] if current_path else [])
    )


    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_ros_gz_sim,
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': [
                PathJoinSubstitution([
                    pkg_dir,
                    'worlds',
                    LaunchConfiguration('world')
                ]),
                TextSubstitution(text=' -r -v -v1')
            ],
            'on_exit_shutdown': 'true'
        }.items()
    )

    return LaunchDescription([
        world_arg,
        gazebo_launch
    ])
