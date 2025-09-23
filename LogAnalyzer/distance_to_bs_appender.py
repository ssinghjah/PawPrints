import pandas as pd
import common

BS_ANT_DELTA_ALT = 12 # Height in meters with respect to UAV take-off

BS_LOC = (35.727479, -78.695920, BS_ANT_DELTA_ALT)

LOG_PATH = "/home/simran/Work/AERPAW/AeroConf/Data/5G_all_nemo.csv"
df = pd.read_csv(LOG_PATH)
for index, row in df.iterrows():
    if not common.isNan(row["altitude"]) and not common.isNan(row["altitude"]) and not common.isNan(row["altitude"]):
        df.at[index, "bs_distance"] = common.lla_distance((row["latitude"], row["longitude"], row["altitude"]), BS_LOC)
    else:
        df.at[index, "bs_distance"] = None

df.to_csv(LOG_PATH, index=False)
