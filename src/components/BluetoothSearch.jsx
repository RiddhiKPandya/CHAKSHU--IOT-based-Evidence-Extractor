import React from "react";

const BluetoothSearch = () => {
  const searchBluetooth = () => {
    alert("Searching for Bluetooth devices...");
  };

  return (
    <div className="card">
      <h3>Search Bluetooth</h3>
      <button onClick={searchBluetooth}>Search</button>
    </div>
  );
};

export default BluetoothSearch;
