import React, { useState } from "react";
import * as XLSX from "xlsx"; // Import XLSX for Excel support
import "./Slider.css";
import VideoUpload from "./VideoUpload";
import Gallery from "./Gallery";
import ExcelTable from "./ExcelTable"; // Import Excel Table Component

const Slider = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [excelData, setExcelData] = useState([]);
  const [showTable, setShowTable] = useState(false);
  const [imageUrls, setImageUrls] = useState([]); // State for CCTV images
  const [isProcessing, setIsProcessing] = useState(false); // Processing state

  const handleExcelUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: "array" });

      const sheetName = workbook.SheetNames[0]; // Read the first sheet
      const sheet = workbook.Sheets[sheetName];
      const parsedData = XLSX.utils.sheet_to_json(sheet); // Convert to JSON

      if (parsedData.length === 0) {
        alert("Empty file uploaded! Showing dummy data.");
      }

      setExcelData(parsedData); // Store data
      setShowTable(true);
    };

    reader.readAsArrayBuffer(file);
  };

  const handleCCTVUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsProcessing(true);
    setTimeout(() => {
      setImageUrls(["/face.jpg", "/facetwo.jpg"]); // Dummy image display
      setIsProcessing(false);
    }, 3000); // 3-second delay to simulate processing
  };

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % 3);
  };

  const prevSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex - 1 + 3) % 3);
  };

  return (
    <div className="slider-wrapper">
      <div className="slider-container">
        {/* Slide 1: DashCam Video Upload */}
        <div className={`slide ${currentIndex === 0 ? "active" : ""}`}>
          <h1>Upload Videos for DashCam</h1>
          <VideoUpload />
          <Gallery />
        </div>

        {/* Slide 2: Excel Upload and Table Display */}
        <div className={`slide ${currentIndex === 1 ? "active" : ""}`}>
          <h2>Upload Excel for IoT Data</h2>
          <input type="file" accept=".xlsx" onChange={handleExcelUpload} />
          {showTable && <ExcelTable excelData={excelData} />}
        </div>

        {/* Slide 3: CCTV Video Upload with Dummy Processing */}
        <div className={`slide ${currentIndex === 2 ? "active" : ""}`}>
          <h1>Upload Videos for CCTV</h1>
          <input type="file" accept="video/*" onChange={handleCCTVUpload} />
          <button onClick={handleCCTVUpload} disabled={isProcessing}>
            {isProcessing ? "Processing..." : "Process"}
          </button>
          
          {isProcessing && <p>Processing video...</p>}
          <div className="image-grid">
            {imageUrls.length > 0 && (
              <div style={{ display: "flex", gap: "10px" }}>
                {imageUrls.map((url, index) => (
                  <img
                    key={index}
                    src={url}
                    alt={`Dummy ${index}`}
                    style={{ width: "150px", height: "150px", objectFit: "cover" }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="navigation-buttons">
        <button className="prev-btn" onClick={prevSlide}>❮</button>
        <button className="next-btn" onClick={nextSlide}>❯</button>
      </div>
    </div>
  );
};

export default Slider;
