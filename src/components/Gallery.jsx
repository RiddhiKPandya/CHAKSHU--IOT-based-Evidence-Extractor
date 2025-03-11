import { useState, useEffect } from "react";
import axios from "axios";

const Gallery = () => {
  const [images, setImages] = useState([]);

  // Function to fetch images
  const fetchImages = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/images/");
      setImages(response.data.images);
    } catch (error) {
      console.error("Error fetching images:", error);
    }
  };

  // Fetch images when the component mounts
  useEffect(() => {
    fetchImages();
  }, []);

  return (
    <div>
      <h2>Processed Images Gallery</h2>
      <div style={{ display: "flex", flexWrap: "wrap" }}>
        {images.map((image, index) => (
          <img
            key={index}
            src={`http://127.0.0.1:8000/dashcam_analysis/${image}?t=${Date.now()}`} 
            alt={`Processed ${index}`}
            style={{ width: "200px", margin: "10px", borderRadius: "5px" }}
          />
        ))}
      </div>
    </div>
  );
};

export default Gallery;
