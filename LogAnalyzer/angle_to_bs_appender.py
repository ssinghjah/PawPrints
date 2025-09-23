import pandas as pd
import common
import os
import math

BS_ANT_DELTA_ALT = 12 # Height in meters with respect to UAV take-off
BS_LOC = (35.727480, -78.695920, BS_ANT_DELTA_ALT)

MODE = "file"
LOG_PATH = "/home/simran/Work/AERPAW/AeroConf/Data/5G_all_nemo.csv"

def process(log_path):    
    df = pd.read_csv(log_path)
    for index, row in df.iterrows():
        if not common.isNan(row["altitude"]) and not common.isNan(row["altitude"]) and not common.isNan(row["altitude"]):
            bearing_wrt_bs = common.calculate_bearing(BS_LOC[0], BS_LOC[1], row["latitude"], row["longitude"])
            elevation_wrt_bs = common.calculate_elevation(BS_LOC[0], BS_LOC[1], BS_LOC[2], row["latitude"], row["longitude"], row["altitude"])
            df.at[index, "bs_bearing"] = bearing_wrt_bs
            df.at[index, "bs_elevation"] = elevation_wrt_bs
            print(bearing_wrt_bs, elevation_wrt_bs)
        else:
            df.at[index, "bs_distance"] = None
    df.to_csv(log_path, index=False)
    

if MODE == "folder":
    files = os.listdir(LOG_PATH)
    for file_to_process in files:
        if file_to_process.endswith(".csv"):
            log_path = os.path.join(LOG_PATH, file_to_process)
            process(log_path)
elif MODE == "file":
    process(LOG_PATH)
    

