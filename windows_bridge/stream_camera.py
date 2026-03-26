import cv2
import socket
import pickle
import struct
import sys

# 1. Configura o servidor de rede com proteção de reuso
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Isso evita o erro "Address already in use" ao reiniciar o script
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)
    print("=== Servidor de Câmera Windows Iniciado ===")
    print("Aguardando conexão do ROS no WSL... (Pressione Ctrl+C para sair)")

    cap = cv2.VideoCapture(0) # Abre a câmera nativamente no Windows

    while True:
        # Define um timeout curto para o accept para que ele verifique o Ctrl+C periodicamente
        server_socket.settimeout(1.0)
        try:
            client_socket, addr = server_socket.accept()
            server_socket.settimeout(None) # Remove o timeout para a transmissão
            print(f"Conectado a: {addr}")
        except socket.timeout:
            continue

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Serializa e envia
                data = pickle.dumps(frame)
                message = struct.pack("Q", len(data)) + data
                client_socket.sendall(message)
                
        except (ConnectionResetError, BrokenPipeError, socket.error):
            print("Conexão com o WSL perdida. Aguardando nova conexão...")
        finally:
            client_socket.close()

except KeyboardInterrupt:
    print("\nInterrupção detectada pelo usuário (Ctrl+C).")

finally:
    # 2. LIMPEZA TOTAL (O segredo para não travar)
    print("Limpando recursos...")
    if 'cap' in locals():
        cap.release()
    if 'server_socket' in locals():
        server_socket.close()
    cv2.destroyAllWindows()
    print("Servidor encerrado com sucesso.")
    sys.exit(0)