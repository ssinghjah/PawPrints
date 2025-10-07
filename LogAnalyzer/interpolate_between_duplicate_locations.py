import pandas as pd
import sys
import argparse

SPEED_LOG = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/All/aerpaw-1_motion.csv"
PAWPRINTS_LOG = "/home/simran/Work/AERPAW/RadioDemographics/data/analysis/radio_kpis_all_no_duplicates.csv"
PAWPRINTS_OUTPUT_LOG = "/home/simran/Work/AERPAW/RadioDemographics/data/analysis/radio_kpis_all_no_duplicates_interp.csv"
speed_log_pointer = 0
SPEED_THRESHOLD = 5
TIME_THRESHOLD = 1000

def run():
    pawprints_pd = pd.read_csv(PAWPRINTS_LOG)
    num_rows = len(pawprints_pd)
    LATITUDE_LOC = pawprints_pd.columns.get_loc("latitude")
    LONGITUDE_LOC = pawprints_pd.columns.get_loc("longitude")
    ALTITUDE_LOC = pawprints_pd.columns.get_loc("altitude")

    speed_pd = pd.read_csv(SPEED_LOG)
    speed_pd["phone_abs_time"] = speed_pd["abs_time"]
    speed_pd = speed_pd.set_index('abs_time')

    # Iterate over merged cell log
    sync_and_moving_counter = 0
    interpolated_pd = []
    for row_num in range(num_rows - 1):
        sys.stdout.write("\r" + str(row_num) + "/" + str(num_rows))
        cell_log_row = pawprints_pd.iloc[row_num]
        cell_log_row_next = pawprints_pd.iloc[row_num + 1]
        if (cell_log_row["phone_abs_time"] == cell_log_row_next["phone_abs_time"]):
            continue
        # Get current heading, based on GPS of adjacent data points
        # If the GPS coordinates are the same, but speed > 0, then use speed to interpolate, based on the heading and difference between adjacent points
        if((cell_log_row["latitude"] == cell_log_row_next["latitude"]) and (cell_log_row["longitude"] == cell_log_row_next["longitude"]) and (cell_log_row["altitude"] == cell_log_row_next["altitude"])):
            bsyncd, bmoving = fix_location(cell_log_row, speed_pd)
            if bsyncd and bmoving:
                heading_offset = get_next_diff_pos(row_num, pawprints_pd)
                t_diff = pawprints_pd.iloc[row_num + heading_offset]["phone_abs_time"] - cell_log_row["phone_abs_time"]
                interpolated_pos = adjust_position(cell_log_row, cell_log_row["phone_abs_time"], cell_log_row_next["phone_abs_time"], pawprints_pd.iloc[row_num + heading_offset]["phone_abs_time"], pawprints_pd.iloc[row_num + heading_offset])
                pawprints_pd.iloc[row_num + 1, LATITUDE_LOC] = interpolated_pos["latitude"]
                pawprints_pd.iloc[row_num + 1, LONGITUDE_LOC] = interpolated_pos["longitude"]
                pawprints_pd.iloc[row_num + 1, ALTITUDE_LOC] =  interpolated_pos["altitude"]
                sync_and_moving_counter += 1

    sys.stdout.write("\n. Same locations but speed > 0 =" + str(sync_and_moving_counter) + "/" + str(num_rows))
    pawprints_pd.to_csv(PAWPRINTS_OUTPUT_LOG, index=False)
  
def fix_location(cell_log_row, speed_pd):
        bMoving = False
        bSyncd = False
        time_now = cell_log_row["phone_abs_time"]
        speed_index = speed_pd.index.get_indexer([time_now], method="nearest")[0]
        t_difference = speed_pd.iloc[speed_index]["phone_abs_time"] - cell_log_row["phone_abs_time"]
        speed = speed_pd.iloc[speed_index]["speed_mph"]
        bMoving = speed > SPEED_THRESHOLD 
        bSyncd = t_difference < TIME_THRESHOLD
        return bSyncd, bMoving

def get_next_diff_pos(curr_row_num, df):
        offset = 0
        while (curr_row_num + offset <  len(df) - 1 and df.iloc[curr_row_num]["latitude"] == df.iloc[curr_row_num + offset]["latitude"] and df.iloc[curr_row_num]["longitude"] == df.iloc[curr_row_num + offset]["longitude"] and df.iloc[curr_row_num]["altitude"] == df.iloc[curr_row_num + offset]["altitude"]):
            offset += 1
        return offset

def adjust_position(start_pos, t_start, t_interpolate, t_end, end_pos):
        interpolated_pos = {}
        interp_ratio = (t_interpolate - t_start) / (t_end - t_start) 
        interpolated_pos["latitude"] = start_pos["latitude"] + (end_pos["latitude"] - start_pos["latitude"])* interp_ratio
        interpolated_pos["longitude"] = start_pos["longitude"] + (end_pos["longitude"] - start_pos["longitude"])* interp_ratio
        interpolated_pos["altitude"] = start_pos["altitude"] + (end_pos["altitude"] - start_pos["altitude"])* interp_ratio
        return interpolated_pos

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i","--radio-log", type=str, default=PAWPRINTS_LOG, required=True)
    argParser.add_argument("-o","--output", type=str, default=PAWPRINTS_OUTPUT_LOG, required=True)
    argParser.add_argument("-s","--speed-log", type=str, default=SPEED_LOG, required=True)

    # options = argParser.parse_args()
    # PAWPRINTS_LOG = options.radio_log
    # PAWPRINTS_OUTPUT_LOG = options.output
    # SPEED_LOG = options.speed_log
    run()
