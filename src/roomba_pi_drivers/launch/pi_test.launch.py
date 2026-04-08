from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Driver Real do Pi
        Node(
            package='roomba_pi_drivers',
            executable='camera',
            name='pi_camera',
	    parameters=[{'device_index': 0}]
        ),
        # 2. Sua Lógica de ArUco (REUTILIZADA)
        Node(
            package='roomba_logic',
            executable='detector',
            name='aruco_detector'
        )
    ])
