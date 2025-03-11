import os
import shutil
import subprocess
import sys
import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()

# Enable CORS so that your React frontend can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your React app URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define directories
UPLOAD_DIR = "uploads"               # For video uploads
IMAGE_FOLDER = "dashcam_analysis"    # Where dash3.py saves images
CSV_UPLOAD_DIR = "csv_uploads"       # Directory to store CSV files

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(CSV_UPLOAD_DIR, exist_ok=True)

# Mount directories for serving static files
app.mount("/dashcam_analysis", StaticFiles(directory=IMAGE_FOLDER), name="dashcam_analysis")

# Use the Python executable from the active virtual environment
VENV_PYTHON = sys.executable

# ------------------------------ VIDEO UPLOAD & PROCESSING ------------------------------

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run dash3.py for video processing
    result = subprocess.run([VENV_PYTHON, "dash3.py", file_path], capture_output=True, text=True)
    
    return JSONResponse(content={
        "status": "Processing complete",
        "video_path": os.path.abspath(file_path),
        "output_folder": os.path.abspath(IMAGE_FOLDER),
        "stdout": result.stdout,
        "stderr": result.stderr
    })

@app.get("/images/")
def list_images():
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return {"images": image_files}

@app.get("/images/{image_name}")
def get_image(image_name: str):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    return JSONResponse(content={"error": "Image not found"}, status_code=404)

# ------------------------------ CSV UPLOAD & PROCESSING ------------------------------

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    """
    Uploads a CSV file, validates it, and returns structured JSON.
    """
    file_path = os.path.join(CSV_UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        df = pd.read_csv(file_path)

        # Ensure required columns exist
        required_columns = {"When", "Where", "Why", "What"}
        if not required_columns.issubset(df.columns):
            return JSONResponse(content={"error": "CSV must contain columns: When, Where, Why, What"}, status_code=400)

        # Convert to JSON
        data = df.to_dict(orient="records")

        return JSONResponse(content={"status": "success", "data": data, "csv_path": os.path.abspath(file_path)})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/csv_files/")
def list_csv_files():
    """
    List all available CSV files.
    """
    csv_files = [f for f in os.listdir(CSV_UPLOAD_DIR) if f.endswith(".csv")]
    return {"csv_files": csv_files}

@app.get("/csv_files/{filename}")
def get_csv_file(filename: str):
    """
    Serve a requested CSV file for download.
    """
    file_path = os.path.join(CSV_UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv", filename=filename)
    return JSONResponse(content={"error": "CSV file not found"}, status_code=404)

# ------------------------------ RUN FASTAPI SERVER ------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
