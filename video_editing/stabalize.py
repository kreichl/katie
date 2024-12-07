import cv2
import numpy as np
import os
from vidstab import VidStab


# Directory containing input videos
input_directory = r"C:\Users\reich\Documents\RealEstateVideos\20241202-Demo-1"

# Create a subfolder for stabilized videos
output_directory = os.path.join(input_directory, "stabilized")
os.makedirs(output_directory, exist_ok=True)

import cv2
import numpy as np
import os

def stabilize_video(input_path, output_path):

    # Initialize stabilizer
    stabilizer = VidStab()

    # Open video capture
    cap = cv2.VideoCapture(input_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error opening video file")

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Stabilize the frame
        stabilized_frame = stabilizer.stabilize_frame(input_frame=frame)

        # Write the stabilized frame to the output video
        out.write(stabilized_frame)

    # Release video capture and writer
    cap.release()
    out.release()


# Process all videos in the input directory
for file_name in os.listdir(input_directory):
    if file_name.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        input_path = os.path.join(input_directory, file_name)
        output_name = os.path.splitext(file_name)[0] + "_stabilized.mp4"
        output_path = os.path.join(output_directory, output_name)

        print(f"Stabilizing {file_name}...")
        stabilize_video(input_path, output_path)
        print(f"Saved stabilized video as {output_name}")

print(f"All videos have been stabilized and saved in {output_directory}.")