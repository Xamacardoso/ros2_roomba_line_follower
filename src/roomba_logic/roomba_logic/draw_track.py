import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen

class TrackDrawer(Node):
    def __init__(self):
        super().__init__('track_drawer')
        self.teleport_cli = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen_cli = self.create_client(SetPen, '/turtle1/set_pen')

    def call_service(self, client, request):
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def set_pen(self, off):
        req = SetPen.Request()
        req.off = off
        req.width = 4
        req.r, req.g, req.b = (255, 255, 0)
        self.call_service(self.pen_cli, req)

    def go_to(self, x, y):
        req = TeleportAbsolute.Request()
        req.x, req.y = float(x), float(y)
        self.call_service(self.teleport_cli, req)

    def draw(self):
        self.teleport_cli.wait_for_service()
        self.pen_cli.wait_for_service()
        
        # 1. Posicionar no "Inicio/Fim" (Topo)
        self.set_pen(off=1)
        self.go_to(5.5, 10.0)
        
        # 2. Desenhar entrada do circuito
        self.set_pen(off=0)
        self.go_to(5.5, 8.5)
        
        # 3. Desenhar Retângulo Central (Circuito)
        self.go_to(3.5, 8.5) # Topo-Esquerda
        self.go_to(3.5, 2.5) # Baixo-Esquerda
        self.go_to(7.5, 2.5) # Baixo-Direita
        self.go_to(7.5, 8.5) # Topo-Direita
        self.go_to(5.5, 8.5) # Fecha no Topo-Centro
        
        # 4. Desenhar Estações da Esquerda (1, 2, 3) - Viradas para Fora
        for y in [7.0, 5.5, 4.0]:
            self.set_pen(off=1); self.go_to(3.5, y)
            self.set_pen(off=0); self.go_to(1.5, y)
            
        # 5. Desenhar Estações da Direita (4, 5, 6) - Viradas para Fora
        for y in [4.0, 5.5, 7.0]:
            self.set_pen(off=1); self.go_to(7.5, y)
            self.set_pen(off=0); self.go_to(9.5, y)

        # 6. Reposicionar no Início
        self.set_pen(off=1)
        self.go_to(5.5, 10.0)
        self.get_logger().info("Mapa de validação pronto!")

def main():
    rclpy.init()
    TrackDrawer().draw()
    rclpy.shutdown()