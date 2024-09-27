import common
import pandas
import json
import argparse

def run(options):
    gps_data = []
    with open(options.input, "r") as fp:
        lines = fp.readlines()
        for line in lines:
            line_obj = json.loads(line)
            gps_data.append(line_obj)
    
    gps_df = pandas.DataFrame(gps_data)
    gps_df = gps_df.sort_values("abs_time")
    gps_df["time_readable"] = gps_df["abs_time"].apply(common.epoch_ms_to_readable) 
    if "speed" in gps_df.columns:
        gps_df["speed_mph"] = gps_df["speed"]*2.23694

    gps_df.to_csv(options.output, index=False)

INPUT_PATH = "/home/simran/Work/Logs_AWS/AERPAW-1_motion.jsonl"
OUTPUT_PATH = "/home/simran/Work/Logs_AWS/aerpaw-1_motion.csv"
# df = run(PATH)
# df.to_csv(OUTPUT, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert PawPrints GPS log into .csv.')    
    parser.add_argument('-i', '--input', type = str, default = INPUT_PATH, help='Input pawprints gps log file')
    parser.add_argument('-o', '--output', type = str, default = OUTPUT_PATH, help='Output gps csv path.')
    options = parser.parse_args()
    run(options)

