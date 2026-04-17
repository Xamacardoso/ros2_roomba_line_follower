import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
import RPi.GPIO as GPIO

class SensorLinhaNode(Node):
    def __init__(self):
        super().__init__('line_sensor_node')
        
        # Publicador do array de sensores
        self.publisher_ = self.create_publisher(Int32MultiArray, '/line_sensor', 10)
        
        # Pinos BCM: L2, L1, C, R1, R2
        self.canais = [17, 27, 22, 23, 24]
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pino in self.canais:
            GPIO.setup(pino, GPIO.IN)

        # Lê a 20Hz (0.05s) para garantir resposta rápida
        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info("Driver do Sensor TCRT5000 Iniciado!")

    def timer_callback(self):
        msg = Int32MultiArray()
        leituras = []
        
        for pino in self.canais:
            estado = GPIO.input(pino)
            # Vamos assumir 1 para a Linha (Preto/Baixo) e 0 para Fundo (Branco/Alto)
            # Inverta a lógica abaixo se o seu sensor for ativo em ALTO para a linha
            leituras.append(1 if estado == GPIO.LOW else 0)
            
        msg.data = leituras
        self.publisher_.publish(msg)

    def __del__(self):
        GPIO.cleanup()

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(SensorLinhaNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()