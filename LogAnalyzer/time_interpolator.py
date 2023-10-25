import json, common
import math

LOG_FOLDER = "../Data/"
BS = "pawprints"
GPS = "gps"
TIME_LOG_SUFFIX = "_abs_time.csv"
METADATA_FOLDER = "./metadata.json"
TIME_STEP = 1000 # In milliseconds
def interpolate_time_log(start_time, end_time, start_index, end_index, time_log):
    interpolated_indices = []
    time_log_index = start_index
    for time in range(start_time, end_time, TIME_STEP):
        curr_time = time_log[time_log_index]
        if (abs(curr_time - time) > (time_log[time_log_index] - time)) and (time_log_index+1) <= end_index:
            time_log_index += 1
        interpolated_indices.append(int(time_log_index))
    return interpolated_indices

with open(LOG_FOLDER + METADATA_FOLDER) as f:
    metadata = json.load(f)
    bs_times =  common.read_csv(LOG_FOLDER + BS + TIME_LOG_SUFFIX)
    gps_times = common.read_csv(LOG_FOLDER + GPS + TIME_LOG_SUFFIX)
    interpolated_time_indices = interpolate_time_log(math.ceil(metadata["start_time"]), math.floor(metadata["end_time"]), metadata["pawprints_start_index"], metadata["pawprints_end_index"], bs_times)
    common.write_csv(LOG_FOLDER + BS + "_interpolated_time_indices.csv", interpolated_time_indices)
    interpolated_time_indices = interpolate_time_log(math.ceil(metadata["start_time"]), math.floor(metadata["end_time"]), metadata["gps_start_index"], metadata["gps_end_index"], gps_times)
    common.write_csv(LOG_FOLDER + GPS + "_interpolated_time_indices.csv", interpolated_time_indices)

