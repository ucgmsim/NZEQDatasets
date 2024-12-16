from cs_api.server import db
from models import Dataset, DatasetMetadata, Site, Event, DataType, File

def create_demo_data():

    # Add db.drop_all() if you want to drop all tables and start from scratch
    db.drop_all()

    # Create tables - It only creates when tables don't exist
    db.create_all()
    db.session.commit()

    # Shared data
    sites = [
        Site(name="Site A", latitude=34.05, longitude=-118.25),
        Site(name="Site B", latitude=36.77, longitude=-119.41),
        Site(name="Site C", latitude=37.77, longitude=-122.42)
    ]

    events = [
        Event(name="Event X"),
        Event(name="Event Y")
    ]

    # Create Datasets
    datasets = []

    # Cybershake Datasets
    for i in range(2):
        dataset = Dataset(name=f"Cybershake Dataset {i+1}", type="Cybershake", author="ucgmsim")
        dataset.display_metadata.append(DatasetMetadata(key="grid_spacing", value="200m"))
        dataset.sites.extend(sites)
        dataset.events.extend(events)

        data_type = DataType(name="Velocity Model")
        data_type.files.append(File(name="velocity_model.csv", dropbox_link="http://example.com/vm.csv", file_size=12.5))
        dataset.data_types.append(data_type)

        datasets.append(dataset)

    # Historical Dataset
    historical = Dataset(name="Historical Dataset 1", type="Historical", author="ucgmsim")
    historical.display_metadata.append(DatasetMetadata(key="grid_spacing", value="1.0"))
    historical.sites.extend(sites[:2])  # Only include first two sites
    historical.events.append(events[0])

    data_type = DataType(name="Historical Events")
    data_type.files.append(File(name="historical_events.csv", dropbox_link="http://example.com/he.csv", file_size=8.2))
    historical.data_types.append(data_type)

    datasets.append(historical)

    # Observed Datasets
    for i in range(2):
        observed = Dataset(name=f"Observed Dataset {i+1}", type="Observed", author="ucgmsim")
        observed.display_metadata.append(DatasetMetadata(key="num_records", value=str(100 * (i + 1))))
        observed.sites.append(sites[i])
        observed.events.append(events[1])

        data_type = DataType(name="Seismic Records")
        data_type.files.append(File(name="seismic_records.csv", dropbox_link="http://example.com/sr.csv", file_size=15.0))
        observed.data_types.append(data_type)

        datasets.append(observed)

    # Add everything to the session
    db.session.add_all(datasets)
    db.session.commit()

if __name__ == "__main__":
    create_demo_data()
    print("Demo database populated successfully!")

