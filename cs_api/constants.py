from pathlib import Path

# Metadata endpoints
GET_DATASET_TYPES = "/meta/dataset_types"
GET_UNIQUE_SITES = "/meta/unique_sites"
GET_UNIQUE_EVENTS = "/meta/unique_events"

# Dataset endpoints
GET_DATASETS_INFO = "/datasets/info"
GET_DATASETS_FROM_INTERESTS = "/datasets/interests"

# Metadata Path
METADATA_FILE = Path(__file__).parent / "db" / "resources" / "run_metadata.yaml"
SITE_DF_FILE = Path(__file__).parent / "db" / "resources" / "site_df.csv"
DROPBOX_FILE = Path(__file__).parent / "db" / "resources" / "dropbox.csv"
