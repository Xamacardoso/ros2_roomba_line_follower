import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist

class PIDControllerNode(Node):
    def __init__(self):
        super().__init__('pid_controller')
        
        self.subscription = self.create_subscription(Int32MultiArray, '/line_sensor', self.sensor_callback, 10)
        # Publicamos em um tópico intermediário para a Lógica de Controle decidir se usa
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel_pid', 10)

        # Parâmetros PID (Ajuste fino será necessário no robô real)
        self.declare_parameter('kp', 0.8)
        self.declare_parameter('ki', 0.0)
        self.declare_parameter('kd', 0.2)
        self.declare_parameter('base_speed', 0.15) # m/s

        self.last_error = 0.0
        self.integral = 0.0

        # Pesos geométricos: Esquerda -> Direita
        self.pesos = [-2.0, -1.0, 0.0, 1.0, 2.0]
        self.get_logger().info("Controlador PID Online!")

    def sensor_callback(self, msg):
        sensores = msg.data
        
        # 1. Cálculo do Erro (Média Ponderada)
        soma_pesos = 0.0
        soma_ativos = 0
        
        for i in range(5):
            if sensores[i] == 1: # Se detectou a linha
                soma_pesos += self.pesos[i]
                soma_ativos += 1
                
        if soma_ativos == 0:
            # Perdeu a linha! Mantém o último erro para tentar reencontrar
            erro = self.last_error 
        else:
            erro = soma_pesos / soma_ativos

        # 2. Cálculos do PID
        kp = self.get_parameter('kp').value
        ki = self.get_parameter('ki').value
        kd = self.get_parameter('kd').value
        base_speed = self.get_parameter('base_speed').value

        self.integral += erro
        derivada = erro - self.last_error
        
        correcao_angular = (kp * erro) + (ki * self.integral) + (kd * derivada)
        self.last_error = erro

        # 3. Publicar Comando de Velocidade
        twist = Twist()
        # Se o erro for muito grande (curva brusca), diminui a velocidade linear
        twist.linear.x = base_speed if abs(erro) < 1.5 else base_speed / 2.0
        # Inverte o sinal da correção angular dependendo da orientação física dos motores
        twist.angular.z = -correcao_angular 
        
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(PIDControllerNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()