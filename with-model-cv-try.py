# import Tkinter to create our GUI.
from tkinter import Tk, Label, Button, Frame
# import openCV for receiving the video frames
import cv2
# make imports from the Pillow library for displaying the video stream with Tkinter.
from PIL import Image, ImageTk
# Import the tello module
from djitellopy import tello
# Import threading for our takeoff/land method
import threading
# import our flight commands
from flight_commands import start_flying, stop_flying

import av
import numpy as np


# Class for controlling the drone via keyboard commands
class DroneController:
    def __init__(self):

        # Initialize the Tkinter window, give it a title, and define its minimum size on the screen.
        self.root = Tk()
        self.root.title("Drone Keyboard Controller - Tkinter")
        self.root.minsize(800, 600)

        # Create a hidden frame to handle input from key presses and releases
        self.input_frame = Frame(self.root)

        # Initialize, connect, and turn on the drones video stream
        self.drone = tello.Tello()
        self.drone.connect()
        self.drone.streamon()
        # Initialize a variable to get the video frames from the drone
        self.frame = self.drone.get_frame_read()

        # Define a speed for the drone to fly at
        self.drone.speed = 50

        # Label for displaying video stream
        self.cap_lbl = Label(self.root)
        
        # Load the TensorFlow model for face recognition
        self.face_net = cv2.dnn.readNetFromTensorflow(
            'frozen_inference_graph.pb',
            'face_detection_model.pbtxt'  # Path to configuration file
        )

        # Create a button to send takeoff and land commands to the drone
        self.takeoff_land_button = Button(self.root, text="Takeoff/Land", command=lambda: self.takeoff_land())

        # ----------------------------------------------------------------------------------------------------------------
        """STEP 1: Initialize a flipping attribute and flip buttons as a part of our DroneController class."""
        self.flipping = False
        # Create Buttons bound to our flip commands and make them a child of the input frame.
        self.flip_left_button = Button(self.input_frame, text="Flip Left", command=lambda: self.execute_flip('left'))
        self.flip_right_button = Button(self.input_frame, text="Flip Right", command=lambda: self.execute_flip('right'))
        self.flip_forward_button = Button(self.input_frame, text="Flip Forward", command=lambda: self.execute_flip('forward'))
        self.flip_back_button = Button(self.input_frame, text="Flip Backward", command=lambda: self.execute_flip('back'))
        # ----------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------------------------------
    """STEP 2: Create a method to send flip commands in a separate thread when buttons are pressed. """
    def execute_flip(self, direction):
        try:
            if self.drone.is_flying and self.flipping is False:
                if direction == 'right':
                    print('flipping right')
                    threading.Thread(target=lambda: self.drone.flip_right()).start()
                    self.flipping = True
                elif direction == 'left':
                    print('flipping left')
                    threading.Thread(target=lambda: self.drone.flip_left()).start()
                    self.flipping = True
                elif direction == 'forward':
                    print('flipping forward')
                    threading.Thread(target=lambda: self.drone.flip_forward()).start()
                    self.flipping = True
                elif direction == 'back':
                    print('flipping back')
                    threading.Thread(target=lambda: self.drone.flip_back()).start()
                    self.flipping = True
        except Exception as e:
            print(f"Error in execute flip: {e}")
        finally:
            self.flipping = False
    # ----------------------------------------------------------------------------------------------------------------

    # Define a method for taking off and landing
    def takeoff_land(self):
        # Set the command for taking off or landing by checking the drones is_flying attribute
        if self.drone.is_flying:
            threading.Thread(target=lambda: self.drone.land()).start()
        else:
            threading.Thread(target=lambda: self.drone.takeoff()).start()

    # Method to run the application
    def run_app(self):
        try:
            # Add the button and video stream label to the window
            self.takeoff_land_button.pack(side='bottom', pady=10)
            self.cap_lbl.pack(anchor="center")

            # Bind the key presses with to the flight commands by associating them with a direction to travel.
            self.input_frame.bind('<KeyPress-w>',
                                  lambda event: start_flying(event, 'upward', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-w>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-a>',
                                  lambda event: start_flying(event, 'yaw_left', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-a>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-s>',
                                  lambda event: start_flying(event, 'downward', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-s>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-d>',
                                  lambda event: start_flying(event, 'yaw_right', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-d>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-Up>',
                                  lambda event: start_flying(event, 'forward', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-Up>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-Down>',
                                  lambda event: start_flying(event, 'backward', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-Down>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-Left>',
                                  lambda event: start_flying(event, 'left', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-Left>', lambda event: stop_flying(event, self.drone))

            self.input_frame.bind('<KeyPress-Right>',
                                  lambda event: start_flying(event, 'right', self.drone, self.drone.speed))
            self.input_frame.bind('<KeyRelease-Right>', lambda event: stop_flying(event, self.drone))

            # ----------------------------------------------------------------------------------------------------------------
            """STEP 3: Pack the input frame in a different position and pack the flip buttons to it."""
            # Pack the input frame to the bottom left corner of our gui window.
            self.input_frame.pack(side='left', anchor='sw')
            # Pack the buttons in the button frame in a 'd-pad' style format.
            self.flip_left_button.pack(side='left', padx=5)
            self.flip_right_button.pack(side='right', padx=5)
            self.flip_forward_button.pack(side='top', pady=15)
            self.flip_back_button.pack(side='bottom', pady=15)
            # ----------------------------------------------------------------------------------------------------------------

            # Give direct focus to our input frame.
            self.input_frame.focus_set()

            self.cap_lbl.pack(anchor="center")

            # Call the video stream method
            self.video_stream()

            # Start the tkinter main loop
            self.root.mainloop()

        except Exception as e:
            print(f"Error running the application: {e}")
        finally:
            # When the root window is exited out of ensure to clean up any resources.
            self.cleanup()

    def video_stream(self):
        try:
            # Define the height and width to resize the current frame to
            h = 480
            w = 720

            # Read a frame from the drone
            frame = self.frame.frame

            # Check if the frame is valid
            if frame is None:
                print("No frame received")
                return

            # Resize the frame to fit the display window
            frame_resized = cv2.resize(frame, (w, h))

            # Convert the current frame to the RGB color space (OpenCV uses BGR)
            cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

            # Perform face detection
            faces = self.detect_faces(frame_resized)

            # Draw bounding boxes on detected faces
            for (x, y, x1, y1) in faces:
                cv2.rectangle(cv2image, (x, y), (x1, y1), (0, 255, 0), 2)

            # Convert this to a Pillow Image object
            img = Image.fromarray(cv2image)

            # Convert this then to a Tkinter compatible PhotoImage object
            imgtk = ImageTk.PhotoImage(image=img)

            # Set the image to the label and update it
            self.cap_lbl.imgtk = imgtk  # Keep a reference to avoid garbage collection
            self.cap_lbl.configure(image=imgtk)

            # Schedule the next frame update
            self.cap_lbl.after(10, self.video_stream)

        except Exception as e:
            print(f"Error in video_stream: {e}")

    def detect_faces(self, frame):
        try:
            # Prepare the frame for the model
            blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
            self.face_net.setInput(blob)

            # Perform forward pass to detect faces
            detections = self.face_net.forward()

            # List to store face bounding boxes
            face_boxes = []

            # Loop over all detections
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                # Filter out weak detections by confidence threshold
                if confidence > 0.5:  # You can adjust this threshold
                    box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                    (x, y, x1, y1) = box.astype("int")
                    face_boxes.append((x, y, x1, y1))

            return face_boxes

        except Exception as e:
            print(f"Error in detect_faces: {e}")
            return []


    # Method for cleaning up resources
    def cleanup(self) -> None:
        try:
            # Release any resources
            print("Cleaning up resources...")
            self.drone.end()  # Terminate drone connection
            self.root.quit()  # Quit the Tkinter main loop
            self.root.destroy()  # Destroy the Tkinter root window
            exit()  # Optionally, exit the program
        except Exception as e:
            print(f"Error performing cleanup: {e}")



if __name__ == "__main__":
    # Initialize the GUI
    gui = DroneController()
    # Call the run_app method to run tkinter mainloop
    gui.run_app()