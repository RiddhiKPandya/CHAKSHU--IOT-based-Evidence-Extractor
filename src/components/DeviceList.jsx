import React, { useState } from 'react';

const DeviceList = () => {
  const [devices, setDevices] = useState([]);
  const [error, setError] = useState(null);

  const scanForDevices = async () => {
    try {
      setError(null);
      const device = await navigator.bluetooth.requestDevice({
        acceptAllDevices: true,
        optionalServices: ['battery_service'], // You can modify this
      });

      setDevices(prevDevices => [
        ...prevDevices,
        {
          name: device.name || 'Unknown Device',
          type: 'Bluetooth',
          address: device.id, // Unique device ID
        }
      ]);
    } catch (err) {
      setError('Failed to scan for Bluetooth devices. Make sure Bluetooth is enabled.');
    }
  };

  return (
    <div>
      <h2>Bluetooth Devices</h2>
      <button onClick={scanForDevices}>Scan for Devices</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {devices.length === 0 ? (
        <p>No devices found.</p>
      ) : (
        <ul>
          {devices.map((device, index) => (
            <li key={index}>
              <strong>Name:</strong> {device.name} <br />
              <strong>Type:</strong> {device.type} <br />
              <strong>Address:</strong> {device.address}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DeviceList;
