from cs_api.server import db

from cs_api.db.models import *


def get_data_types():
    """
    Get the data types from the database
    :return: list of data types
    """
    return [data_type.data_type for data_type in DataType.query.all()]


def get_tect_types():
    """
    Get the tectonic types from the database
    :return: list of tectonic types
    """
    return sorted([tect_type.tect_type for tect_type in TectType.query.all()])


def get_grid_spacings():
    """
    Get the grid spacings from the database
    :return: list of grid spacings
    """
    return sorted(
        [grid_spacing.grid_spacing for grid_spacing in GridSpacing.query.all()]
    )


def get_run_types():
    """
    Get the run types aviailable from the database
    :return: list of different run types e.g. (Historical, Cybershake)
    """
    return sorted([run_type.type for run_type in RunType.query.all()])


def get_available_run_names():
    """
    Get the available runs from the database
    :return: list of available runs
    """
    return [run.run_name for run in Run.query.all()]


def get_available_runs():
    """
    Get the available runs from the database
    :return: list of available run objects
    """
    return Run.query.all()


def get_all_unique_faults():
    """
    Get all the unique faults from the database
    :return: list of unique faults
    """
    faults = Fault.query.all()
    unique_faults = {fault.fault_name for fault in faults}
    return sorted(list(unique_faults))


def get_all_unique_sites():
    """
    Get all the unique sites from the database
    :return: list of unique sites
    """
    sites = Site.query.all()
    unique_sites = {site.site_name for site in sites}
    return sorted(list(unique_sites))


def add_run(run: Run):
    """
    Add a run to the database
    :param run: run object
    :return: None
    """
    db.session.add(run)
    db.session.commit()


def get_run(run_name: str):
    """
    Get the run object from the database
    :param run_name: name of the run
    :return: run object
    """
    return Run.query.filter_by(run_name=run_name).first()


def get_fault(fault_name: str, run: Run):
    """
    Get the fault object from the database
    :param fault_name: name of the fault
    :param run: run object
    :return: fault object
    """
    return Fault.query.filter_by(fault_name=fault_name, run=run).first()


def get_realisation(realisation_name: str, fault: Fault):
    """
    Get the realisation object from the database
    :param realisation_name: name of the realisation
    :param fault: fault object
    :return: realisation object
    """
    return Realisation.query.filter_by(realisation_name=realisation_name, fault=fault).first()


def get_job_order(
    run_name: str, fault_name: str, realisation_name: str, workflow_step: str, step_id: int
):
    """
    Get the order of the step
    :param run_name: name of the run
    :param fault_name: name of the fault
    :param realisation_name: name of the realisation
    :param workflow_step: name of the workflow step
    :param step_id: id of the step
    :return: order of the step
    """
    return (
        StepMetadata.query.filter_by(
            run_name=run_name,
            fault_name=fault_name,
            realisation_name=realisation_name,
            workflow_step=workflow_step,
            step_id=step_id,
        )
        .first()
        .order
    )

def get_step(
        step_id: int,
):
    """
    Gets the step metadata from the database

    Parameters
    ----------
    step_id : int
        The id of the step
    """
    return StepMetadata.query.filter_by(step_id=step_id).first()