import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import struct

class RoombaMotorDriver(Node):
    def __init__(self):
        super().__init__('roomba_motor_driver')
        
        # --- CONFIGURAÇÃO DE HARDWARE ---
        # No Raspberry Pi 4, os pinos GPIO 14/15 costumam ser /dev/ttyS0 ou /dev/ttyAMA0
        self.declare_parameter('port', '/dev/ttyS0') 
        self.declare_parameter('baud', 115200) # Baud rate padrão do Roomba 600
        
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            self.get_logger().info(f"Conectado ao Roomba via GPIO UART em {port}")
            self.init_roomba()
        except Exception as e:
            self.get_logger().error(f"Erro ao abrir porta serial nos pinos GPIO: {e}")
            self.get_logger().error("DICA: Verifique se a porta serial está habilitada no raspi-config!")

        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.wheel_base = 0.235 # Metros

    def init_roomba(self):
        # Inicia a Open Interface (OI) do iRobot
        self.ser.write(b'\x80') # Opcode START
        self.ser.write(b'\x83') # Opcode SAFE MODE
        self.get_logger().info("iRobot inicializado em SAFE MODE")

    def cmd_vel_callback(self, msg):
        # Conversão de Cinemática Diferencial
        v = msg.linear.x * 1000  # m/s para mm/s
        w = msg.angular.z * (self.wheel_base / 2.0) * 1000
        
        v_right = int(v + w)
        v_left = int(v - w)
        
        # Limites físicos do motor (mm/s)
        v_right = max(min(v_right, 500), -500)
        v_left = max(min(v_left, 500), -500)
        
        # Drive Direct (Opcode 145) [145, VelRight_H, VelRight_L, VelLeft_H, VelLeft_L]
        command = struct.pack('>Bhh', 145, v_right, v_left)
        self.ser.write(command)

    def __del__(self):
        if hasattr(self, 'ser'):
            self.ser.write(b'\xad') # Opcode STOP
            self.ser.close()

def main(args=None):
    rclpy.init(args=args)
    node = RoombaMotorDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()