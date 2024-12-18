import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
import threading
import time
import os
import tempfile
import webbrowser

# Server Configuration (replace these with the real endpoints)
POST_URL = "http://localhost:8080"  # Endpoint for image upload
GET_URL = "http://localhost:8080"  # Endpoint for status check




class ImageClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Upload and Status Checker")

        # Variables
        self.uuid = None
        self.status_label_text = tk.StringVar()
        self.status_label_text.set("Status: Idle")

        self.options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        

        # GUI Layout
        self.upload_button = tk.Button(root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.status_label = tk.Label(root, textvariable=self.status_label_text, font=("Helvetica", 16))
        self.status_label.pack(pady=10)

        self.check_button = tk.Button(root, text="Check Status", command=self.start_status_check)
        self.check_button.pack(pady=10)
        self.check_button.config(state=tk.DISABLED)  # Disabled until image is uploaded

        # Stop flag for threading
        self.stop_polling = False

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image")
        if not file_path:
            return

        # Extract content type from the file extension
        file_extension = os.path.splitext(file_path)[-1][1:]  # Get extension without '.'
        content_type = f"image/{file_extension}"

        try:
            with open(file_path, "rb") as image_file:
                image_data = image_file.read()
                headers = {
                    "Content-Type": content_type,
                    "Content-Length": str(len(image_data))
                }
                response = requests.post(POST_URL, data=image_data, headers=headers)

                if response.status_code == 200:
                    self.uuid = response.text
                    self.status_label_text.set(f"Image uploaded. UUID: {self.uuid}")
                    self.check_button.config(state=tk.NORMAL)
                else:
                    messagebox.showerror("Error", f"Failed to upload image. Status Code: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def start_status_check(self):
        if not self.uuid:
            messagebox.showwarning("Warning", "No UUID found. Please upload an image first.")
            return

        try:
            print(self.uuid)
            response = requests.get(f"{GET_URL}?uuid={self.uuid}")
            if response.status_code == 200:
                # Image processed, download and open it
                self.status_label_text.set("Status: Image Processed ✅")
                self.download_and_open_image()
            elif response.status_code == 201:
                self.status_label_text.set("Status: Processing Image... ⏳")
            else:
                self.status_label_text.set("Status: No Image in Queue or Error ⚠️")
        
        except Exception as e:
            self.status_label_text.set(f"Error: {e}")
        

    def download_and_open_image(self):
        try:
            # Request the image directly (assuming server can send the image)
            response = requests.get(f"{GET_URL}/?uuid={self.uuid}")
            if response.status_code == 200:
                # Save image to a temporary file
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, f"{self.uuid}.png")

                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(response.content)
                self.status_label_text.set("Opening Processed Image...")
                image = Image.open(temp_file_path)
                image.show()
            else:
                messagebox.showerror("Error", f"Failed to download the image. Status Code: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while downloading the image: {e}")

    def on_close(self):
        self.stop_polling = True
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
