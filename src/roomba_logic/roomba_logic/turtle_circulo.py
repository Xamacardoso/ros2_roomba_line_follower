import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist # A mensagem padrão para mover robôs

class CirculoNode(Node):
    def __init__(self):
        super().__init__('no_circulo')
        # Criamos um "Publisher" (Publicador)
        # Ele vai "gritar" no tópico /turtle1/cmd_vel
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Criamos um timer para rodar a função a cada 0.5 segundos
        self.timer = self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 2.0  # Velocidade para frente
        msg.angular.z = 1.0 # Velocidade de giro (faz a curva)
        self.publisher_.publish(msg)
        self.get_logger().info('Publicando comando de movimento...')

def main(args=None):
    rclpy.init(args=args)
    no = CirculoNode()
    rclpy.spin(no) # Mantém o nó vivo
    no.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
