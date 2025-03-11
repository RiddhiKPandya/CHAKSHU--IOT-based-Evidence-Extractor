import cv2
import os
import face_recognition
import time
import numpy as np
from datetime import datetime

def extract_faces_from_video(video_path, output_dir, sample_rate=30, min_face_size=(50, 50), confidence_threshold=0.6):
    """
    Extracts faces from video frames and saves them to an output directory.
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save extracted faces
        sample_rate (int): Process every Nth frame
        min_face_size (tuple): Minimum face size to detect (width, height)
        confidence_threshold (float): Minimum confidence for face detection
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Open the video file
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    frame_count = 0
    saved_count = 0
    previously_seen_faces = []
    
    print(f"Processing video: {video_path}")
    
    while True:
        # Read the next frame
        success, frame = video.read()
        if not success:
            break
        
        # Process only every Nth frame for efficiency
        if frame_count % sample_rate == 0:
            print(f"Processing frame {frame_count}...")
            
            # Convert BGR to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find all faces in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Check if face meets minimum size requirement
                face_width = right - left
                face_height = bottom - top
                if face_width < min_face_size[0] or face_height < min_face_size[1]:
                    continue
                
                # Check if we've seen this face before (to avoid duplicates)
                is_new_face = True
                if previously_seen_faces:
                    # Compare with previously seen faces
                    matches = face_recognition.compare_faces(previously_seen_faces, face_encoding, tolerance=0.6)
                    if True in matches:
                        # This is a face we've seen before
                        is_new_face = False
                
                if is_new_face:
                    # Save the face encoding for future comparisons
                    previously_seen_faces.append(face_encoding)
                    
                    # Extract the face region
                    face_image = frame[top:bottom, left:right]
                    
                    # Generate a unique filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    face_filename = os.path.join(output_dir, f"face_{timestamp}_{saved_count}.jpg")
                    
                    # Save the face image
                    cv2.imwrite(face_filename, face_image)
                    saved_count += 1
                    
                    print(f"Saved face #{saved_count} to {face_filename}")
        
        frame_count += 1
    
    video.release()
    print(f"Finished processing. Processed {frame_count} frames and saved {saved_count} unique faces.")

def main():
    """
    Main function to run the face extraction script.
    """
    # Configuration
    video_path = "C:\\Users\\ragha\\OneDrive\\Documents\\DEV\\hackathons\\cidecode"  # Change this to your video file path
    output_dir = "extracted_faces"
    sample_rate = 5  # Process every 30th frame for efficiency
    
    extract_faces_from_video(
        video_path=video_path,
        output_dir=output_dir,
        sample_rate=sample_rate,
        min_face_size=(50, 50),
        confidence_threshold=0.6
    )

if __name__ == "__main__":
    main()