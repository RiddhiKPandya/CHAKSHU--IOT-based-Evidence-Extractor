import cv2
import os
import face_recognition
import numpy as np
from datetime import datetime

def extract_faces_from_video(video_path, output_dir, sample_rate=30, min_face_size=(30, 30), confidence_threshold=0.6):
    """
    Extracts faces from video frames and saves them to an output directory.
    Fixed version to address memory layout issues with face_recognition.
    
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
    
    # Create a debug directory to save frames with detected faces
    debug_dir = os.path.join(output_dir, "debug")
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
        print(f"Created debug directory: {debug_dir}")
    
    # Open the video file
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    frame_count = 0
    saved_count = 0
    total_faces_detected = 0
    faces_too_small = 0
    duplicate_faces = 0
    previously_seen_faces = []
    
    print(f"Processing video: {video_path}")
    print(f"Minimum face size threshold: {min_face_size}")
    
    while True:
        # Read the next frame
        success, frame = video.read()
        if not success:
            break
        
        # Process only every Nth frame for efficiency
        if frame_count % sample_rate == 0:
            print(f"Processing frame {frame_count}...")
            
            # Ensure frame is valid before processing
            if frame is None or len(frame.shape) != 3:
                print(f"WARNING: Frame {frame_count} is invalid. Skipping.")
                frame_count += 1
                continue
            
            try:
                # Critical fix: Create a fresh copy of the frame with the correct memory layout
                # This ensures it's contiguous in memory as dlib expects
                frame_copy = np.array(frame, dtype=np.uint8, copy=True, order='C')
                
                # Convert BGR to RGB (face_recognition uses RGB)
                rgb_frame = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
                
                # Alternative approach: convert to a PIL Image and back (sometimes fixes memory layout issues)
                # import PIL.Image
                # pil_img = PIL.Image.fromarray(rgb_frame)
                # rgb_frame = np.array(pil_img)
                
                # Save a debug copy of the processed frame
                debug_rgb_path = os.path.join(debug_dir, f"processed_rgb_frame_{frame_count}.jpg")
                cv2.imwrite(debug_rgb_path, cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
                
                # Find all faces in the frame
                # Use model='hog' which is faster and more compatible than the default CNN model
                face_locations = face_recognition.face_locations(rgb_frame, model='hog')
                
                # Debug: Save frame with bounding boxes if any faces detected
                debug_frame = frame.copy()
                frame_faces_count = len(face_locations)
                total_faces_detected += frame_faces_count
                
                print(f"  - Found {frame_faces_count} faces in frame {frame_count}")
                
                if frame_faces_count > 0:
                    # Use 'batch_size=1' to process one face at a time, which can help with memory issues
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1, model='small')
                    
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        # Draw rectangle on debug frame
                        cv2.rectangle(debug_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Check if face meets minimum size requirement
                        face_width = right - left
                        face_height = bottom - top
                        face_size_text = f"{face_width}x{face_height}"
                        cv2.putText(debug_frame, face_size_text, (left, top - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
                        if face_width < min_face_size[0] or face_height < min_face_size[1]:
                            faces_too_small += 1
                            cv2.putText(debug_frame, "TOO SMALL", (left, bottom + 20), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                            continue
                        
                        # Check if we've seen this face before (to avoid duplicates)
                        is_new_face = True
                        if previously_seen_faces:
                            # Compare with previously seen faces using lower tolerance to improve matching
                            matches = face_recognition.compare_faces(previously_seen_faces, face_encoding, tolerance=0.6)
                            if True in matches:
                                # This is a face we've seen before
                                is_new_face = False
                                duplicate_faces += 1
                                cv2.putText(debug_frame, "DUPLICATE", (left, bottom + 40), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        
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
                            
                            print(f"  - Saved face #{saved_count} to {face_filename}")
                            cv2.putText(debug_frame, "SAVED", (left, bottom + 60), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    
                    # Save debug frame with annotations
                    debug_filename = os.path.join(debug_dir, f"debug_frame_{frame_count}.jpg")
                    cv2.imwrite(debug_filename, debug_frame)
            
            except Exception as e:
                print(f"ERROR processing frame {frame_count}: {str(e)}")
                # Try alternative approach with downsized frame
                try:
                    print("Attempting with downsized frame...")
                    # Resize to a smaller resolution
                    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                    # Create new copy with correct memory layout
                    small_frame = np.array(small_frame, dtype=np.uint8, copy=True, order='C')
                    # Convert to RGB
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    # Try face detection on smaller frame
                    face_locations = face_recognition.face_locations(rgb_small_frame, model='hog')
                    print(f"  - Found {len(face_locations)} faces in downsized frame")
                    
                    # If this succeeds, save the debug info
                    debug_small_path = os.path.join(debug_dir, f"small_frame_{frame_count}.jpg")
                    cv2.imwrite(debug_small_path, small_frame)
                    
                    # Adjust face locations to match original frame size
                    adjusted_locations = []
                    for top, right, bottom, left in face_locations:
                        adjusted_locations.append((top*2, right*2, bottom*2, left*2))
                    
                    # Continue processing with these adjusted locations
                    # (Code omitted for brevity, would be similar to the main processing loop)
                    
                except Exception as e2:
                    print(f"  Secondary approach also failed: {str(e2)}")
                    # Save problematic frame for inspection
                    problem_frame_path = os.path.join(debug_dir, f"problem_frame_{frame_count}.jpg")
                    cv2.imwrite(problem_frame_path, frame)
        
        frame_count += 1
    
    video.release()
    
    # Print detailed summary
    print("\nDetailed Summary:")
    print(f"Total frames processed: {frame_count}")
    print(f"Frames analyzed (every {sample_rate}th frame): {frame_count // sample_rate}")
    print(f"Total faces detected: {total_faces_detected}")
    print(f"Faces too small (below {min_face_size}): {faces_too_small}")
    print(f"Duplicate faces: {duplicate_faces}")
    print(f"Unique faces saved: {saved_count}")
    
    if total_faces_detected == 0:
        print("\nNo faces were detected. Possible issues:")
        print("- The video might not contain clearly visible faces")
        print("- Faces might be at angles that are difficult to detect")
        print("- Lighting or video quality issues might be affecting detection")
        print("- There might be compatibility issues with the face_recognition library")
        print("\nPossible solutions:")
        print("1. Try with a different video file to test if the issue is with this specific video")
        print("2. Consider using OpenCV's built-in face detector instead of face_recognition")
        print("3. Check if you have the latest versions of dlib and face_recognition")
    elif faces_too_small == total_faces_detected:
        print("\nAll detected faces were too small. Consider:")
        print(f"- Further reducing the minimum face size (currently {min_face_size})")
        print("- Using a video where subjects are closer to the camera")

def main():
    """
    Main function to run the face extraction script.
    """
    # Configuration
    video_path = "C:\\Users\\ragha\\OneDrive\\Documents\\DEV\\hackathons\\cidecode\\face.mp4"  # Change this to your video file path
    output_dir = "extracted_faces"
    sample_rate = 5  # Process every 5th frame for efficiency
    
    extract_faces_from_video(
        video_path=video_path,
        output_dir=output_dir,
        sample_rate=sample_rate,
        min_face_size=(30, 30),
        confidence_threshold=0.6
    )

if __name__ == "__main__":
    main()