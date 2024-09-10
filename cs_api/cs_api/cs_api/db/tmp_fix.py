from pathlib import Path
import subprocess
import pandas as pd

# cs_version = "v19p5"
# stage_dir = Path("/home/joel/local/web_cybershake/site_finder")
#
# root_dir = stage_dir / cs_version
#
# for fault_dir in root_dir.iterdir():
#     # Chekc if there is a tar file
#     tar_file = list(fault_dir.glob("*.tar"))
#     # If there is then untar
#     if len(tar_file) > 0:
#         tar_file = tar_file[0]
#         print(f"Untaring {tar_file}")
#         data_dir = fault_dir / "IM"
#         data_dir.mkdir(exist_ok=True, parents=True)
#         p = subprocess.Popen(
#             f"tar -xf {tar_file} -C {data_dir}",
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#         p.wait()
#         print(f"Untared {tar_file}")
#         # remove the tar file
#         tar_file.unlink(missing_ok=True)
# print("Done")


def check_run(data_dir: Path, run: str):
    """
    Check the run has all the required files
    :param data_dir: Path to the data directory
    :param run: String of the run name
    :return:
    """
    IM_source_dir = data_dir / run / "IM_Source"
    Empirical_dir = data_dir / run / "Empirical"
    Plots_dir = data_dir / run / "Plots"
    LIMITED_IMS = [
        "PGA",
        "pSA_0.1",
        "pSA_0.5",
        "pSA_1.0",
        "pSA_3.0",
        "pSA_5.0",
        "pSA_7.5",
    ]
    REALISATIONS = 5

    # List of missing files
    missing_files = []

    # Get the list of faults from the IM_Source dir
    faults = [x.name for x in IM_source_dir.iterdir() if x.is_dir()]

    # Check there is an empirical csv for each fault
    for fault in faults:
        empirical_csv = Empirical_dir / fault / f"{fault}.csv"
        # Add to missing files if it doesn't exist
        if not empirical_csv.exists():
            missing_files.append(empirical_csv)
        # Load the file and check the length is correct
        else:
            empirical_df = pd.read_csv(empirical_csv)
            if len(empirical_df) == 0:
                missing_files.append(empirical_csv)

    # Check there is a plot for each of the different types
    # Check in site residual there is a plot for each IM
    for im in LIMITED_IMS:
        plot = Plots_dir / "site_residual" / f"avg_{im}_ratio.png"
        if not plot.exists():
            missing_files.append(plot)
    # Check there is the correct amount of IM plots
    # One for each fault (median and first 5 realisations), IM and simulation and Empirical
    for fault in faults:
        for rel in range(REALISATIONS+1):
            for im in LIMITED_IMS:
                for sim_emp in ["sim", "emp"]:
                    flt_string = fault if rel == 0 else f"{fault}_REL0{rel}"
                    plot = Plots_dir / "im" / f"{fault}_{im}_{sim_emp}.png"
                    if not plot.exists():
                        missing_files.append(plot)
    # Check there is the corretc amount of log ratio plots
    # One for each fault (median and first 5 realisations) and IM
    for fault in faults:
        for rel in range(REALISATIONS+1):
            for im in LIMITED_IMS:
                flt_string = fault if rel == 0 else f"{fault}_REL0{rel}"
                plot = Plots_dir / "log_ratio" / f"{flt_string}_{im}_ratio.png"
                if not plot.exists():
                    missing_files.append(plot)
    # Check there is the correct amount of std plots
    # One for each fault, IM and [ratio, empirical and simulation]
    for fault in faults:
        for im in LIMITED_IMS:
            for sim_emp_ratio in ["ratio", "emp", "sim"]:
                plot = Plots_dir / "std" / f"{fault}_{im}_{sim_emp_ratio}.png"
                if not plot.exists():
                    missing_files.append(plot)

    # List the missing files
    print(f"Missing files for {run}")
    for missing_file in missing_files:
        print(missing_file)
    print(f"Total missing files: {len(missing_files)}")

# Write a script to check that all plots and Empirical calculations are available for a run
# data_dir = Path("/home/joel/local/streamlit/cs_investigation/data")
# data_dir = Path("/mnt/mantle_data/cs_investigation/live")
# runs = [x.name for x in data_dir.iterdir() if x.is_dir()]
# for run in runs:
#     check_run(data_dir, run)

# Check for tared and untared files for a current run
run_dir = Path("/mnt/mantle_data/cs_investigation/stage/v20p6/IM_Source")

check_run(run_dir.parent.parent, "v20p6")
tared_list = []
untared_list = []
for fault_dir in run_dir.iterdir():
    # Check is a dir
    if fault_dir.is_dir():
        # Check if there is a tar file
        tar_file = list(fault_dir.glob("*.tar"))
        # If there is then untar
        if len(tar_file) > 0:
            tared_list.append(fault_dir.name)
        else:
            untared_list.append(fault_dir.name)
            # tar_file = tar_file[0]
            # print(f"Untaring {tar_file}")
            # data_dir = fault_dir / "IM"
            # data_dir.mkdir(exist_ok=True, parents=True)
            # p = subprocess.Popen(
            #     f"tar -xf {tar_file} -C {data_dir}",
            #     shell=True,
            #     stdout=subprocess.PIPE,
            #     stderr=subprocess.PIPE,
            # )
            # p.wait()
            # print(f"Untared {tar_file}")
            # # remove the tar file
            # tar_file.unlink(missing_ok=True)
print(f"Tared: {len(tared_list)}")
print(f"Untared: {len(untared_list)}")