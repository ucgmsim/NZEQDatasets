import enum
from typing import Optional

import pandas as pd
from dropbox_rclone import dropbox_reading
from sqlalchemy import Enum, Interval

from cs_api.server import db

run_tecttypes = db.Table(
    "run_tecttypes",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column(
        "tecttype_id", db.Integer, db.ForeignKey("tect_types.id"), primary_key=True
    ),
)


run_datatypes = db.Table(
    "run_data_types",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column(
        "datatype_id", db.Integer, db.ForeignKey("data_types.id"), primary_key=True
    ),
)

run_events = db.Table(
    "run_events",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), primary_key=True),
)

event_files = db.Table(
    "event_files",
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), primary_key=True),
    db.Column("file_id", db.Integer, db.ForeignKey("files.id"), primary_key=True),
)

site_runs = db.Table(
    "site_runs",
    db.Column("site_id", db.Integer, db.ForeignKey("sites.id"), primary_key=True),
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
)


class Run(db.Model):
    __tablename__ = "runs"
    id = db.Column(db.Integer, primary_key=True)
    run_name = db.Column(
        db.String(100),
        unique=True,
    )
    type_id = db.Column(db.Integer, db.ForeignKey("run_types.id"))
    type = db.relationship("RunType")

    n_events = db.Column(db.Integer)
    region = db.Column(db.String(100))

    grid_spacing_id = db.Column(db.Integer, db.ForeignKey("grid_spacings.id"))
    grid_spacing = db.relationship("GridSpacing")

    tect_types = db.relationship("TectType", secondary=run_tecttypes, backref="runs")
    data_types = db.relationship("DataType", secondary=run_datatypes, backref="runs")
    events = db.relationship("Event", secondary=run_events, backref="runs")
    sites = db.relationship("Site", secondary=site_runs, backref="runs")
    steps = db.relationship("StepMetadata", back_populates="run")

    def __init__(
        self,
        run_name: str,
        run_info: dict,
        site_df: Optional[pd.DataFrame] = None,
        dropbox_df: Optional[pd.DataFrame] = None,
        live_run: bool = False,
    ):
        """
        Create a run object from a run name from extracting the data from dropbox. Or initialise a run object
        that is currently live and still being run on an HPC.

        Parameters
        ----------
        run_name : str
            Name of the run
        run_info : dict
            Dictionary of run metadata information
            Should include region, grid, type, tectonic_types and events with realisation numbers if the run is live
        site_df : pd.DataFrame
            DataFrame of site information for this specific run event
        dropbox_df : pd.DataFrame
            DataFrame of stored links for downloading to save time on the dropbox API
            Can be None and if not found in the df then it will be extracted from the API
        live_run : bool, optional default=False
            If the run is a live run, ignores creating all the links and files
        """
        if live_run:
            events = run_info["events"]
        else:
            events = dropbox_reading.get_run_info(run_name)
            dbx = dropbox_reading.get_dropbox_api_object()
        self.run_name = run_name
        self.n_events = len(events)
        self.region = run_info["region"]
        self.grid_spacing = GridSpacing.query.filter_by(
            grid_spacing=run_info["grid"]
        ).first()
        self.type = RunType.query.filter_by(type=str(run_info["type"])).first()
        self.tect_types = [
            TectType.query.filter_by(tect_type=tect_type).first()
            for tect_type in run_info["tectonic_types"]
        ]

        if live_run:
            # Add the events and Realisations for the run
            run_events_list = []
            run_realisations_list = []
            for event, n_rels in events.items():
                event_obj = Event(event_name=event, run=self)
                for rel in range(1, n_rels + 1):
                    realisation_obj = Realisation(realisation_number=rel, event=event_obj)
                    run_realisations_list.append(realisation_obj)
                    db.session.add(realisation_obj)
                event_obj.realisations = run_realisations_list
                run_events_list.append(event_obj)
                db.session.add(event_obj)
            self.events = run_events_list
        else:
            # Create each event for the run
            data_types_found = set()
            run_events_list = []
            for event, files in events.items():
                event_files_list = []
                for file_name, file_size in files.items():
                    data_type_str = file_name.split(".")[0].split("_")[1]
                    file_data_type = DataType.query.filter_by(
                        data_type=data_type_str
                    ).first()
                    data_types_found.add(file_data_type)

                    # Try find the dropbox link from the dropbox df
                    # If None or not found then get the link from the dropbox API
                    if dropbox_df is None:
                        file_path = dropbox_reading.get_full_dropbox_path(
                            run_name, file_name.split("/")[1]
                        )
                        download_link = dropbox_reading.get_download_link(file_path, dbx)
                    else:
                        download_links = dropbox_df.loc[
                            (dropbox_df["run_name"] == run_name)
                            & (dropbox_df["event_name"] == event)
                            & (dropbox_df["file_name"] == file_name.split("/")[1])
                        ]["dropbox_link"]
                        if len(download_links) == 0:
                            file_path = dropbox_reading.get_full_dropbox_path(
                                run_name, file_name.split("/")[1]
                            )
                            download_link = dropbox_reading.get_download_link(
                                file_path, dbx
                            )
                        else:
                            download_link = download_links.values[0]

                    file_obj = File(
                        file_name=file_name.split("/")[1],
                        download_link=download_link,
                        file_size=file_size,
                        data_type=file_data_type,
                    )
                    event_files_list.append(file_obj)
                    db.session.add(file_obj)
                event_obj = Event(
                    event_name=event,
                    run=self,
                    files=event_files_list,
                )
                run_events_list.append(event_obj)
                db.session.add(event_obj)
            self.data_types = list(data_types_found)
            self.events = run_events_list
        if site_df is not None:
            # Add the sites for each row of the df
            sites = []
            # Only get rows from the site df where the run name column is True
            site_df = site_df[site_df[run_name]]
            for index, row in site_df.iterrows():
                site_obj = Site(
                    site_name=index,
                    lat=row["lat"],
                    lon=row["lon"],
                    vs30=row["vs30"],
                    z1p0=row["z1p0"],
                    z2p5=row["z2p5"],
                    run=self,
                )
                sites.append(site_obj)
                db.session.add(site_obj)
            self.sites = sites


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(
        db.String(100),
    )
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    vs30 = db.Column(db.Float)
    z1p0 = db.Column(db.Float)
    z2p5 = db.Column(db.Float)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"))
    run = db.relationship("Run")

    def __init__(
        self,
        site_name: str,
        lat: float,
        lon: float,
        vs30: float,
        z1p0: float,
        z2p5: float,
        run: Run,
    ):
        """
        Create a site object from a site name
        from extracting the data from dropbox

        Parameters
        ----------
        site_name : str
            Name of the site
        lat : float
            Latitude of the site
        lon : float
            Longitude of the site
        vs30 : float
            Vs30 value of the site
        z1p0 : float
            Z1.0 value of the site
        z2p5 : float
            Z2.5 value of the site
        run : Run
            Run object that the site is associated with
        """
        self.site_name = site_name
        self.lat = lat
        self.lon = lon
        self.vs30 = vs30
        self.z1p0 = z1p0
        self.z2p5 = z2p5
        self.run = run


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)

    event_name = db.Column(
        db.String(100),
    )

    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"))
    run = db.relationship("Run")

    files = db.relationship("File", secondary=event_files, backref="events")
    realisations = db.relationship("Realisation", back_populates="event")
    steps = db.relationship("StepMetadata", back_populates="event")


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)

    file_name = db.Column(
        db.String(100),
    )
    download_link = db.Column(
        db.String(255),
    )
    file_size = db.Column(
        db.Integer,
    )

    data_type_id = db.Column(db.Integer, db.ForeignKey("data_types.id"))
    data_type = db.relationship("DataType")


