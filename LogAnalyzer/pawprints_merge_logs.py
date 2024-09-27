import argparse
import pandas
import time_merger
import os
import numpy as np

def merge_logs(options):
    data = {}
    cell_info = pandas.read_csv(options.input)
    
    # if options["nr_signal_strength"]: 
    #     data["nr_signal_strength"] = pandas.read_csv(options.nr_signal_strength)
    # else:
    #     data["nr_signal_strength"] = None

    bMergeGPS = options.gps_log is not None
    # bMergeIPerf = options.iperf_log is not None

    # if not bMergeGPS and not bMergeIPerf:
    #     return

    # Common operations 
    cell_info_times = cell_info["companion_abs_time"] if "companion_abs_time" in cell_info else cell_info["phone_abs_time"]

    gps_data = None
    if bMergeGPS:
          gps_data = pandas.read_csv(options.gps_log)

    # Specific operations
    if bMergeGPS:
        print("Merging GPS ...")
        interp_locs = time_merger.merge_locs(cell_info_times, gps_data["abs_time"].to_list(), gps_data["latitude"], gps_data["longitude"], gps_data["altitude"])
        cell_info["longitude"] = interp_locs["longitude"]
        cell_info["latitude"] = interp_locs["latitude"]
        cell_info["altitude"] = interp_locs["altitude"]
        cell_info["zero_altitude"] = cell_info["altitude"][~np.isnan(cell_info["altitude"])]*0.0
        cell_info.to_csv(options.output, index=False)

parser = argparse.ArgumentParser(description='Merge PawPrints logs into .csv.')
parser.add_argument('-i','--input', type = str, default = "./pawprints.csv", help='Input pawprints cellular log file')
parser.add_argument('-g', '--gps-log', type = str, default = None, help='GPS log file')
parser.add_argument('-o', '--output', type=str, default= "./pawprints_merged.csv", help="Prefix of the output csv file(s)")
options = parser.parse_args()

merge_logs(options)




