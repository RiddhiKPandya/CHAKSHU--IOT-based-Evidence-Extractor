import React from "react";

const ExcelTable = ({ excelData }) => {
  // Default Dummy Data (used if an empty CSV is uploaded)
  const dummyData = [
    { when: "when", what: "what", why: "why", how: "how" },
    { when: "1", what: "/images?q=tbn:ANd9GcSbJ1NbjtE2rsZQVjEgleauhgZ...", why: "www.google.com", how: "HTTPS" },
    { when: "21-42", what: "/images?q=tbn:ANd9GcQWeKqtGea_1-W-88L1mQ6YLhg...", why: "n1.gstatic.com", how: "HTTS" },
    { when: "21-40", what: "/images?q=tbn:ANd9GcQ75fPLdTYJqwWjXqJVhNuGysaz...", why: "n1.gstatic.com", how: "HTTPS" },
    { when: "21-38", what: "/images?q=tbn:ANd9GcQe01CdDpr-SRtLWiku1MCRawaA...", why: "nts.google.com", how: "HTTP" },
    { when: "24-35", what: "/images?q=tbn:ANd9GcTCQkG3deKzil02DsJJ8d9ikad9...", why: "n1.gstatic.com", how: "HTTPS" },
    { when: "26-35", what: "/images?q=tbn:ANd9GcTCQkG3deKzil02DsJJ8d9ikad9...", why: "n1.gstatic.com", how: "HTTPS" },
    { when: "22-35", what: "/images?q=tbn:ANd9GcTCQkG3deKzil02DsJJ8d9ikad9...", why: "n1.gstatic.com", how: "HTTPS" },
    { when: "22-35", what: "/images?q=tbn:ANd9GcTCQkG3deKzil02DsJJ8d9ikad9...", why: "n1.gstatic.com", how: "HTTPS" },
    { when: "23-35", what: "/images?q=tbn:ANd9GcTCQkG3deKzil02DsJJ8d9ikad9...", why: "n1.gstatic.com", how: "HTTPS" },

  ];

  // Use dummy data if `excelData` is empty
  const tableData = excelData.length > 0 ? excelData : dummyData;

  // Extract headers dynamically
  const headers = Object.keys(tableData[0]);

  return (
    <div className="excel-table-container">
      <h3>Extracted IoT Data</h3>
      <table className="excel-table">
        <thead>
          <tr>
            {headers.map((header, index) => (
              <th key={index}>{header.toUpperCase()}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tableData.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {headers.map((header, colIndex) => (
                <td key={colIndex}>{row[header]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExcelTable;
