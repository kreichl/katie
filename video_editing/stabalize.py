import cv2
import numpy as np
import os
from vidstab import VidStab

# Directory containing input videos
input_directory = r"C:\Users\reich\Documents\RealEstateVideos\20241202-Demo-1"

# Create a subfolder for stabilized videos
output_directory = os.path.join(input_directory, "stabilized")
os.makedirs(output_directory, exist_ok=True)

def estimate_trajectory(prev_frame, curr_frame):
    """
    Estimate motion between two frames using feature tracking.
    
    Args:
        prev_frame (numpy.ndarray): Previous frame
        curr_frame (numpy.ndarray): Current frame
    
    Returns:
        numpy.ndarray: Transformation matrix
    """
    # Convert frames to grayscale
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    
    # Detect features
    features_prev = cv2.goodFeaturesToTrack(
        prev_gray, 
        maxCorners=200, 
        qualityLevel=0.01, 
        minDistance=30, 
        blockSize=3
    )
    
    # Track features
    features_curr, status, err = cv2.calcOpticalFlowPyrLK(
        prev_gray, curr_gray, features_prev, None
    )
    
    # Filter good matches
    idx = np.where(status == 1)[0]
    features_prev = features_prev[idx]
    features_curr = features_curr[idx]
    
    # Find transformation matrix
    transformation = cv2.estimateAffinePartial2D(features_prev, features_curr)[0]
    return transformation

def smooth_trajectory(trajectories):
    """
    Smooth camera motion trajectories.
    
    Args:
        trajectories (list): List of transformation matrices
    
    Returns:
        list: Smoothed transformation matrices
    """
    # Simple moving average smoothing
    smooth_trajectories = []
    window_size = 5
    
    for i in range(len(trajectories)):
        start = max(0, i - window_size // 2)
        end = min(len(trajectories), i + window_size // 2 + 1)
        
        # Calculate average transformation
        avg_transformation = np.mean(trajectories[start:end], axis=0)
        smooth_trajectories.append(avg_transformation)
    
    return smooth_trajectories

def stabilize_video(input_path, output_path):
    """
    Stabilize video by smoothing camera motion.
    
    Args:
        input_path (str): Path to input video
        output_path (str): Path to output stabilized video
    """
    # Open video
    cap = cv2.VideoCapture(input_path)
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Read first frame
    ret, prev_frame = cap.read()
    if not ret:
        print("Could not read video")
        return
    
    # Store transformation matrices
    trajectories = []
    
    # Process video
    while True:
        ret, curr_frame = cap.read()
        if not ret:
            break
        
        # Estimate motion
        transformation = estimate_trajectory(prev_frame, curr_frame)
        trajectories.append(transformation)
        
        prev_frame = curr_frame
    
    # Reset video capture
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Smooth trajectories
    smooth_trajs = smooth_trajectory(trajectories)
    
    # Stabilize video
    for i, transformation in enumerate(smooth_trajs):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply smoothed transformation
        stabilized_frame = cv2.warpAffine(
            frame, 
            transformation, 
            (width, height), 
            flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP
        )
        
        out.write(stabilized_frame)
        
        # Optional: show progress
        print(f"Processed frame {i+1}/{total_frames}")
    
    # Release resources
    cap.release()
    out.release()
    
    print(f"Stabilized video saved to {output_path}")


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