from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Hardware: Driver do Motor (Comunicação Serial)
        Node(
            package='roomba_pi_drivers',
            executable='motor',
            name='roomba_motor_driver',
            parameters=[{
                'port': '/dev/ttyAMA0', 
                'baud': 115200
            }],
            output='screen' # Permite ver os logs de "Acordando Roomba" no terminal
        ),
        
        # 2. Hardware: Driver do Sensor de Linha (TCRT5000)
        Node(
            package='roomba_pi_drivers',
            executable='line_sensor',
            name='sensor_linha_node',
            output='screen'
        ),

        # 3. Lógica: Controlador PID
        Node(
            package='roomba_logic',
            executable='pid',
            name='pid_controller',
            parameters=[{
                'kp': 0.8, 
                'ki': 0.0, 
                'kd': 0.2, 
                'base_speed': 0.15
            }],
            output='screen'
        ),

        # 4. Lógica: Controle de Missão (Mux)
        Node(
            package='roomba_logic',
            executable='mission_control_pi',
            name='mission_control_pi',
            output='screen'
        ),
        
        # ---------------------------------------------------------
        # OPCIONAL: Descomente abaixo se a Câmera e o ArUco 
        # forem rodar fisicamente no Raspberry Pi junto com a linha
        # ---------------------------------------------------------
        # Node(
        #     package='roomba_pi_drivers', 
        #     executable='camera', 
        #     name='pi_camera'
        # ),
        # Node(
        #     package='roomba_logic', 
        #     executable='detector', 
        #     name='aruco_detector'
        # ),
    ])