from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    return LaunchDescription([
        # 1. Ponte de Câmera (WSL <-> Windows)
        Node(
            package='roomba_wsl_drivers',
            executable='ponte',
            name='camera_bridge',
            # output='screen'
        ),
        
        # 2. Detector de ArUco (Logic)
        Node(
            package='roomba_logic',
            executable='detector',
            name='aruco_detector',
            # output='screen'
        ),

        # 3. Gateway ROS2 Medkit
        Node(
            package='ros2_medkit_gateway',
            executable='gateway_node',
            name='medkit_gateway',
            parameters = [
                {
                    'server.port': 8081,
                    'server.docs': True,
                    'discovery.strategy': 'hybrid',
                }
            ]
            # output='screen'
        ),
        # 3. RViz2 para visualização (Opcional, mas útil)
        # Node(package='rviz2', executable='rviz2', name='rviz2')
    ])
