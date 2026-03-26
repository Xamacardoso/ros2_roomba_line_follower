from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Nó da Ponte (Pega a câmera do Windows)
        Node(
            package='roomba_wsl_drivers', 
            executable='ponte', 
            name='camera_bridge'
        ),
        
        # 2. Nó do Detector de aruco
        Node(
            package='roomba_logic', 
            executable='detector', 
            name='aruco_detector'
        ),
        
        # 3. Nó do Cérebro
        # Node(package='roomba_control', executable='brain', name='robot_brain'),
        
        # 4. ROS2 Medkit (futuramente)
        # Node(package='roomba_control', executable='ros2_medkit', name='ros2_medkit'),
    ])