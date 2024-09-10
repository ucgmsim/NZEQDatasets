from cs_api.server import db
import enum
from sqlalchemy import Enum

import pandas as pd

from dropbox_rclone import dropbox_reading


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

run_faults = db.Table(
    "run_faults",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column("fault_id", db.Integer, db.ForeignKey("faults.id"), primary_key=True),
)

fault_files = db.Table(
    "fault_files",
    db.Column("fault_id", db.Integer, db.ForeignKey("faults.id"), primary_key=True),
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

    n_faults = db.Column(db.Integer)
    region = db.Column(db.String(100))

    grid_spacing_id = db.Column(db.Integer, db.ForeignKey("grid_spacings.id"))
    grid_spacing = db.relationship("GridSpacing")

    tect_types = db.relationship("TectType", secondary=run_tecttypes, backref="runs")
    data_types = db.relationship("DataType", secondary=run_datatypes, backref="runs")
    faults = db.relationship("Fault", secondary=run_faults, backref="runs")
    sites = db.relationship("Site", secondary=site_runs, backref="runs")
    steps = db.relationship("StepMetadata", back_populates="run")

    def __init__(
        self,
        run_name: str,
        run_info: dict,
        site_df: pd.DataFrame,
        dropbox_df: pd.DataFrame = None,
        dropbox_directory: str = None,
    ):
        """
        Create a run object from a run name
        from extracting the data from dropbox

        Parameters
        ----------
        run_name : str
            Name of the run
        run_info : dict
            Dictionary of run metadata information
        site_df : pd.DataFrame
            DataFrame of site information for this specific run event
        dropbox_df : pd.DataFrame
            DataFrame of stored links for downloading to save time on the dropbox API
            Can be None and if not found in the df then it will be extracted from the API
        dropbox_directory : str (optional)
            Path to the dropbox directory, if None then will use the default Cybershake directory
        """
        faults = dropbox_reading.get_run_info(run_name, dropbox_directory)
        dbx = dropbox_reading.get_dropbox_api_object()
        self.run_name = run_name
        self.n_faults = len(faults)
        self.region = run_info["region"]
        self.grid_spacing = GridSpacing.query.filter_by(
            grid_spacing=run_info["grid"]
        ).first()
        self.type = RunType.query.filter_by(type=str(run_info["type"])).first()
        self.tect_types = [
            TectType.query.filter_by(tect_type=tect_type).first()
            for tect_type in run_info["tectonic_types"]
        ]
        # Create each fault for the run
        data_types_found = set()
        run_faults_list = []
        for fault, files in faults.items():
            fault_files_list = []
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
                        run_name, file_name.split("/")[1], dropbox_directory
                    )
                    download_link = dropbox_reading.get_download_link(file_path, dbx)
                else:
                    download_links = dropbox_df.loc[
                        (dropbox_df["run_name"] == run_name)
                        & (dropbox_df["fault_name"] == fault)
                        & (dropbox_df["file_name"] == file_name.split("/")[1])
                    ]["dropbox_link"]
                    if len(download_links) == 0:
                        file_path = dropbox_reading.get_full_dropbox_path(
                            run_name, file_name.split("/")[1], dropbox_directory
                        )
                        download_link = dropbox_reading.get_download_link(
                            file_path, dbx
                        )
                    else:
                        dropbox_link = download_links.values[0]

                file_obj = File(
                    file_name=file_name.split("/")[1],
                    download_link=download_link,
                    file_size=file_size,
                    data_type=file_data_type,
                )
                fault_files_list.append(file_obj)
                db.session.add(file_obj)
            fault_obj = Fault(
                fault_name=fault,
                run=self,
                files=fault_files_list,
            )
            run_faults_list.append(fault_obj)
            db.session.add(fault_obj)
        self.data_types = list(data_types_found)
        self.faults = run_faults_list
        # Add the sites for each row of the df
        sites = []
        # Only get rows from the site df where the run name column is True
        site_df = site_df[site_df[run_name] == True]
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

    @classmethod
    def create_live_run(cls, run_name, run_info, fault_info):
        """
        Creates a live Run, which does not set any dropbox or site information

        Parameters
        ----------
        run_name : str
            Name of the run
        run_info : dict
            Dictionary of run metadata information
        fault_info : dict
            Dictionary of fault information, this includes the number of realisations per fault
            e.g. {"fault1": 2, "fault2": 3}
        """
        self.run_name = run_name
        self.n_faults = len(fault_info)
        self.region = run_info["region"]
        self.grid_spacing = GridSpacing.query.filter_by(
            grid_spacing=run_info["grid"]
        ).first()
        self.type = RunType.query.filter_by(type=str(run_info["type"])).first()
        self.tect_types = [
            TectType.query.filter_by(tect_type=tect_type).first()
            for tect_type in run_info["tectonic_types"]
        ]
        run = cls(
            run_name=run_name,
            region=run_info["region"],
            grid_spacing=GridSpacing.query.filter_by(grid_spacing=run_info["grid"]).first(),
            type=RunType.query.filter_by(type=str(run_info["type"])).first(),
            tect_types=[
                TectType.query.filter_by(tect_type=tect_type).first()
                for tect_type in run_info["tectonic_types"]
            ]
        )
        faults = []
        for fault, n_rels in fault_info.items():
            fault_obj = Fault(fault_name=fault, run=self)
            for i in range(n_rels):
                realisation_obj = Realisation(realisation_number=i+1, fault=fault_obj)
                db.session.add(realisation_obj)
            db.session.add(fault_obj)
            faults.append(fault_obj)
        self.faults = faults

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


class Fault(db.Model):
    __tablename__ = "faults"
    id = db.Column(db.Integer, primary_key=True)

    fault_name = db.Column(
        db.String(100),
    )

    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"))
    run = db.relationship("Run")

    files = db.relationship("File", secondary=fault_files, backref="faults")
    realisations = db.relationship("Realisation", back_populates="fault")
    steps = db.relationship("StepMetadata", back_populates="fault")


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
    runtime = db.Column(db.Float, nullable=False)
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
        self.step_metadata


class StepMetadata(db.Model):
    __tablename__ = "step_metadata"
    id = db.Column(db.String(36), primary_key=True)
    workflow_step = db.Column(db.String(50), nullable=False)

    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=True)
    run = db.relationship("Run", back_populates="steps")

    fault_id = db.Column(db.Integer, db.ForeignKey("faults.id"), nullable=True)
    fault = db.relationship("Fault", back_populates="steps")

    realisation_id = db.Column(db.Integer, db.ForeignKey("realisations.id"), nullable=True)
    realisation = db.relationship("Realisation", back_populates="steps")

    jobs = db.relationship("JobMetadata", back_populates="step_metadata")

    def __init__(self, id, workflow_step, run=None, fault=None, realisation=None):
        self.id = id
        self.workflow_step = workflow_step
        self.run = run
        self.fault = fault
        self.realisation = realisation

class Realisation(db.Model):
    __tablename__ = "realisations"
    id = db.Column(db.Integer, primary_key=True)
    realisation_number = db.Column(db.Integer, nullable=False)
    fault_id = db.Column(db.Integer, db.ForeignKey("faults.id"))
    fault = db.relationship("Fault", back_populates="realisations")
    steps = db.relationship("StepMetadata", back_populates="realisation")

    def __init__(self, realisation_number, fault):
        self.realisation_number = realisation_number
        self.fault = fault