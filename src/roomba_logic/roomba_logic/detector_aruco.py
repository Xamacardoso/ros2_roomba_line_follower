import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
import cv2
from cv_bridge import CvBridge

class DetectorAruco(Node):
    def __init__(self):
        super().__init__('detector_aruco')
        
        # 1. Subscreve no topico da ponte de camera
        self.subscription = self.create_subscription(Image, '/image_raw', self.process_image, 10)

        # 2. Publica o id do ArUco para outros usarem
        self.publisher_ = self.create_publisher(Int32, '/aruco_id', 10)

        # 3. Publica a imagem processada para debug
        self.publisher_img = self.create_publisher(Image, '/aruco_image_debug', 10)
        
        self.bridge = CvBridge()
        
        # --- AJUSTE PARA OPENCV 4.6.0 ---
        # Usamos o dicionário diretamente
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        # Usamos o criador de parâmetros específico da versão 4.x
        self.aruco_params = cv2.aruco.DetectorParameters_create()
        
        self.get_logger().info("Detector ArUco 4.6.0 configurado e pronto!")

    def process_image(self, msg):
        try:
            # Converte imagem ROS -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            frame = cv_image.copy()

            cv2.circle(frame, (50, 50), 40, (0, 0, 255), -1)
            cv2.putText(
                frame,
                "MODO DEBUG ATIVO", 
                (100, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, # espessura
                (0, 255, 255), # cor amarela
                2
            )
            
            if frame is None:
                return

            # --- CHAMADA POSICIONAL (Mais segura no 4.6.0) ---
            # A ordem é: (imagem, dicionário, parâmetros)
            corners, ids, rejected = cv2.aruco.detectMarkers(
                frame, 
                self.aruco_dict, 
                parameters=self.aruco_params
            )
            

            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids, (0, 255, 255))
                for i in range(len(ids)):
                    aruco_id = int(ids[i][0])
                    
                    msg_id = Int32()
                    msg_id.data = aruco_id
                    self.publisher_.publish(msg_id)
                    
                    self.get_logger().info(f"ID Detectado: {aruco_id}")
            
            # preparando pro rviz
            # converte de volta para mensagem de imagem do ros
            img_debug_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

            # adiciona timestamp e nome de referencia
            img_debug_msg.header.stamp = self.get_clock().now().to_msg()
            img_debug_msg.header.frame_id = "camera_link"

            self.publisher_img.publish(img_debug_msg)

        except Exception as e:
            self.get_logger().error(f"Erro no processamento: {e}")

def main():
    rclpy.init()
    node = DetectorAruco()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()