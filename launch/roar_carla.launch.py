# Copyright 2023 michael. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os

import launch
from ament_index_python.packages import get_package_share_directory
import launch_ros
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():

    base_path = os.path.realpath(
        get_package_share_directory("roar_carla_ros2")
    )  # also tried without realpath
    vehicle_config_path = base_path + "/config/berkeley_gokart.json"

    should_launch_manual_control_args = DeclareLaunchArgument(
        "should_launch_manual_control",
        default_value="False",  # default_value=[], has the same problem
        description="True to start manual control, false otherwise",
    )

    ld = launch.LaunchDescription(
        [
            should_launch_manual_control_args,
            launch.actions.DeclareLaunchArgument(
                name="host", default_value="localhost"
            ),
            launch.actions.DeclareLaunchArgument(name="port", default_value="2000"),
            launch.actions.DeclareLaunchArgument(name="timeout", default_value="2"),
            launch.actions.DeclareLaunchArgument(
                name="role_name", default_value="ego_vehicle"
            ),
            launch.actions.DeclareLaunchArgument(
                name="vehicle_filter", default_value="vehicle.*"
            ),
            launch.actions.DeclareLaunchArgument(
                name="spawn_point",
                default_value={
                    "x": 265.0,
                    "y": -65.0,
                    "z": 0.0,
                    "roll": 0.0,
                    "pitch": 0.0,
                    "yaw": 0.0,
                },
            ),
            launch.actions.DeclareLaunchArgument(
                name="spawn_point_ego_vehicle", default_value="spawn_point_hero0"
            ),
            launch.actions.DeclareLaunchArgument(name="town", default_value="Town04"),
            launch.actions.DeclareLaunchArgument(name="passive", default_value="False"),
            launch.actions.DeclareLaunchArgument(
                name="synchronous_mode_wait_for_vehicle_control_command",
                default_value="False",
            ),
            launch.actions.DeclareLaunchArgument(
                name="fixed_delta_seconds", default_value="0.05"
            ),
            launch.actions.DeclareLaunchArgument(
                name="objects_definition_file", default_value=vehicle_config_path
            ),
            launch.actions.DeclareLaunchArgument(
                name="role_name", default_value="ego_vehicle"
            ),
            launch.actions.DeclareLaunchArgument(
                name="spawn_sensors_only", default_value="False"
            ),
            launch.actions.DeclareLaunchArgument(
                name="control_id", default_value="control"
            ),
            launch.actions.IncludeLaunchDescription(
                launch.launch_description_sources.PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("carla_ros_bridge"),
                        "carla_ros_bridge.launch.py",
                    )
                ),
                launch_arguments={
                    "host": launch.substitutions.LaunchConfiguration("host"),
                    "port": launch.substitutions.LaunchConfiguration("port"),
                    "town": launch.substitutions.LaunchConfiguration("town"),
                    "timeout": launch.substitutions.LaunchConfiguration("timeout"),
                    "passive": launch.substitutions.LaunchConfiguration("passive"),
                    "synchronous_mode_wait_for_vehicle_control_command": launch.substitutions.LaunchConfiguration(
                        "synchronous_mode_wait_for_vehicle_control_command"
                    ),
                    "fixed_delta_seconds": launch.substitutions.LaunchConfiguration(
                        "fixed_delta_seconds"
                    ),
                }.items(),
            ),
            launch.actions.IncludeLaunchDescription(
                launch.launch_description_sources.PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("carla_spawn_objects"),
                        "carla_spawn_objects.launch.py",
                    )
                ),
                launch_arguments={
                    "host": launch.substitutions.LaunchConfiguration("host"),
                    "port": launch.substitutions.LaunchConfiguration("port"),
                    "timeout": launch.substitutions.LaunchConfiguration("timeout"),
                    "vehicle_filter": launch.substitutions.LaunchConfiguration(
                        "vehicle_filter"
                    ),
                    "role_name": launch.substitutions.LaunchConfiguration("role_name"),
                    "spawn_point": launch.substitutions.LaunchConfiguration(
                        "spawn_point"
                    ),
                    "spawn_point_ego_vehicle": "specify_ego_vehicle_spawn_in_objects_definition_file",
                    "objects_definition_file": launch.substitutions.LaunchConfiguration(
                        "objects_definition_file"
                    ),
                    "spawn_sensors_only": launch.substitutions.LaunchConfiguration(
                        "spawn_sensors_only"
                    ),
                }.items(),
            ),
            launch.actions.IncludeLaunchDescription(
                launch.launch_description_sources.PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("carla_spawn_objects"),
                        "set_initial_pose.launch.py",
                    )
                ),
                launch_arguments={
                    "role_name": launch.substitutions.LaunchConfiguration("role_name"),
                    "control_id": launch.substitutions.LaunchConfiguration(
                        "control_id"
                    ),
                }.items(),
            ),
            launch.actions.IncludeLaunchDescription(
                launch.launch_description_sources.PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("carla_manual_control"),
                        "carla_manual_control.launch.py",
                    )
                ),
                launch_arguments={
                    "role_name": launch.substitutions.LaunchConfiguration("role_name")
                }.items(),
                condition=IfCondition(
                    LaunchConfiguration("should_launch_manual_control")
                ),  # 3
            ),
        ]
    )
    return ld


if __name__ == "__main__":
    generate_launch_description()
