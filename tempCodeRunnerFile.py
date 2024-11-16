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