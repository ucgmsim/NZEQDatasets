from pathlib import Path
import subprocess

import shutil
import pandas as pd
from qcore import formats

cs_versions = [
    "v22p12",
    "v22p11",
    "v22p4",
    "v22p2",
    "v21p6",
    "v21p1",
    "v20p9",
    "v20p6",
    "v20p5",
    "v20p4",
    "v19p5",
]
stage_dir = Path("/home/joel/local/web_cybershake/site_finder")
cs_dropbox_download_py_ffp = Path(
    "/home/joel/code/cs_dropbox_sync/dropbox_rclone/dropbox_rclone/scripts/cs_dropbox_download.py"
)
ll_file = Path(
    "/mnt/mantle_data/seistech/sites/20p3/non_uniform_whole_nz_with_real_stations-hh400_v20p3_land.ll"
)

# Create the main dataframe with columns being the cs versions and the rows being the stations
# Fill with False
station_df = formats.load_station_file(ll_file)
main_df = pd.DataFrame(
    index=station_df.index.values,
    columns=cs_versions,
    data=False,
)

# Check if there is already a main df
if (stage_dir / "main_df.csv").exists():
    main_df = pd.read_csv(stage_dir / "main_df.csv", index_col=0)
    # Find the last cs version that was processed (last column with True values
    last_cs_version = main_df.columns[main_df.any()].values[-1]
    # Slice the cs_verisons to only include the ones after the last cs version
    cs_versions = cs_versions[cs_versions.index(last_cs_version) :]


for cs_version in cs_versions:
    # Download the data
    print(f"Downloading {cs_version}")
    root_dir = stage_dir / cs_version
    root_dir.mkdir(exist_ok=True, parents=True)
    # Only run if not the first in the list
    if cs_version != cs_versions[0]:
        p = subprocess.Popen(
            f"python {cs_dropbox_download_py_ffp} {cs_version} --download_dir {root_dir} --force_untar --cleanup -t IM",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.wait()
    print(f"Downloaded {cs_version}")
    # For each fault load the 1st realistion and get the list of stations
    for fault_dir in root_dir.iterdir():
        if fault_dir.is_dir():
            fault_name = fault_dir.name
            # Find the 1st realisation under any folder directory under fault_dir using glob
            rel_csv_ffp = list(fault_dir.glob("**/*REL01.csv"))[0]
            rel_csv = pd.read_csv(rel_csv_ffp)
            # Get the list of stations
            stations = rel_csv["station"].unique()
            # Set the stations to True
            main_df.loc[stations, cs_version] = True
            # Find stations that are not in the station list
            missing_stations = set(main_df.index.values) - set(stations)

    # Save the main df
    main_df.to_csv(stage_dir / "main_df.csv")
    print(f"Saved main df for {cs_version}")

    # remove the data
    shutil.rmtree(root_dir)
