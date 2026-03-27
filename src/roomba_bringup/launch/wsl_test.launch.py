from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Ponte de Câmera (WSL <-> Windows)
        Node(
            package='roomba_wsl_drivers',
            executable='ponte',
            name='camera_bridge',
            output='screen'
        ),
        
        # 2. Detector de ArUco (Logic)
        Node(
            package='roomba_logic',
            executable='detector',
            name='aruco_detector',
            output='screen'
        ),

        # 3. RViz2 para visualização (Opcional, mas útil)
        # Node(package='rviz2', executable='rviz2', name='rviz2')
    ])
