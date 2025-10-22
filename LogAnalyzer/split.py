import pandas
import math
import os

def run(input, num_splits, output_folder, prefix):
    df = pandas.read_csv(input)
    chunk_size = math.ceil(len(df) / num_splits)
    for i in range(num_splits):
        df.iloc[i*chunk_size: (i+1)*chunk_size].to_csv(os.path.join(output_folder, prefix + "seg_" + str(i) + ".csv"), index=False)

if __name__ == "__main__":
    INPUT = "~/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/All/aerpaw-1_merged_interpolated.csv"
    NUM_SPLITS = 80
    PREFIX = "aerpaw-1_cellular_interpolated"

    OUTPUT_FOLDER = "~/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Split/Interpolated"
    run(INPUT, NUM_SPLITS, OUTPUT_FOLDER, PREFIX)
