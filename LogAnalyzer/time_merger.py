import json, common
import math
import argparse
import numpy as np
import os
from datetime import datetime
from pathlib import Path

WORKSPACE_FOLDER = "./WorkSpace"
CELL_TIMES = "./WorkSpace/353_abs_time.csv"
GPS_TIMES = "./WorkSpace/gps_abs_time.csv"
TIME_STEP = 1000 # In milliseconds
MODE = 1

def interpolate_time_log_third_ref(start_time, end_time, time_log):
    interpolated_indices = []
    curr_index = 0
    for ref_time in range(start_time, end_time, TIME_STEP):
        # Time increases monotonically. So, step towards the ref time, until the next time is farther from the target, rather than the current time.
        index_found = False
        while not index_found:
            if curr_index == len(time_log) - 1:
                break
            curr_time = time_log[curr_index]
            next_time = time_log[curr_index + 1]
            if abs(curr_time - ref_time) < abs(next_time - ref_time):
                index_found = True
                break
            curr_index += 1
        interpolated_indices.append(int(curr_index))
    return interpolated_indices

def interpolate_time_log(source_log, time_log):
    interpolated_indices = []
    curr_index = 0
    for ref_time in source_log:
        # Time increases monotonically. So, step towards the ref time, until the next time is farther from the target, rather than the current time.
        index_found = False
        while not index_found:
            if curr_index == len(time_log) - 1:
                break
            curr_time = time_log[curr_index]
            next_time = time_log[curr_index + 1]
            if abs(curr_time - ref_time) < abs(next_time - ref_time):
                index_found = True
                break
            curr_index += 1
        interpolated_indices.append(int(curr_index))
    return interpolated_indices

def merge(cell_times, gps_times, mode = MODE, to_csv = False):
    cell_merged_time_indices = []
    gps_merged_time_indices = []
    
    if mode == 0:
        start_time = math.ceil(max(cell_times[0], gps_times[0]))
        end_time = math.floor(min(cell_times[-1], gps_times[-1]))   
        reference = range(start_time, end_time, TIME_STEP)
        cell_merged_time_indices = interpolate_time_log(reference, cell_times)
        gps_merged_time_indices = interpolate_time_log(reference, gps_times)
        references_times_readable = [datetime.utcfromtimestamp(time/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for time in np.arange(start_time, end_time, TIME_STEP)]
        if to_csv:
            common.write_csv(os.path.join(WORKSPACE_FOLDER, "references_times_readable.csv"), references_times_readable)
    elif mode == 1:
        gps_merged_time_indices = interpolate_time_log(cell_times, gps_times)
        cell_merged_time_indices = np.arange(0, len(cell_times), 1)
    
    
    if to_csv:
        common.write_csv(os.path.join(WORKSPACE_FOLDER,"cell_merged_time_indices.csv"), cell_merged_time_indices)
        common.write_csv(os.path.join(WORKSPACE_FOLDER,"gps_merged_time_indices.csv"), gps_merged_time_indices)
        # For Unit Test. Open the csv and verify that the timestamps make sense
        cell_merged_readable = [datetime.utcfromtimestamp(cell_times[index]/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for index in cell_merged_time_indices]
        gps_merged_readable = [datetime.utcfromtimestamp(gps_times[index]/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for index in gps_merged_time_indices]
        common.write_csv(os.path.join(WORKSPACE_FOLDER, "cell_merged_readable.csv"), cell_merged_readable)
        common.write_csv(os.path.join(WORKSPACE_FOLDER, "gps_merged_readable.csv"), gps_merged_readable)


    return (cell_merged_time_indices, gps_merged_time_indices)

if __name__ == "__main__":
    cell_times = common.read_csv(CELL_TIMES)
    gps_times = common.read_csv(GPS_TIMES)
    merge(cell_times, gps_times, to_csv=True)