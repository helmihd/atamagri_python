import cv2
from ultralytics import YOLO

# Load model YOLOv8
model = YOLO('best.pt')  # Ganti dengan path ke model YOLOv8 Anda

# Load gambar untuk pengujian
image_path = 'babi.jpg'  # Ganti dengan path gambar Anda
img = cv2.imread(image_path)

# Deteksi objek dengan YOLO
results = model(img)

# Ambil hasil deteksi (bounding boxes)
for result in results:  # 'results' adalah list, jadi kita iterasi
    boxes = result.boxes  # Bounding boxes
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # Ambil koordinat bounding box
        conf = box.conf[0]  # Confidence score
        cls = int(box.cls[0])  # Kelas objek

        # Gambar kotak di sekitar objek yang terdeteksi
        if conf > 0.5:  # Jika confidence > 0.5
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Gambar kotak hijau
            cv2.putText(img, f'{model.names[cls]} {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Tampilkan gambar dengan OpenCV
cv2.imshow('Detection Result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
