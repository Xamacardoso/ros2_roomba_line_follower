import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Int32
import math

class MissionControl(Node):
    def __init__(self):
        super().__init__('mission_control')
        
        # --- CONFIGURAÇÃO ---
        self.target_id = 10 
        self.current_station_idx = 1
        self.state = "CALCULATING_PATH" # CALCULATING_PATH, EXECUTING_PATH, WAITING_FOR_READ
        
        self.center_x = 5.5 # A "rua principal" da pista
        self.waypoints = {
            'inicio': (5.5, 1.0),
            1: (2.0, 3.0), 2: (2.0, 5.5), 3: (2.0, 8.0),
            4: (9.0, 8.0), 5: (9.0, 5.5), 6: (9.0, 3.0)
        }

        self.path_queue = [] # Fila de pontos intermediários
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.aruco_sub = self.create_subscription(Int32, '/aruco_id', self.aruco_callback, 10)
        
        self.current_pose = None
        self.last_aruco_id = -1
        self.get_logger().info("Piloto de Linha Ativo!")

    def pose_callback(self, msg):
        self.current_pose = msg
        self.control_loop()

    def aruco_callback(self, msg):
        self.last_aruco_id = msg.data

    def control_loop(self):
        if not self.current_pose: return

        if self.state == "CALCULATING_PATH":
            self.generate_path_to_station(self.current_station_idx)
            self.state = "EXECUTING_PATH"

        elif self.state == "EXECUTING_PATH":
            if not self.path_queue:
                self.state = "WAITING_FOR_READ"
                self.last_aruco_id = -1
                return

            target = self.path_queue[0]
            if self.move_to(target):
                self.path_queue.pop(0) # Remove ponto alcançado
                self.get_logger().info(f"Ponto de linha alcançado. Restantes: {len(self.path_queue)}")

        elif self.state == "WAITING_FOR_READ":
            self.stop_robot()
            if self.last_aruco_id != -1:
                if self.last_aruco_id == self.target_id:
                    self.get_logger().info("ALVO! Voltando para o início pela linha.")
                    self.generate_path_to_home()
                    self.state = "EXECUTING_PATH"
                else:
                    self.current_station_idx = (self.current_station_idx % 6) + 1
                    self.state = "CALCULATING_PATH"

    def generate_path_to_station(self, station_idx):
        """Gera pontos intermediários para seguir a linha até a estação"""
        dest_x, dest_y = self.waypoints[station_idx]
        
        # 1. Ponto de entrada na avenida central (na mesma altura da estação)
        self.path_queue.append((self.center_x, self.current_pose.y))
        # 2. Ponto de cruzamento (onde a estação se ramifica)
        self.path_queue.append((self.center_x, dest_y))
        # 3. Destino final na estação
        self.path_queue.append((dest_x, dest_y))

    def generate_path_to_home(self):
        """Gera caminho de volta passando pelo centro"""
        home_x, home_y = self.waypoints['inicio']
        # 1. Volta para o centro na altura atual
        self.path_queue.append((self.center_x, self.current_pose.y))
        # 2. Desce pelo centro até o início
        self.path_queue.append((home_x, home_y))
        # 3. Estado especial para terminar
        self.target_id = -99 # Impede de re-entrar no loop

    def move_to(self, target):
        dist = math.sqrt((target[0] - self.current_pose.x)**2 + (target[1] - self.current_pose.y)**2)
        angle_to_target = math.atan2(target[1] - self.current_pose.y, target[0] - self.current_pose.x)
        diff_angle = math.atan2(math.sin(angle_to_target - self.current_pose.theta), 
                                math.cos(angle_to_target - self.current_pose.theta))
        
        msg = Twist()
        if dist > 0.12:
            if abs(diff_angle) > 0.05:
                msg.angular.z = 2.0 * diff_angle
            else:
                msg.linear.x = 1.2
            self.cmd_pub.publish(msg)
            return False
        return True

    def stop_robot(self):
        self.cmd_pub.publish(Twist())

def main():
    rclpy.init()
    rclpy.spin(MissionControl())
    rclpy.shutdown()