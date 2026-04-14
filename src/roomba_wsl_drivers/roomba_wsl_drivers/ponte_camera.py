import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
import socket
import pickle
import struct
from cv_bridge import CvBridge

class PonteCamera(Node):
    def __init__(self):
        super().__init__('ponte_camera')
        self.publisher_ = self.create_publisher(Image, '/image_raw', 10)
        self.bridge = CvBridge()
        
        # Conecta no Windows (o IP do host no WSL costuma ser 172.x.x.x ou localhost)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        import subprocess
        cmd = "ip route show | grep default | awk '{print $3}'"
        # windows_ip = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        windows_ip = "127.0.0.1"

        self.get_logger().info(f"Tentando conectar no Windows no IP Localhost: {windows_ip}, na porta 9999")

        try:
            self.client_socket.connect((windows_ip, 9999))
        except Exception as e:
            self.get_logger().error(f"Não foi possível conectar ao Windows: {e}")
            self.get_logger().error("Verifique se o script 'stream_camera.py' está rodando no Windows!")
            return

        self.payload_size = struct.calcsize("Q")
        self.data = b""
        
        self.timer = self.create_timer(0.01, self.receive_frame)
        self.get_logger().info("Conectado à câmera do Windows!")

    def receive_frame(self):
        try:
            while len(self.data) < self.payload_size:
                self.data += self.client_socket.recv(4096)
            
            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            
            while len(self.data) < msg_size:
                self.data += self.client_socket.recv(4096)
            
            frame_data = self.data[:msg_size]
            self.data = self.data[msg_size:]
            frame = pickle.loads(frame_data)
            
            # Publica no ROS
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.publisher_.publish(img_msg)
        except:
            pass

def main():
    rclpy.init()
    rclpy.spin(PonteCamera())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
