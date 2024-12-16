import React, { useEffect, useState, memo, useRef } from "react";
import Select from "react-select";
import "assets/Download.css";
import "assets/Popup.css";
import { Button } from "react-bootstrap";

const Download = ({ openPopup, selectedRunData, goBack }) => {
  const [downloadAvailable, setDownloadAvailable] = useState(false);
  const [availableDataTypes, setAvailableDataTypes] = useState([]);
  const [selectedDataType, setSelectedDataType] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [downloadLinks, setDownloadLinks] = useState([]);
  const [selectedTotalSize, setSelectedTotalSize] = useState(0);
  const textAreaRef = useRef(null);

  // Initialize Available Data Types Dropdown
  useEffect(() => {
    const tempDataTypes = selectedRunData["data_types"].map((type) => ({
      value: type.id,
      label: type.name,
      files: type.files, // Attach files for easier access later
    }));
    setAvailableDataTypes(tempDataTypes);
  }, [selectedRunData]);

  // Update Available Files Dropdown when Data Type is Selected
  useEffect(() => {
    if (selectedDataType) {
      setAvailableFiles(
        selectedDataType.files.map((file) => ({
          value: file.id,
          label: file.name,
          file_size: file.file_size,
          download_link: file.dropbox_link,
        }))
      );
    } else {
      setAvailableFiles([]);
      setSelectedFiles([]);
    }
  }, [selectedDataType]);

  // Update Total Size and Download Availability
  useEffect(() => {
    if (selectedFiles.length > 0) {
      const totalBytes = selectedFiles.reduce(
        (sum, file) => sum + file.file_size,
        0
      );
      setSelectedTotalSize(totalBytes);
      setDownloadAvailable(true);
    } else {
      setSelectedTotalSize(0);
      setDownloadAvailable(false);
    }
  }, [selectedFiles]);

  const formatBytes = (bytes) => {
    if (bytes === 0) return "0 B";
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const downloadFiles = () => {
    if (selectedFiles.length === 1) {
      const file = selectedFiles[0];
      const link = document.createElement("a");
      link.href = file.download_link;
      link.download = file.label;
      link.click();
      link.remove();
    } else if (selectedFiles.length > 1) {
      const links = selectedFiles.map((file) => file.download_link);
      setDownloadLinks(links);
      openPopup();
    }
  };

  return (
    <div className="border section">
      <div className="sub-section">
        <div className="form-label">Download Data</div>
        <div className="download-selects">
          <Select
            className="download-select-box"
            placeholder="Select Data Type"
            options={availableDataTypes}
            value={selectedDataType}
            onChange={setSelectedDataType}
            isDisabled={availableDataTypes.length === 0}
          />
          <Select
            className="download-select-box"
            placeholder="Select Files"
            options={availableFiles}
            value={selectedFiles}
            onChange={setSelectedFiles}
            isMulti={true}
            isDisabled={availableFiles.length === 0}
          />
        </div>
        <p>Selected total file size: {formatBytes(selectedTotalSize)}</p>
        <Button
          variant="primary"
          size="lg"
          disabled={!downloadAvailable}
          className="download-button"
          onClick={downloadFiles}
        >
          Download
        </Button>
        {downloadLinks.length > 0 && (
          <div>
            <Button
              variant="secondary"
              size="sm"
              className="download-button"
              onClick={openPopup}
            >
              Show Download Instructions
            </Button>
            <textarea
              ref={textAreaRef}
              value={downloadLinks.join("\n")}
              readOnly
              style={{ position: "absolute", left: "-9999px" }}
            />
          </div>
        )}
      </div>
      <div className="nav-section">
        <Button
          variant="secondary"
          size="sm"
          className="back-button"
          onClick={goBack}
        >
          Back
        </Button>
      </div>
    </div>
  );
};

export default memo(Download);
