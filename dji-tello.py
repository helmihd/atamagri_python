import cv2
import av
from djitellopy import Tello
from PIL import Image, ImageTk
import tkinter as tk
import threading


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

        # Jalankan decoding dalam thread terpisah
        self.video_thread = threading.Thread(target=self.update_video)
        self.video_thread.daemon = True
        self.video_thread.start()

    def update_video(self):
        for frame in self.container.decode(video=0):
            if not self.running:
                break

            try:
                # Konversi frame ke RGB
                frame_rgb = cv2.cvtColor(frame.to_ndarray(format="bgr24"), cv2.COLOR_BGR2RGB)

                # Konversi ke format Tkinter
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                # Update UI di thread utama
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            except Exception as e:
                print(f"Error while decoding video: {e}")

        self.quit()

    def quit(self):
        self.running = False
        self.tello.streamoff()
        self.tello.end()
        self.container.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TelloApp(root)
    root.mainloop()
