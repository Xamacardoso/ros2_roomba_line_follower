import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class PiCameraNode(Node):
    def __init__(self):
        super().__init__('pi_camera_node')
        self.publisher_ = self.create_publisher(Image, '/image_raw', 10)
        self.bridge = CvBridge()
        
        # Abre a câmera do Pi (0 para USB ou CSI configurada como V4L2)
        self.cap = cv2.VideoCapture(0)
        
        # Define uma resolução menor para não sobrecarregar o processamento do Pi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Timer para capturar frames (30 FPS aprox.)
        self.timer = self.create_timer(0.033, self.timer_callback)
        self.get_logger().info("Driver de Câmera do Raspberry Pi iniciado!")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # Converte OpenCV -> ROS Image
            msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "camera_link"
            self.publisher_.publish(msg)

    def __del__(self):
        self.cap.release()

def main(args=None):
    rclpy.init(args=args)
    node = PiCameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()