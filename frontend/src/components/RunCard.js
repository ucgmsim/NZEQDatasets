import React, { memo } from "react";
import { Card } from "react-bootstrap";


import "assets/RunCard.css";

const RunCard = ({ key_x, runData, setRun, runName, active }) => {

  const handleClick = () => {
    // Sets the select run in the Form component
    setRun([runName]);
  };


  return (
    <Card className={'run-card ' +  (active ? "run-card-active" : "run-card")} onClick={handleClick}>
      <Card.Body className="run-card-body">
        <Card.Title className="run-card-title">{runData["type"]}</Card.Title>
        <Card.Title className="run-card-sub-title">{runName}</Card.Title>
        <Card.Text className="run-card-info-text">
  <span>
    <b>Author:</b> {runData["author"]}
  </span>
          <br />
          {runData?.display_metadata
            ? Object.entries(runData["display_metadata"]).map(([key, value]) => (
              <span key={key}>
        <b>{key.replace(/_/g, " ")}:</b>{" "}
                {Array.isArray(value) ? value.join(", ") : value}
                <br />
      </span>
            ))
            : <span>No metadata available</span>}
        </Card.Text>

      </Card.Body>
    </Card>
  );
};

export default memo(RunCard);
