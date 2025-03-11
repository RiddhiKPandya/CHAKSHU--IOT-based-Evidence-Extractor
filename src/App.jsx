import React, { useState } from 'react';
//import axios from 'axios';
import Heading from './components/header';
import Slider from './components/Slider'; // Import Slider component

const App = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDevices = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:5000/api/devices');
      setDevices(response.data.devices);
    } catch (err) {
      setError('Failed to fetch devices.');
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <Heading />
      <div className="main-content">
          {/*
        <button onClick={fetchDevices} disabled={loading}>
        
          {loading ? 'Scanning...' : 'Scan for Devices'}
        </button>
        {error && <p className="error">{error}</p>}
        <DeviceList devices={devices} />
         */ }
        {/* Add Slider Component Here */}
        <Slider />
      </div>
    </div>
  );
};

export default App;
