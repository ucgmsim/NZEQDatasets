from cs_api.db.models import Dataset, Site, Event, DataType


def get_data_types():
    """
    Get the data types from the database
    :return: list of data types
    """
    return [data_type.data_type for data_type in DataType.query.all()]


def get_dataset_types():
    """
    Get the dataset types aviailable from the database
    :return: list of different dataset types e.g. (Historical, Cybershake)
    """
    return sorted(list({dataset.type for dataset in Dataset.query.all()}))


def get_available_datasets():
    """
    Get the available datasets from the database
    :return: list of available datasets
    """
    return Dataset.query.all()


def get_available_runs():
    """
    Get the available runs from the database
    :return: list of available run objects
    """
    return Dataset.query.all()


def get_all_unique_events():
    """
    Get all the unique events from the database
    :return: list of unique events
    """
    events = Event.query.all()
    unique_events = {event.name for event in events}
    return sorted(list(unique_events))


def get_all_unique_sites():
    """
    Get all the unique sites from the database
    :return: list of unique sites
    """
    sites = Site.query.all()
    unique_sites = {site.name for site in sites}
    return sorted(list(unique_sites))


def get_dataset(dataset_name: str):
    """
    Get the run object from the database
    :param dataset_name: name of the run
    :return: dataset object
    """
    return Dataset.query.filter_by(name=dataset_name).first()
