import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import struct
import RPi.GPIO as GPIO
import time

class RoombaMotorDriver(Node):
    def __init__(self):
        super().__init__('roomba_motor_driver')
        
        # Pino GPIO para o Device Detect (DD) do Roomba
        self.DD_PIN = 18 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DD_PIN, GPIO.OUT)

        self.declare_parameter('port', '/dev/ttyAMA0')
        self.declare_parameter('baud', 115200)
        
        try:
            self.ser = serial.Serial(self.get_parameter('port').value, 
                                     self.get_parameter('baud').value, 
                                     timeout=0.1)
            # 1. ACORDAR O ROBÔ (Lógica adaptada do C++)
            self.wake_up()
            # 2. INICIAR MODOS
            self.start_safe()
        except Exception as e:
            self.get_logger().error(f"Falha na conexão: {e}")

        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)

    def wake_up(self):
        self.get_logger().info("Acordando o Roomba...")
        # Pulso no pino DD conforme o código C++ dos colegas
        GPIO.output(self.DD_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.DD_PIN, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(self.DD_PIN, GPIO.HIGH)
        time.sleep(2.0)

    def start_safe(self):
        self.get_logger().info("Iniciando Modo Safe...")
        self.ser.write(b'\x80') # Opcode 128 (Start)
        time.sleep(0.1)
        self.ser.write(b'\x83') # Opcode 131 (Safe Mode)
        time.sleep(0.1)

    def cmd_vel_callback(self, msg):
        # Lógica de movimentação Drive Direct (Opcode 145)
        v = int(msg.linear.x * 1000)
        w = int(msg.angular.z * (0.235 / 2.0) * 1000)
        v_right = max(min(v + w, 500), -500)
        v_left = max(min(v - w, 500), -500)
        
        command = struct.pack('>Bhh', 145, v_right, v_left)
        self.ser.write(command)

    def __del__(self):
        GPIO.cleanup()