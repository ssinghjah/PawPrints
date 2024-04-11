import json, common
import math
import argparse
import numpy as np
import os
from datetime import datetime

WORKSPACE_FOLDER = "./WorkSpace/"
CELL_TIMES = "./WorkSpace/Data/connected_abs_time.csv"
GPS_TIMES = "./WorkSpace/Data/gps_abs_time.csv"
TIME_STEP = 1000 # In milliseconds

def interpolate_time_log(start_time, end_time, time_log):
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

cell_times =  common.read_csv(CELL_TIMES)
gps_times = common.read_csv(GPS_TIMES)

start_time = math.ceil(max(cell_times[0], gps_times[0]))
end_time = math.floor(min(cell_times[-1], gps_times[-1]))

cell_merged_time_indices = interpolate_time_log(start_time, end_time, cell_times)
gps_merged_time_indices = interpolate_time_log(start_time, end_time, gps_times)

common.write_csv(os.path.join(WORKSPACE_FOLDER,"./Data/cell_merged_time_indices.csv"), cell_merged_time_indices)
common.write_csv(os.path.join(WORKSPACE_FOLDER,"./Data/gps_merged_time_indices.csv"), gps_merged_time_indices)

# For Unit Test: we can open the below csvs and verify that the timestamps make sense
cell_merged_readable = [datetime.utcfromtimestamp(cell_times[index]/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for index in cell_merged_time_indices]
gps_merged_readable = [datetime.utcfromtimestamp(gps_times[index]/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for index in gps_merged_time_indices]
references_times_readable = [datetime.utcfromtimestamp(time/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for time in np.arange(start_time, end_time, TIME_STEP)]

common.write_csv(os.path.join(WORKSPACE_FOLDER, "./Data/references_times_readable.csv"), references_times_readable)
common.write_csv(os.path.join(WORKSPACE_FOLDER, "./Data/cell_merged_readable.csv"), cell_merged_readable)
common.write_csv(os.path.join(WORKSPACE_FOLDER, "./Data/gps_merged_readable.csv"), gps_merged_readable)
