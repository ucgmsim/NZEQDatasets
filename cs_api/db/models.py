from cs_api.server import db

class Dataset(db.Model):
    """
    Base model for Datasets.
    """
    __tablename__ = "datasets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(255), nullable=True)

    # Relationships
    display_metadata = db.relationship("DatasetMetadata", back_populates="dataset", cascade="all, delete-orphan")
    sites = db.relationship("Site", back_populates="dataset", cascade="all, delete-orphan")
    events = db.relationship("Event", back_populates="dataset", cascade="all, delete-orphan")
    data_types = db.relationship("DataType", back_populates="dataset", cascade="all, delete-orphan")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "author": self.author,
            "display_metadata": {meta.key: meta.value for meta in self.display_metadata},
            "sites": [site.to_json() for site in self.sites],
            "events": [event.to_json() for event in self.events],
            "data_types": [data_type.to_json() for data_type in self.data_types]
        }


class DatasetMetadata(db.Model):
    """
    Model for Metadata associated with a Dataset.
    """
    __tablename__ = "dataset_metadata"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)

    # Foreign keys
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    dataset = db.relationship("Dataset", back_populates="display_metadata")


class Site(db.Model):
    """
    Model for the sites table in the database.
    """
    __tablename__ = "sites"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # Foreign keys
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    dataset = db.relationship("Dataset", back_populates="sites")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


class Event(db.Model):
    """
    Model for the events table in the database.
    """
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    hyp_latitude = db.Column(db.Float, nullable=True)
    hyp_longitude = db.Column(db.Float, nullable=True)
    corner0_latitude = db.Column(db.Float, nullable=True)
    corner0_longitude = db.Column(db.Float, nullable=True)
    corner1_latitude = db.Column(db.Float, nullable=True)
    corner1_longitude = db.Column(db.Float, nullable=True)
    corner2_latitude = db.Column(db.Float, nullable=True)
    corner2_longitude = db.Column(db.Float, nullable=True)
    corner3_latitude = db.Column(db.Float, nullable=True)
    corner3_longitude = db.Column(db.Float, nullable=True)

    # Foreign keys
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    dataset = db.relationship("Dataset", back_populates="events")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "hypocenter": {
                "latitude": self.hyp_latitude,
                "longitude": self.hyp_longitude
            },
            "corners": [
                {"latitude": self.corner0_latitude, "longitude": self.corner0_longitude},
                {"latitude": self.corner1_latitude, "longitude": self.corner1_longitude},
                {"latitude": self.corner2_latitude, "longitude": self.corner2_longitude},
                {"latitude": self.corner3_latitude, "longitude": self.corner3_longitude}
            ]
        }


class DataType(db.Model):
    """
    Model for the data_types table in the database.
    """
    __tablename__ = "data_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    files = db.relationship("File", back_populates="data_type", cascade="all, delete-orphan")

    # Foreign keys
    dataset_id = db.Column(db.Integer, db.ForeignKey("datasets.id"), nullable=False)
    dataset = db.relationship("Dataset", back_populates="data_types")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "files": [file.to_json() for file in self.files]
        }


class File(db.Model):
    """
    Model for the files table in the database.
    """
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    dropbox_link = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Float, nullable=False)

    # Foreign keys
    data_type_id = db.Column(db.Integer, db.ForeignKey("data_types.id"), nullable=False)
    data_type = db.relationship("DataType", back_populates="files")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "dropbox_link": self.dropbox_link,
            "file_size": self.file_size
        }
