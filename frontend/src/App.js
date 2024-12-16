import React, {useState} from "react";

import {Form, InstallCard, Map, Download, AddRun} from "components";

import "assets/App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import {Button} from "react-bootstrap";

function App() {

  const [showDownloadPopup, setShowDownloadPopup] = useState(false);
  const [selectedRunData, setSelectedRunData] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [showDownloadPage, setShowDownloadPage] = useState(false);
  const [addRunButtonText, setAddRunButtonText] = useState("Add Run");

  const onCloseDownloadPopup = () => {
    setShowDownloadPopup(false);
  };

  const handleShowDownloadPopup = () => {
    setShowDownloadPopup(true);
  };

  const setDataset = (selectedRun, selectedRunData) => {
    setSelectedRunData(selectedRunData);
    setShowDownloadPage(true);
  }

  const setShowAddForm = () => {
    if (showAdd) {
      setAddRunButtonText("Add Run");
      setShowAdd(false);
    } else {
      setAddRunButtonText("Back");
      setShowAdd(true);
    }
  }

  const returnToDatasets = () => {
    setShowDownloadPage(false);
    setSelectedRunData([]);
  }

  return (
    <div>
      <div className="App d-flex flex-column h-100">
        <div className="row two-column-row">
          <div className="col-7 left-side-title">
            <div className="title">NZEQ Datasets</div>
          </div>
          <div className="col-5 right-side-title">
            <Button
              variant="secondary"
              className="add-run-button"
              onClick={setShowAddForm}
            >
              {addRunButtonText}
            </Button>
          </div>
        </div>
        {showAdd && <AddRun/>}
        {!showAdd &&
          <div className="row two-column-row">
            <div className="col-7 h-100">
              {!showDownloadPage && <Form setDataset={setDataset}/>}
              {showDownloadPage &&
                <Download openPopup={handleShowDownloadPopup} selectedRunData={selectedRunData}
                          goBack={returnToDatasets}/>}
            </div>
            <div className="col-5 h-100">
              <Map/>
            </div>
          </div>
        }
        {showDownloadPopup && <div className="popup-overlay">
          <div className="popup-content">
            <InstallCard onClose={onCloseDownloadPopup}/>
          </div>
        </div>}
      </div>
    </div>
  );
}

export default App;
