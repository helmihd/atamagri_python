import cv2
import av
from djitellopy import Tello
from PIL import Image, ImageTk
import tkinter as tk
import threading
import tensorflow as tf
import numpy as np


class TelloApp:
    def __init__(self, master):
        self.master = master
        self.master.title("DJI Tello Video Feed")

        # Inisialisasi Tello
        self.tello = Tello()
        self.tello.connect()
        print(f"Battery Level: {self.tello.get_battery()}%")
        self.tello.streamon()

        # Dekoder video
        self.container = av.open(self.tello.get_udp_video_address())

        # Label untuk menampilkan video
        self.video_label = tk.Label(master)
        self.video_label.pack()

        # Tombol untuk keluar
        self.quit_button = tk.Button(master, text="Quit", command=self.quit)
        self.quit_button.pack()

        # Flag untuk thread
        self.running = True

        # Load TensorFlow model dan konfigurasi
        self.load_model()

        # Jalankan decoding dalam thread terpisah
        self.video_thread = threading.Thread(target=self.update_video)
        self.video_thread.daemon = True
        self.video_thread.start()

    def load_model(self):
        # Muat model TensorFlow dan konfigurasi pbtxt
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            # Muat frozen_inference_graph.pb
            with tf.io.gfile.GFile("frozen_inference_graph.pb", "rb") as f:
                serialized_graph = f.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name="")
        
            # Muat konfigurasi pbtxt
            config_file = "ssd_mobilenet_v1_coco_2017_11_17.pbtxt"
            with tf.io.gfile.GFile(config_file, "r") as f:
                pbtxt_str = f.read()

        # Buat sesi untuk inferensi
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Tensor input dan output
        self.input_tensor = self.detection_graph.get_tensor_by_name("image_tensor:0")
        self.boxes = self.detection_graph.get_tensor_by_name("detection_boxes:0")
        self.scores = self.detection_graph.get_tensor_by_name("detection_scores:0")
        self.classes = self.detection_graph.get_tensor_by_name("detection_classes:0")
        self.num_detections = self.detection_graph.get_tensor_by_name("num_detections:0")

    def update_video(self):
        for frame in self.container.decode(video=0):
            if not self.running:
                break

            try:
                # Konversi frame ke RGB
                frame_rgb = cv2.cvtColor(frame.to_ndarray(format="bgr24"), cv2.COLOR_BGR2RGB)

                # Terapkan deteksi wajah
                frame_rgb = self.detect_faces(frame_rgb)

                # Konversi ke format Tkinter
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                # Update UI di thread utama
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            except Exception as e:
                print(f"Error while decoding video: {e}")

        self.quit()

    def detect_faces(self, frame):
        # Resize frame untuk model
        resized_frame = cv2.resize(frame, (300, 300))
        input_frame = np.expand_dims(resized_frame, axis=0)

        # Inferensi menggunakan model
        (boxes, scores, classes, num_detections) = self.sess.run(
            [self.boxes, self.scores, self.classes, self.num_detections],
            feed_dict={self.input_tensor: input_frame}
        )

        # Filter berdasarkan skor deteksi
        h, w, _ = frame.shape
        for i in range(int(num_detections[0])):
            if scores[0][i] > 0.5:  # Ambang batas deteksi
                box = boxes[0][i]
                (ymin, xmin, ymax, xmax) = (box[0] * h, box[1] * w, box[2] * h, box[3] * w)
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)

        return frame

    def quit(self):
        self.running = False
        self.tello.streamoff()
        self.tello.end()
        self.container.close()
        self.sess.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TelloApp(root)
    root.mainloop()
