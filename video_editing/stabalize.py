import cv2
import numpy as np
import os

# Directory containing input videos
input_directory = r"C:\Users\reich\Documents\RealEstateVideos\20241202-Demo-1"

# Create a subfolder for stabilized videos
output_directory = os.path.join(input_directory, "stabilized")
os.makedirs(output_directory, exist_ok=True)

def stabilize_video(input_path, output_path):
    # Load the video
    cap = cv2.VideoCapture(input_path)

    # Get video properties
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Read the first frame
    _, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Transformations store
    transforms = np.zeros((n_frames - 1, 3), np.float32)

    # Loop to compute transformations
    for i in range(n_frames - 1):
        success, curr_frame = cap.read()
        if not success:
            break

        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Detect feature points in previous frame
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)

        # Calculate optical flow
        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)

        # Filter valid points
        idx = np.where(status == 1)[0]
        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]

        # Skip if not enough points
        if len(prev_pts) < 4:
            transforms[i] = transforms[i - 1] if i > 0 else [0, 0, 0]
            continue

        # Estimate transformation matrix
        m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)

        # Extract translation and rotation
        dx = m[0, 2]
        dy = m[1, 2]
        da = np


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