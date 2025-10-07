import pandas as pd

# Read speed log
SPEED_LOG = "/home/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/aerpaw-1_motion.csv"

# Read merged cellular and pos log
PAWPRINTS_LOG = "/home/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/aerpaw-1_merged.csv"

pawprints_pd = pd.read_csv(PAWPRINTS_LOG)
num_rows = len(pawprints_pd)

speed_log_pointer = 0

def get_next_different_gps(row_num):
    curr_lat = pawprints_pd.iloc[row_num, "lat"]
    curr_lon = pawprints_pd.iloc[row_num, "lon"]
    next_row = row_num + 1
    while(next_row < num_rows):
        next_lat = pawprints_pd.iloc[next_row, "lat"]
        next_lon = pawprints_pd.iloc[next_row, "lon"]
        if (next_lat != curr_lat or next_lon != curr_lon):
            return next_row
        next_row += 1
    return -1


def get_closest_speed(speed_log_pointer, pawprints_abs_time):
    while(speed_log_pointer < len(SPEED_LOG)):
        speed_time_curr = SPEED_LOG.iloc[speed_log_pointer, "abs_time"]
        speed_time_next = SPEED_LOG.islower[speed_log_pointer + 1, "abs_time"]
        if (speed_time_curr < pawprints_abs_time and speed_time_next > pawprints_abs_time):
            return speed_log_pointer
        speed_log_pointer += 1


# Iterate over merged cell log
for row_num in range(num_rows - 1):
    cell_log_row = pawprints_pd.iloc[row_num]


    # Get current heading, based on GPS of adjacent data points

    # If the GPS coordinates are the same, but speed > 0, then use speed to interpolate, based on the heading and difference between adjacent points


