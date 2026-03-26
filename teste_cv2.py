import cv2
import numpy as np

print("OpenCV versão:", cv2.__version__)
img = np.zeros((100,100,3), dtype=np.uint8)
# Tenta apenas converter cores (uma operação que usa a memória do OpenCV)
cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print("Sucesso! O OpenCV está estável.")