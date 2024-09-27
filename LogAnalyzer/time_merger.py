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
MODE = 1 # Mode = 1, use first source as reference, Mode = 2: use second source as reference. Mode = 0: use a third reference time scale, give start, end and interval

def interpolate_time_log(source_log, time_log, bIntersect):
    if bIntersect:
            intersectTimeLogs(source_log, time_log)

    interpolated_indices = []
    curr_index = 0
    if bIntersect:
        start = max(min(source_log), min(time_log))
        end = min(max(source_log), min(time_log))
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


def intersectTimeLogs(reference, other):
    while min(reference) < min(other):
        reference.pop(0)
    
    while max(reference) > max(other):
        reference.pop()

def merge_csv(df1, df2, timeIndex1, timeIndex2, bIntersect=False, mode = MODE, to_csv = False):
    indices1, indices2 = merge(df1[timeIndex1].to_list(), df2[timeIndex2], bIntersect, mode, to_csv)
    for column_name in df2.columns: 
        df1[column_name] = df2.iloc[indices2][column_name].to_list()
     
def merge_locs(cell_times, gps_times, gps_lat, gps_lon, gps_alt):
    len_cell_times = len(cell_times)
    interpolated_loc = {"time": cell_times, 
                       "longitude": [None]*len_cell_times, 
                       "latitude": [None]*len_cell_times, 
                       "altitude":[None]*len_cell_times}
    
    start_index = 0
    end_index = len_cell_times

    len_gps_times = len(gps_times)

    for cell_index, t in enumerate(cell_times):
        if gps_times[0] < t:
            start_index = cell_index
            break

    for cell_index, t in enumerate(reversed(cell_times)):
        if  gps_times[-1] > t:
            end_index = cell_index
    
    gps_index_curr = 0
    for cell_index in range(start_index, end_index):
        for gps_index in range(gps_index_curr, len_gps_times):
            if gps_times[gps_index] > cell_times[cell_index]:
                gps_index_curr = gps_index
                interp_ratio = (cell_times[cell_index] - gps_times[gps_index - 1]) / (gps_times[gps_index] - gps_times[gps_index-1])
                interpolated_loc["latitude"][cell_index] = gps_lat[gps_index - 1] + interp_ratio*(gps_lat[gps_index] - gps_lat[gps_index - 1])
                interpolated_loc["longitude"][cell_index] = gps_lon[gps_index - 1] + interp_ratio*(gps_lon[gps_index] - gps_lon[gps_index - 1])
                interpolated_loc["altitude"][cell_index] = gps_alt[gps_index - 1] + interp_ratio*(gps_alt[gps_index] - gps_alt[gps_index - 1])
                break

    return interpolated_loc



def merge(cell_times, gps_times, bIntersect=False, mode = MODE, to_csv = False, gps_df = None):
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
        gps_merged_time_indices = interpolate_time_log(cell_times, gps_times, bIntersect)
        cell_merged_time_indices = np.arange(0, len(cell_times), 1)
        
    elif mode == 2:
        cell_merged_time_indices = np.array(interpolate_time_log(gps_times, cell_times))
        gps_merged_time_indices = np.arange(0, len(gps_times), 1)
    
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