import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String

class BrainNode(Node):
    def __init__(self):
        super().__init__('brain_node')
        self.create_subscription(Int32, '/aruco_id', self.decision_callback, 10)
        self.status_pub = self.create_publisher(String, '/robot_status', 10)
        self.get_logger().info("Cérebro operacional. Aguardando comandos visuais...")

    def decision_callback(self, msg):
        status = String()
        if msg.data == 10: # Supondo que ID 10 seja 'Estação de Limpeza'
            status.data = "DOCKING"
        elif msg.data == 20: # Supondo que ID 20 seja 'Obstáculo'
            status.data = "STOP_AND_AVOID"
        else:
            status.data = f"ID_{msg.data}_UNKNOWN"
        
        self.status_pub.publish(status)
        self.get_logger().info(f"Decisão tomada: {status.data}")