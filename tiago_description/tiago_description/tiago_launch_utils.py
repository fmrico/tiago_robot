# Copyright (c) 2021 PAL Robotics S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch.actions import DeclareLaunchArgument
from pmb2_description.pmb2_launch_utils import get_tiago_base_hw_arguments
from launch_pal.arg_utils import read_launch_argument
from launch_ros.substitutions import FindPackageShare, ExecutableInPackage
from launch.substitutions import Command, PathJoinSubstitution, PythonExpression, LaunchConfiguration
from launch import LaunchContext, Substitution
from typing import List, Text


def get_tiago_hw_arguments(
        arm=False,
        wrist_model=False,
        end_effector=False,
        ft_sensor=False,
        camera_model=False,
        default_arm="no-arm",
        default_wrist_model="wrist-2010",
        default_end_effector="no-end-effector",
        default_ft_sensor="schunk-ft",
        default_camera_model="orbbec-astra",
        **kwargs):
    """
    Return TIAGo Hardware launch arguments.

    Returns a list of the requested hardware LaunchArguments for tiago
    The default value can be configured passing an argument called
    default_NAME_OF_ARGUMENT

    Check get_tiago_base_hw_arguments for more options

    example:
        LaunchDescription([*get_tiago_hw_arguments(
                                wheel_model=True, laser_model=True,
                                default_laser_model='sick-571')])
    """
    args = get_tiago_base_hw_arguments(
        **kwargs)  # RGBD on top of base are impossible if torso is installed
    if arm:
        args.append(
            DeclareLaunchArgument(
                'arm',
                default_value=default_arm,
                description='Which type of arm TIAGo has. ',
                choices=["no-arm", "left-arm", "right-arm"]))
    if wrist_model:
        args.append(
            DeclareLaunchArgument(
                'wrist_model',
                default_value=default_wrist_model,
                description='Wrist model. ',
                choices=["wrist-2010", "wrist-2017"]))
    if end_effector:
        args.append(
            DeclareLaunchArgument(
                'end_effector',
                default_value=default_end_effector,
                description='End effector model.',
                choices=["pal-gripper", "pal-hey5", "schunk-wsg",
                         "custom", "no-end-effector"]))
    if ft_sensor:
        args.append(
            DeclareLaunchArgument(
                'ft_sensor',
                default_value=default_ft_sensor,
                description='FT sensor model. ',
                choices=["schunk-ft", "no-ft-sensor"]))

    if camera_model:
        args.append(
            DeclareLaunchArgument(
                'camera_model',
                default_value=default_camera_model,
                description='Head camera model. ',
                choices=["no-camera", "orbbec-astra", "orbbec-astra-pro", "asus-xtion"]))
    return args


def get_tiago_hw_suffix(
        arm=False,
        wrist_model=False,
        end_effector=False,
        ft_sensor=False,
        camera_model=False,
        **kwargs):
    """
    Generate a substitution that creates a text suffix combining the specified tiago arguments

    The arguments are read as LaunchConfigurations

    For instance, the suffix for: arm=right-arm, wrist_model=wrist-2017, end_effector="pal-gripper"
    would be "right-arm_wrist-2017_pal-gripper"
    """

    suffix_elements = ["'"]
    if arm:
        suffix_elements.append(LaunchConfiguration("arm"))
        suffix_elements.append("_")
    if wrist_model:
        suffix_elements.append(LaunchConfiguration("wrist_model"))
        suffix_elements.append("_")
    if end_effector:
        suffix_elements.append(LaunchConfiguration("end_effector"))
        suffix_elements.append("_")
    if ft_sensor:
        suffix_elements.append(LaunchConfiguration("ft_sensor"))
        suffix_elements.append("_")
    if camera_model:
        suffix_elements.append(LaunchConfiguration("camera_model"))
        suffix_elements.append("_")
    suffix_elements = suffix_elements[:-1]  # remove last _
    suffix_elements.append("'")
    print(suffix_elements)
    return PythonExpression(suffix_elements)


class TiagoXacroConfigSubstitution(Substitution):
    """
    Substitution extracts the tiago hardware args and passes them
    as xacro variables. Used in launch system
    """

    def __init__(self) -> None:
        super().__init__()
        """
        Construct the substitution
        :param: source_file the original YAML file t
        """

    @property
    def name(self) -> List[Substitution]:
        """Getter for name."""
        return "TIAGo Xacro Config"

    def describe(self) -> Text:
        """Return a description of this substitution as a string."""
        return 'Parses tiago hardware launch arguments into xacro \
        arguments potat describe'

    def perform(self, context: LaunchContext) -> Text:
        """
           Generate the robot description and return it as a string
        """

        laser_model = read_launch_argument("laser_model", context)

        arm = read_launch_argument("arm", context)
        end_effector = read_launch_argument("end_effector", context)
        ft_sensor = read_launch_argument("ft_sensor", context)
        camera_model = read_launch_argument("camera_model", context)

        return " laser_model:=" + laser_model + \
            " arm:=" + arm + \
            " end_effector:=" + end_effector + \
            " ft_sensor:=" + ft_sensor + \
            " camera_model:=" + camera_model


def generate_robot_description_action():
    """
       Return a launch Action that reads launch args and generates the robot description

       In order to use this, your launch file must have all launch configurations used in the
       robot description, to do so use the get_tiago_base_hw_arguments with all options to True
    """
    return Command(
        [
            ExecutableInPackage(package='xacro', executable="xacro"),
            ' ',
            PathJoinSubstitution(
                [FindPackageShare('tiago_description'),
                 'robots', 'tiago.urdf.xacro']),
            TiagoXacroConfigSubstitution()
        ])

