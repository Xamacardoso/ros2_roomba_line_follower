# Controle Robô com ROS 2 e Visão Computacional

Este projeto faz parte de um TCC focado na navegação autônoma e monitoramento de robôs utilizando **ROS 2 Jazzy Jalisco** em uma arquitetura de **PC de Borda (Edge Computing)**.

## 🚀 Arquitetura do Sistema

O sistema é modular e distribuído:
1.  **Windows Bridge**: Captura o vídeo da webcam nativa e transmite via Sockets TCP/IP.
2.  **ROS 2 Node (Ponte)**: Recebe os frames no Linux (WSL2) e os publica no tópico `/image_raw`.
3.  **Detector ArUco**: Processa as imagens com OpenCV 4.6, detecta marcadores 4x4 e publica os IDs no tópico `/aruco_id`.
4.  **Visualização**: Integração total com **RViz 2** para monitoramento em tempo real.

## 🛠️ Tecnologias Utilizadas

* **ROS 2 Jazzy Jalisco** (Ubuntu 24.04 via WSL2)
* **OpenCV 4.6.0**
* **Python 3.12**
* **ros2_medkit** (futuramente, para API REST)

## 📋 Como Rodar

### 1. No Windows (Host)
Inicie o servidor de transmissão da câmera:
```bash
python windows_bridge/stream_camera.py
```

### 2. No Linux (WSL2 / PC de Borda)
Compile o workspace e inicie o sistema via Launch File:

```bash
colcon build --packages-select roomba_control
source install/setup.bash
ros2 launch roomba_control wsl_roomba.launch.py
```

### 3. Visualização
Para ver a detecção visualmente, em outro terminal do WSL:

```bash
ros2 run rviz2 rviz2
# Adicione o display 'Image' sintonizado no tópico /aruco_image_debug
```