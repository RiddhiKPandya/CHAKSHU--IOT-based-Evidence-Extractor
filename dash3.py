import cv2
import numpy as np
import os
import time
from datetime import datetime

# Optional: Import pytesseract if available
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not found. License plate text recognition will be disabled.")

def create_output_folders():
    """Create folders to store the output in a fixed folder."""
    base_dir = "dashcam_analysis"  # Fixed folder name
    plates_dir = os.path.join(base_dir, "license_plates")
    
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(plates_dir, exist_ok=True)
    
    return base_dir, plates_dir

def analyze_dashcam_video(video_path, sample_rate=5):
    """
    Analyze dashcam footage to detect license plates.
    
    Args:
        video_path: Path to the video file
        sample_rate: Process every nth frame to improve performance
    """
    # Try to load a license plate cascade classifier
    try:
        plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
        if plate_cascade.empty():
            plate_cascade = None
            print("License plate cascade not found or empty")
    except Exception:
        plate_cascade = None
        print("Using edge detection for potential license plates")
    
    # Create output folders (fixed folder)
    base_dir, plates_dir = create_output_folders()
    
    # Open video file
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return None
        
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    print(f"Video stats: {frame_count} frames, {fps} fps, {duration:.2f} seconds")
    print(f"Processing every {sample_rate} frame")
    
    # Create output log file
    log_file = os.path.join(base_dir, "analysis_log.txt")
    
    plate_count = 0
    frame_number = 0
    
    with open(log_file, 'w') as log:
        log.write(f"Dashcam Analysis Log - {datetime.now()}\n")
        log.write(f"Video: {video_path}\n")
        log.write("=" * 50 + "\n\n")
        
        start_time = time.time()
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            
            frame_number += 1
            if frame_number % sample_rate != 0:
                continue
            
            timestamp = frame_number / fps
            elapsed = time.time() - start_time
            if frame_number % 10 == 0:
                print(f"\rProcessing frame {frame_number}/{frame_count} - {timestamp:.2f}s - Elapsed: {elapsed:.2f}s", end="")
            
            # Create a copy for visualization
            display_frame = frame.copy()
            
            # Resize frame for faster processing (keep display frame original size)
            frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            height, width, _ = frame_small.shape
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
            
            # License plate detection
            if plate_cascade is not None:
                # Use Haar Cascade for license plate detection
                plates = plate_cascade.detectMultiScale(gray, 1.1, 5)
                
                for (x, y, w, h) in plates:
                    # Adjust coordinates for the original frame
                    x_orig, y_orig, w_orig, h_orig = x*2, y*2, w*2, h*2
                    
                    # Extract license plate image from original frame
                    plate_img = frame[y_orig:y_orig+h_orig, x_orig:x_orig+w_orig]
                    if process_license_plate(plate_img, display_frame, x_orig, y_orig, w_orig, h_orig, 
                                               frame_number, timestamp, plates_dir, plate_count, log):
                        plate_count += 1
            else:
                # Fallback method using edge detection to find potential license plates
                edges = cv2.Canny(gray, 100, 200)
                contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area < 1000 or area > 10000:
                        continue
                    
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    if 1.5 <= aspect_ratio <= 5.0:
                        x_orig, y_orig, w_orig, h_orig = x*2, y*2, w*2, h*2
                        plate_img = frame[y_orig:y_orig+h_orig, x_orig:x_orig+w_orig]
                        if process_license_plate(plate_img, display_frame, x_orig, y_orig, w_orig, h_orig, 
                                                   frame_number, timestamp, plates_dir, plate_count, log, 
                                                   is_potential=True):
                            plate_count += 1
            
            # Save the annotated frame every 10th processed frame
            if frame_number % 10 == 0:
                output_frame = os.path.join(base_dir, f"frame_{frame_number}.jpg")
                cv2.imwrite(output_frame, display_frame)
            
        log.write("\n" + "=" * 50 + "\n")
        log.write(f"Analysis completed: {plate_count} license plates detected\n")
    
    video.release()
    print(f"\nAnalysis completed: {plate_count} license plates detected")
    print(f"Results saved to {base_dir}")
    
    return base_dir

def process_license_plate(plate_img, display_frame, x, y, w, h, frame_number, timestamp, 
                          plates_dir, plate_count, log, is_potential=False):
    """Process and save a detected license plate."""
    if plate_img.size == 0:
        return False
    
    valid_plate = False
    plate_text = "Unknown"
    
    if TESSERACT_AVAILABLE:
        try:
            gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_plate, 150, 255, cv2.THRESH_BINARY)
            plate_text = pytesseract.image_to_string(thresh, config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            plate_text = plate_text.strip()
            
            has_letter = any(c.isalpha() for c in plate_text)
            has_number = any(c.isdigit() for c in plate_text)
            
            valid_plate = (len(plate_text) >= 2) and has_letter and has_number
            
            if not valid_plate:
                if not is_potential:
                    log.write(f"License plate candidate filtered - insufficient alphanumeric characters: '{plate_text}' at frame {frame_number}\n")
                return False
            
        except Exception as e:
            plate_text = f"Error: {str(e)}"
            log.write(f"OCR error at frame {frame_number}: {str(e)}\n")
            valid_plate = True
    else:
        gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_plate, 100, 200)
        edge_pixels = cv2.countNonZero(edges)
        plate_area = plate_img.shape[0] * plate_img.shape[1]
        edge_density = edge_pixels / plate_area if plate_area > 0 else 0
        
        valid_plate = edge_density > 0.05
        if not valid_plate:
            if not is_potential:
                log.write(f"License plate candidate filtered - insufficient edge features at frame {frame_number}\n")
            return False
    
    plate_file = os.path.join(plates_dir, f"plate_{plate_count}_{frame_number}.jpg")
    cv2.imwrite(plate_file, plate_img)
    
    color = (0, 0, 255) if is_potential else (255, 0, 0)
    cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
    
    if plate_text != "Unknown":
        cv2.putText(display_frame, plate_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    prefix = "Potential " if is_potential else ""
    log.write(f"{prefix}License plate detected at frame {frame_number} ({timestamp:.2f}s)\n")
    if plate_text != "Unknown":
        log.write(f"  Text: {plate_text}\n")
    log.write(f"  Saved to: {plate_file}\n")
    
    return True 

if __name__ == "__main__":
    video_path = "carplates.mp4"  # Change this to your video file path
    sample_rate = 2  # Change this value if needed
     
    print(f"Starting analysis of video: {video_path}")
    print(f"Processing every {sample_rate} frame")
    
    result_dir = analyze_dashcam_video(video_path, sample_rate)
    
    if result_dir:
        print(f"Analysis complete! Results saved to: {result_dir}")
    else:
        print("Analysis failed. Please check the error messages above.")
