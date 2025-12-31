import pandas as pd

# Read speed log
SPEED_LOG_PATH = "C:\\Users\\ssingh28\\RadioDemographics\\data\\aerpaw-1_motion.csv"
speed_log = pd.read_csv(SPEED_LOG_PATH)

# Read merged cellular and pos log
PAWPRINTS_LOG = "C:\\Users\\ssingh28\\RadioDemographics\\data\\split_original\\aerpaw-1_cellular_seg_0.csv"
pawprints_pd = pd.read_csv(PAWPRINTS_LOG)

num_rows = len(pawprints_pd)
speed_log_pointer = 0

def get_next_different_gps(row_num):
    """Return the row index of the next row with different GPS coordinates."""
    curr_lat = pawprints_pd.iloc[row_num]["latitude"]
    curr_lon = pawprints_pd.iloc[row_num]["longitude"]
    next_row = row_num + 1
    while next_row < num_rows:
        next_lat = pawprints_pd.iloc[next_row]["latitude"]
        next_lon = pawprints_pd.iloc[next_row]["longitude"]
        if next_lat != curr_lat or next_lon != curr_lon:
            return next_row
        next_row += 1
    return -1  # No further different GPS found

def get_closest_speed_pointer(pawprints_abs_time):
    """Return the index in speed_log closest to the given absolute time."""
    global speed_log_pointer
    while speed_log_pointer < len(speed_log) - 1:
        speed_time_curr = speed_log.iloc[speed_log_pointer]["phone_abs_time"]
        speed_time_next = speed_log.iloc[speed_log_pointer + 1]["phone_abs_time"]
        if speed_time_curr <= pawprints_abs_time <= speed_time_next:
            return speed_log_pointer
        speed_log_pointer += 1
    return len(speed_log) - 1

def interpolate_block(start_idx, end_idx):
    """
    Interpolate all rows between start_idx (inclusive) and end_idx (exclusive)
    based on time and speed to the next different GPS point.
    """
    next_diff_row = get_next_different_gps(end_idx - 1)
    if next_diff_row == -1:
        # No further different GPS, just copy current lat/lon
        for i in range(start_idx, end_idx):
            pawprints_pd.at[i, "interp_lat"] = pawprints_pd.at[i, "latitude"]
            pawprints_pd.at[i, "interp_lon"] = pawprints_pd.at[i, "longitude"]
        return next_diff_row

    # Current and next different GPS
    lat_start = pawprints_pd.at[start_idx, "latitude"]
    lon_start = pawprints_pd.at[start_idx, "longitude"]
    lat_end = pawprints_pd.at[next_diff_row, "latitude"]
    lon_end = pawprints_pd.at[next_diff_row, "longitude"]

    time_start = pawprints_pd.at[start_idx, "phone_abs_time"]
    time_end = pawprints_pd.at[next_diff_row, "phone_abs_time"]
    delta_time = time_end - time_start

    for i in range(start_idx, end_idx):
        t = pawprints_pd.at[i, "phone_abs_time"]
        fraction = (t - time_start) / delta_time if delta_time > 0 else 0
        interp_lat = lat_start + fraction * (lat_end - lat_start)
        interp_lon = lon_start + fraction * (lon_end - lon_start)
        pawprints_pd.at[i, "interp_lat"] = interp_lat
        pawprints_pd.at[i, "interp_lon"] = interp_lon

    return next_diff_row  # return pointer to next row to process

# Initialize interpolated columns
pawprints_pd["interp_lat"] = pawprints_pd["latitude"]
pawprints_pd["interp_lon"] = pawprints_pd["longitude"]

# Main loop: iterate over pawprints, handle duplicate blocks
row_pointer = 0
while row_pointer < num_rows:
    next_diff_row = get_next_different_gps(row_pointer)
    if next_diff_row == -1 or next_diff_row == row_pointer + 1:
        # No duplicates or only single row, move to next
        row_pointer += 1 
    else:
        # Interpolate all duplicates in block
        row_pointer = interpolate_block(row_pointer, next_diff_row)

# Save updated dataframe
pawprints_pd["latitude"] = pawprints_pd["interp_lat"]
pawprints_pd["longitude"] = pawprints_pd["interp_lon"]
pawprints_pd.to_csv("C:\\Users\\ssingh28\\RadioDemographics\\data\\split_fixed\\aerpaw-1_cellular_block_interpolated_seg_0.csv", index=False)
