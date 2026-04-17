import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32

class MissionControlPi(Node):
    def __init__(self):
        super().__init__('mission_control_pi')
        
        # 1. Subscrições
        # Ouve o desejo do PID (Seguidor de Linha)
        self.pid_sub = self.create_subscription(Twist, '/cmd_vel_pid', self.pid_callback, 10)
        # Ouve o desejo da Visão (Marcadores ArUco)
        self.aruco_sub = self.create_subscription(Int32, '/aruco_id', self.aruco_callback, 10)
        
        # 2. Publicador Final
        # Este é o tópico que o motor_driver.py do Raspberry Pi escuta
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 3. Estado da Missão
        self.state = "FOLLOW_LINE" 
        self.target_station = 10 # Exemplo: Estação de parada
        self.last_pid_cmd = Twist()
        
        self.get_logger().info("Mission Control Pi iniciado. Modo: Seguindo Linha.")

    def pid_callback(self, msg):
        """Recebe o cálculo do PID constantemente."""
        self.last_pid_cmd = msg
        self.execute_mission_logic()

    def aruco_callback(self, msg):
        """Reage a marcadores visuais."""
        if msg.data == self.target_station:
            if self.state != "AT_STATION":
                self.get_logger().info(f"Marcador {msg.data} detectado! Parando na estação.")
                self.state = "AT_STATION"
                # Aqui você poderia iniciar um timer para voltar a andar após 5 segundos

    def execute_mission_logic(self):
        """Decide qual comando enviar para os motores baseada no estado atual."""
        final_msg = Twist()
        
        if self.state == "FOLLOW_LINE":
            # Repassa o comando do PID diretamente para os motores
            final_msg = self.last_pid_cmd
            
        elif self.state == "AT_STATION":
            # Força parada total ignorando o PID
            final_msg.linear.x = 0.0
            final_msg.angular.z = 0.0
            
        self.cmd_pub.publish(final_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MissionControlPi()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()