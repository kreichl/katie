import cv2
import numpy as np
import os

# Directory containing input videos
input_directory = r"C:\Users\reich\Documents\RealEstateVideos\20241202-Demo-1"

# Create a subfolder for stabilized videos
output_directory = os.path.join(input_directory, "stabilized")
os.makedirs(output_directory, exist_ok=True)

import cv2
import numpy as np
import os

def stabilize_video(input_path, output_path):
    # Open the video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video {input_path}")
        return

    # Get video properties
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Read the first frame
    success, prev_frame = cap.read()
    if not success:
        print("Error: Unable to read the first frame.")
        cap.release()
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    transforms = np.zeros((n_frames - 1, 3), np.float32)

    # Compute transformations
    for i in range(n_frames - 1):
        success, curr_frame = cap.read()
        if not success:
            print(f"Warning: Skipping frame {i}")
            break

        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)

        # Filter valid points
        idx = np.where(status == 1)[0]
        if len(idx) < 4:
            transforms[i] = transforms[i - 1] if i > 0 else [0, 0, 0]
            continue

        prev_pts = prev_pts[idx]
        curr_pts = curr_pts[idx]

        # Estimate transformation matrix
        m, _ = cv2.estimateAffinePartial2D(prev_pts, curr_pts)
        if m is None:
            transforms[i] = transforms[i - 1] if i > 0 else [0, 0, 0]
            continue

        dx, dy, da = m[0, 2], m[1, 2], np.arctan2(m[1, 0], m[0, 0])
        transforms[i] = [dx, dy, da]
        prev_gray = curr_gray

    # Smooth transformations
    trajectory = np.cumsum(transforms, axis=0)
    smoothed_trajectory = cv2.GaussianBlur(trajectory, (31, 1), 0)
    difference = smoothed_trajectory - trajectory
    transforms_smooth = transforms + difference

    # Reset video to first frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Apply transformations
    for i in range(n_frames - 1):
        success, frame = cap.read()
        if not success:
            print(f"Warning: Missing frame {i}")
            break

        dx, dy, da = transforms_smooth[i]
        m = np.array([[np.cos(da), -np.sin(da), dx],
                      [np.sin(da),  np.cos(da), dy]])
        stabilized_frame = cv2.warpAffine(frame, m, (width, height), borderMode=cv2.BORDER_REFLECT)
        out.write(stabilized_frame)

    # Release resources
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