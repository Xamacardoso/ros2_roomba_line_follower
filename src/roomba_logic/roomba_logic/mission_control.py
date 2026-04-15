import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Int32
import math
import time

class MissionControl(Node):
    def __init__(self):
        super().__init__('mission_control')
        
        # --- CONFIGURAÇÃO DA MISSÃO ---
        self.target_id = 10 
        self.current_station = 1
        self.state = "GENERATE_PATH" 
        self.path_queue = []

        # Coordenadas do Mapa (Conforme imagem image_d0d400.png)
        self.coords = {
            'home': (5.5, 10.0), 'top_c': (5.5, 8.5),
            'tl': (3.5, 8.5), 'bl': (3.5, 2.5),
            'br': (7.5, 2.5), 'tr': (7.5, 8.5),
            1: (1.5, 7.0), 2: (1.5, 5.5), 3: (1.5, 4.0),
            4: (9.5, 4.0), 5: (9.5, 5.5), 6: (9.5, 7.0)
        }

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.aruco_sub = self.create_subscription(Int32, '/aruco_id', self.aruco_callback, 10)
        
        self.current_pose = None
        self.last_aruco_id = -1
        self.get_logger().info("Missão Sequencial 1-6 Iniciada.")

    def pose_callback(self, msg):
        self.current_pose = msg
        self.control_loop()

    def aruco_callback(self, msg):
        # Apenas aceita leitura se estiver no estado de SCANNING
        if self.state == "SCANNING":
            self.last_aruco_id = msg.data

    def generate_path(self, station_idx):
        """Gera trajetórias ortogonais para seguir a linha perfeitamente"""
        dest_x, dest_y = self.coords[station_idx]
        
        # 1. Se estiver saindo do Início
        if self.current_pose.y > 9.0:
            self.path_queue.extend([self.coords['top_c'], self.coords['tl']])

        # 2. Se estiver saindo de uma estação (volta para o trilho)
        if self.current_pose.x < 3.0: self.path_queue.append((3.5, self.current_pose.y))
        elif self.current_pose.x > 8.0: self.path_queue.append((7.5, self.current_pose.y))

        # 3. Travessia Esquerda -> Direita (Estação 3 para 4)
        if station_idx >= 4 and self.current_pose.x < 5.0:
             self.path_queue.extend([self.coords['bl'], self.coords['br']])

        # 4. Alinhamento vertical e entrada na estação
        junction_x = 3.5 if station_idx <= 3 else 7.5
        self.path_queue.append((junction_x, dest_y))
        self.path_queue.append((dest_x, dest_y))

    def control_loop(self):
        if not self.current_pose: return

        if self.state == "GENERATE_PATH":
            self.generate_path(self.current_station)
            self.state = "FOLLOWING_PATH"

        elif self.state == "FOLLOWING_PATH":
            if not self.path_queue:
                self.get_logger().info(f"Cheguei na Estação {self.current_station}. Resetando sensor...")
                self.last_aruco_id = -1 # LIMPA LEITURAS PASSADAS
                self.state = "SCANNING"
                return
            if self.move_to(self.path_queue[0]):
                self.path_queue.pop(0)

        elif self.state == "SCANNING":
            self.stop_robot()
            # Aguarda uma NOVA leitura (last_aruco_id deixará de ser -1)
            if self.last_aruco_id != -1:
                if self.last_aruco_id == self.target_id:
                    self.get_logger().info("ALVO ENCONTRADO! Retornando.")
                    self.state = "RETURN_HOME"
                else:
                    self.get_logger().warn(f"ID {self.last_aruco_id} incorreto na Estação {self.current_station}.")
                    if self.current_station < 6:
                        self.current_station += 1
                        self.state = "GENERATE_PATH"
                    else:
                        self.get_logger().error("Fim da pista. Alvo não encontrado.")
                        self.state = "RETURN_HOME"

        elif self.state == "RETURN_HOME":
            if not self.path_queue:
                # Garante volta pela linha: centro -> topo -> home
                current_side_x = 3.5 if self.current_pose.x < 5.0 else 7.5
                self.path_queue.append((current_side_x, self.current_pose.y))
                if current_side_x == 3.5: self.path_queue.append(self.coords['tl'])
                else: self.path_queue.append(self.coords['tr'])
                self.path_queue.extend([self.coords['top_c'], self.coords['home']])
            
            if self.move_to(self.path_queue[0]):
                self.path_queue.pop(0)
                if not self.path_queue:
                    self.get_logger().info("Missão Concluída.")
                    self.state = "DONE"

    def move_to(self, target):
        dist = math.sqrt((target[0] - self.current_pose.x)**2 + (target[1] - self.current_pose.y)**2)
        angle = math.atan2(target[1] - self.current_pose.y, target[0] - self.current_pose.x)
        diff = math.atan2(math.sin(angle - self.current_pose.theta), math.cos(angle - self.current_pose.theta))
        
        msg = Twist()
        if dist > 0.12:
            if abs(diff) > 0.08:
                msg.angular.z = 2.5 * diff
            else:
                msg.linear.x = 1.0
            self.cmd_pub.publish(msg)
            return False
        return True

    def stop_robot(self):
        self.cmd_pub.publish(Twist())

def main():
    rclpy.init(); rclpy.spin(MissionControl()); rclpy.shutdown()