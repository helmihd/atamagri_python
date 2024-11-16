from tkinter import Tk, Label, Button, Frame
import cv2
from PIL import Image, ImageTk
from djitellopy import Tello
import threading
import pygame

class DroneController:
    def __init__(self):
        # Initialize the Tkinter window, give it a title, and set the minimum size
        self.root = Tk()
        self.root.title("Drone Keyboard & Joystick Controller - Tkinter")
        self.root.minsize(800, 600)

        # Create a hidden frame to handle input from key presses and releases
        self.input_frame = Frame(self.root)

        # Initialize, connect, and turn on the drone's video stream
        self.drone = Tello()
        self.drone.connect()
        self.drone.streamon()
        self.frame = self.drone.get_frame_read()

        # Define a speed for the drone to fly at
        self.drone.speed = 25

        # Label for displaying the video stream
        self.cap_lbl = Label(self.root)

        # Create a button for takeoff/land commands
        self.takeoff_land_button = Button(self.root, text="Takeoff/Land", command=self.takeoff_land)

        # Initialize joystick
        pygame.init()
        self.joystick = None
        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        # Initialize flip attributes
        self.flipping = False
        self.flip_left_button = Button(self.input_frame, text="Flip Left", command=lambda: self.execute_flip('left'))
        self.flip_right_button = Button(self.input_frame, text="Flip Right", command=lambda: self.execute_flip('right'))
        self.flip_forward_button = Button(self.input_frame, text="Flip Forward", command=lambda: self.execute_flip('forward'))
        self.flip_back_button = Button(self.input_frame, text="Flip Backward", command=lambda: self.execute_flip('back'))

    def execute_flip(self, direction):
        try:
            if self.drone.is_flying and not self.flipping:
                if direction == 'right':
                    threading.Thread(target=self.drone.flip_right).start()
                    self.flipping = True
                elif direction == 'left':
                    threading.Thread(target=self.drone.flip_left).start()
                    self.flipping = True
                elif direction == 'forward':
                    threading.Thread(target=self.drone.flip_forward).start()
                    self.flipping = True
                elif direction == 'back':
                    threading.Thread(target=self.drone.flip_back).start()
                    self.flipping = True
        except Exception as e:
            print(f"Error in execute flip: {e}")
        finally:
            self.flipping = False

    def takeoff_land(self):
        if self.drone.is_flying:
            threading.Thread(target=self.drone.land).start()
        else:
            threading.Thread(target=self.drone.takeoff).start()

    def emergency(self):
        print("Emergency command triggered!")
        try:
            self.drone.emergency()  # Trigger emergency command
        except Exception as e:
            print(f"Error in emergency command: {e}")

    def joystick_control(self):
        try:
            pygame.event.pump()
            if self.joystick:
                up_button = self.joystick.get_button(11)    # Forward button
                down_button = self.joystick.get_button(12)  # Backward button
                left_button = self.joystick.get_button(13)  # Left button
                right_button = self.joystick.get_button(14) # Right button
                up_drone = self.joystick.get_button(9)      # Up button
                down_drone = self.joystick.get_button(10)   # Down button

                if up_drone:
                    threading.Thread(target=self.drone.move_up, args=(self.drone.speed,)).start()
                if down_drone:
                    threading.Thread(target=self.drone.move_down, args=(self.drone.speed,)).start()

                # Movement commands based on button presses
                if up_button:
                    threading.Thread(target=self.drone.move_forward, args=(self.drone.speed,)).start()
                if down_button:
                    threading.Thread(target=self.drone.move_back, args=(self.drone.speed,)).start()

                if left_button:
                    threading.Thread(target=self.drone.move_left, args=(self.drone.speed,)).start()
                if right_button:
                    threading.Thread(target=self.drone.move_right, args=(self.drone.speed,)).start()

                # Joystick buttons for takeoff and landing
                button_a = self.joystick.get_button(0)  # Button A for takeoff
                button_b = self.joystick.get_button(1)  # Button B for landing

                if button_a:  # If button A is pressed, take off
                    threading.Thread(target=self.drone.takeoff).start()
                elif button_b:  # If button B is pressed, land
                    threading.Thread(target=self.drone.land).start()

                emergency_button = self.joystick.get_button(3)
                if emergency_button:
                    threading.Thread(target=self.emergency).start()
                    
        except Exception as e:
            print(f"Error in joystick_control: {e}")

    def run_app(self):
        try:
            self.takeoff_land_button.pack(side='bottom', pady=10)
            self.cap_lbl.pack(anchor="center")

            # Pack the flip buttons to the input frame
            self.input_frame.pack(side='left', anchor='sw')
            self.flip_left_button.pack(side='left', padx=5)
            self.flip_right_button.pack(side='right', padx=5)
            self.flip_forward_button.pack(side='top', pady=15)
            self.flip_back_button.pack(side='bottom', pady=15)

            self.input_frame.focus_set()

            # Start the video stream
            self.video_stream()

            # Start the Tkinter main loop
            self.root.mainloop()

        except Exception as e:
            print(f"Error running the application: {e}")
        finally:
            self.cleanup()

    def video_stream(self):
        try:
            frame = self.frame.frame
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)

            self.cap_lbl.imgtk = imgtk
            self.cap_lbl.configure(image=imgtk)

            self.cap_lbl.after(10, self.video_stream)

            # Update joystick controls every 100ms
            self.joystick_control()

        except Exception as e:
            print(f"Error in video_stream: {e}")

    def cleanup(self):
        try:
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
