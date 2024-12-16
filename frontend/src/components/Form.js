import React, {useEffect, useState, memo} from "react";
import Select from "react-select";

import {Runs} from "components";
import * as CONSTANTS from "Constants";

import "assets/Form.css";
import "assets/Popup.css";
import {Button} from "react-bootstrap";

const Form = ({setDataset, goBack}) => {
  // Filters
  const [datasetTypes, setDatasetTypes] = useState([]);
  const [selectedDatasets, setSelectedDatasets] = useState([]);
  const [uniqueEvents, setUniqueEvents] = useState([]);
  const [selectedUniqueSites, setSelectedUniqueSites] = useState([]);
  const [uniqueSites, setUniqueSites] = useState([]);
  const [selectedUniqueEvents, setSelectedUniqueEvents] = useState([]);

  // Filter Runs
  const [datasetTypeRuns, setDatasetTypeRuns] = useState(null);
  const [eventRuns, setEventRuns] = useState(null);
  const [siteRuns, setSiteRuns] = useState(null);

  // Runs
  const [availableRuns, setAvailableRuns] = useState([]);
  const [shownRuns, setShownRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState([]);
  const [runData, setRunData] = useState([]);
  const [runDataLookup, setRunDataLookup] = useState({});
  const [selectedRunData, setSelectedRunData] = useState([]);

  // Get Dataset Types filter on page load
  useEffect(() => {
    if (datasetTypes.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_DATASET_TYPES_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Available Dataset Types Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({value: value, label: value});
        }
        setDatasetTypes(tempOptionArray);
      });
    }
  }, [datasetTypes]);

  // Get Unique Events filter on page load
  useEffect(() => {
    if (uniqueEvents.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_UNIQUE_EVENTS_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Unique Events for the Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({value: value, label: value});
        }
        setUniqueEvents(tempOptionArray);
      });
    }
  }, [uniqueEvents]);

  // Get Unique Sites filter on page load
  useEffect(() => {
    if (uniqueSites.length === 0) {
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_UNIQUE_SITES_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        // Set Unique Sites Select Dropdown
        let tempOptionArray = [];
        for (const value of Object.values(responseData)) {
          tempOptionArray.push({value: value, label: value});
        }
        setUniqueSites(tempOptionArray);
      });
    }
  }, [uniqueSites]);

  // Function to apply every filter to the available runs to set the shown runs
  useEffect(() => {
    // Add every set together, if null ignore
    let tempShownRuns = availableRuns;
    if (datasetTypeRuns !== null) {
      tempShownRuns = datasetTypeRuns.filter(datasetTypeRun =>
        tempShownRuns.some(tempShownRun => datasetTypeRun.value === tempShownRun.value)
      );
    }
    if (eventRuns !== null) {
      tempShownRuns = eventRuns.filter(eventRun =>
        tempShownRuns.some(tempShownRun => eventRun.value === tempShownRun.value)
      );
    }
    if (siteRuns !== null) {
      tempShownRuns = siteRuns.filter(siteRun =>
        tempShownRuns.some(tempShownRun => siteRun.value === tempShownRun.value)
      );
    }
    setShownRuns(tempShownRuns);
  }, [availableRuns, datasetTypeRuns, eventRuns, siteRuns]);

  // Set datasetTypeRuns when the Grid Spacing filter is changed
  useEffect(() => {
    if (selectedDatasets.length > 0) {
      let tempRunDataLookup = runDataLookup;
      const gridSpacings = selectedDatasets.map((spacing) => spacing.value);
      const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
        if (gridSpacings.includes(tempRunDataLookup[run_name]["type"])) {
          acc.push({
            key: run_name,
            value: run_name,
          });
        }
        return acc;
      }, []);
      setDatasetTypeRuns(tempShownRuns);
    } else {
      setDatasetTypeRuns(null);
    }
  }, [runDataLookup, selectedDatasets]);

  // Set eventRuns when the Run Type filter is changed
  useEffect(() => {
    if (selectedUniqueEvents.length > 0) {
      let tempRunDataLookup = runDataLookup;
      const events = selectedUniqueEvents.map((runType) => runType.value);
      const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
        // Loop over each tectonic type in the run
        for (const event of tempRunDataLookup[run_name]["events"]) {
          if (events.includes(event["name"])) {
            acc.push({
              key: run_name,
              value: run_name,
            });
            break;
          }
        }
        return acc;
      }, []);
      setEventRuns(tempShownRuns);
    } else {
      setEventRuns(null);
    }
  }, [runDataLookup, selectedUniqueEvents]);

  // Set siteRuns when the Sites filter is changed
  useEffect(() => {
    if (selectedUniqueSites.length > 0) {
      let tempRunDataLookup = runDataLookup;
      const sites = selectedUniqueSites.map((site) => site.value);
      const tempShownRuns = Object.keys(tempRunDataLookup).reduce((acc, run_name) => {
        // Loop over each tectonic type in the run
        for (const site of tempRunDataLookup[run_name]["sites"]) {
          if (sites.includes(site["name"])) {
            acc.push({
              key: run_name,
              value: run_name,
            });
            break;
          }
        }
        return acc;
      }, []);
      setSiteRuns(tempShownRuns);
    } else {
      setSiteRuns(null);
    }
  }, [runDataLookup, selectedUniqueSites]);

  // Get Available Runs on page load
  useEffect(() => {
    if (Object.keys(runData).length === 0) {
      // Get the run data for all the runs
      fetch(CONSTANTS.CS_API_URL + CONSTANTS.GET_DATASETS_INFO_ENDPOINT, {
        method: "GET",
      }).then(async (response) => {
        const responseData = await response.json();
        setRunData(responseData);
        setRunDataLookup(responseData);
        // Set Available Runs Array
        let tempOptionArray = Object.keys(responseData).map((key) => ({
          value: key,
          label: key,
        }));
        setAvailableRuns(tempOptionArray);
      });
    }
  }, [runData]);

  // Change the download options when a run is selected
  useEffect(() => {
    if (selectedRun.length > 0) {
      if (Object.keys(runDataLookup).length > 0) {
        // Set the selected run data
        setSelectedRunData(runDataLookup[selectedRun[0]]);
      }
    }
  }, [runDataLookup, selectedRun]);

  const onSelectRun = (e) => {
    if (e[0][0].localeCompare(selectedRun[0])) {
      setSelectedRun(e[0]);
    }
  }

  const selectDataset = () => {
    setDataset(selectedRun, selectedRunData);
  }

  return (
    <div className="border section">
      <div className="sub-section">
        <div className="form-label">Filters</div>
        <div className="row three-column-row">
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Dataset Types"
              isMulti={true}
              options={datasetTypes}
              isDisabled={datasetTypes.length === 0}
              onChange={(e) => setSelectedDatasets(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Events"
              isMulti={true}
              options={uniqueEvents}
              isDisabled={uniqueEvents.length === 0}
              onChange={(e) => setSelectedUniqueEvents(e)}
            ></Select>
          </div>
          <div className="col-4">
            <Select
              className="select-box"
              placeholder="Sites"
              isMulti={true}
              options={uniqueSites}
              isDisabled={uniqueSites.length === 0}
              onChange={(e) => setSelectedUniqueSites(e)}
            ></Select>
          </div>
        </div>
      </div>
      <div className="sub-section">
        <div className="border run-cards-section">
          <Runs
            viewRuns={shownRuns}
            runData={runDataLookup}
            setRun={onSelectRun}
          />
        </div>
        <Button
          variant="primary"
          size="lg"
          disabled={selectedRun.length === 0}
          className="select-dataset-button"
          onClick={selectDataset}
        >
          Select Dataset
        </Button>
      </div>

    </div>
  );
};

export default memo(Form);
