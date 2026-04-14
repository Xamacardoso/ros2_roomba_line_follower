import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen

class TrackDrawer(Node):
    def __init__(self):
        super().__init__('track_drawer')
        self.teleport_cli = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen_cli = self.create_client(SetPen, '/turtle1/set_pen')
        
    def call_service(self, client, request):
        # Envia a requisição de forma assíncrona
        future = client.call_async(request)
        # Gira o nó até que o serviço responda (evita o deadlock)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def set_pen(self, off):
        req = SetPen.Request()
        req.off = off 
        req.width = 4
        req.r, req.g, req.b = (255, 255, 0) # Amarelo vibrante
        self.call_service(self.pen_cli, req)

    def go_to(self, x, y):
        req = TeleportAbsolute.Request()
        req.x, req.y = float(x), float(y)
        self.call_service(self.teleport_cli, req)

    def draw(self):
        self.teleport_cli.wait_for_service()
        self.pen_cli.wait_for_service()
        
        self.get_logger().info("Iniciando desenho da pista...")
        
        # 1. Posicionar no Início (sem riscar)
        self.set_pen(off=1)
        self.go_to(5.5, 1.0)
        
        # 2. Riscar linha central
        self.set_pen(off=0)
        self.go_to(5.5, 8.0)
        
        # 3. Ramificações esquerdas (1, 2, 3)
        for y in [3.0, 5.5, 8.0]:
            self.set_pen(off=1); self.go_to(5.5, y)
            self.set_pen(off=0); self.go_to(2.0, y)
            
        # 4. Ramificações direitas (4, 5, 6)
        for y in [8.0, 5.5, 3.0]:
            self.set_pen(off=1); self.go_to(5.5, y)
            self.set_pen(off=0); self.go_to(9.0, y)

        # --- NOVA INSTRUÇÃO DE REPOSICIONAMENTO ---
        # 5. Voltar para o ponto de início para começar a missão
        self.get_logger().info("Reposicionando Turtle no ponto de INÍCIO...")
        self.set_pen(off=1) # Garante que não vai riscar por cima da pista
        self.go_to(5.5, 1.0) # Coordenada do 'inicio'

        self.get_logger().info("PISTA PRONTA E ROBÔ POSICIONADO!")

def main():
    rclpy.init()
    drawer = TrackDrawer()
    drawer.draw()
    rclpy.shutdown()