class TectType(db.Model):
    __tablename__ = "tect_types"
    id = db.Column(db.Integer, primary_key=True)
    tect_type = db.Column(db.String(100), unique=True)


class DataType(db.Model):
    __tablename__ = "data_types"
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(100), unique=True)


class GridSpacing(db.Model):
    __tablename__ = "grid_spacings"
    id = db.Column(db.Integer, primary_key=True)
    grid_spacing = db.Column(db.String(100), unique=True)


class RunType(db.Model):
    __tablename__ = "run_types"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), unique=True)

class RunTypeEnum(enum.Enum):
    resubmission = "resubmission"
    checkpointed = "checkpointed"
    initial = "initial"

class JobMetadata(db.Model):
    __tablename__ = "job_metadata"
    job_id = db.Column(db.Integer, primary_key=True)
    time_submitted = db.Column(db.DateTime, nullable=False)
    time_started = db.Column(db.DateTime, nullable=True)
    time_ended = db.Column(db.DateTime, nullable=True)
    ncpus = db.Column(db.Integer, nullable=False)
    runtime = db.Column(Interval, nullable=False)
    type = db.Column(Enum(RunTypeEnum), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    step_metadata_id = db.Column(db.Integer, db.ForeignKey("step_metadata.id"))
    step_metadata = db.relationship("StepMetadata", back_populates="jobs")

    def __init__(self, job_id, time_submitted, time_started, time_ended, ncpus, runtime, type, order, step_metadata):
        self.job_id = job_id
        self.time_submitted = time_submitted
        self.time_started = time_started
        self.time_ended = time_ended
        self.ncpus = ncpus
        self.runtime = runtime
        self.type = type
        self.order = order
        self.step_metadata = step_metadata


class StepMetadata(db.Model):
    __tablename__ = "step_metadata"
    id = db.Column(db.Integer, primary_key=True)
    workflow_step = db.Column(db.String(50), nullable=False)

    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=True)
    run = db.relationship("Run", back_populates="steps")

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    event = db.relationship("Event", back_populates="steps")

    realisation_id = db.Column(db.Integer, db.ForeignKey("realisations.id"), nullable=True)
    realisation = db.relationship("Realisation", back_populates="steps")

    jobs = db.relationship("JobMetadata", back_populates="step_metadata")

    def __init__(self, id, workflow_step, run=None, event=None, realisation=None):
        self.id = id
        self.workflow_step = workflow_step
        self.run = run
        self.event = event
        self.realisation = realisation

class Realisation(db.Model):
    __tablename__ = "realisations"
    id = db.Column(db.Integer, primary_key=True)
    realisation_number = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    event = db.relationship("Event", back_populates="realisations")
    steps = db.relationship("StepMetadata", back_populates="realisation")

    def __init__(self, realisation_number, event):
        self.realisation_number = realisation_number
        self.event = event