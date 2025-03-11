import React from "react";

const Heading = () => {
  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        background: "#222",
        color: "white",
        padding: "10px",
        textAlign: "center",
        fontSize: "1.5em",
        zIndex: 1000, // Ensures it's above other content
        boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.3)", // Adds slight shadow
      }}
    >
      <h1 style={{ margin: 0 }}>CHAKSHU</h1>
    </header>
  );
};

export default Heading;
