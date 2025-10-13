import pandas

#-12523290 # -7076496 -12524069.802978516 
TIME_OFFSET_FLIGHT_2 = -12524653.4367676 # -12524653.4367676
TIME_OFFSET_FLIGHT_1 = -12525567.2441406 # 12525567.2441406

TIME_OFFSET = 0
TIME_COL = "nemo_abs_time"
OFFSET_TIME_COL = "companion_abs_time_ms"
RELATIVE_TIME_COL = "rel_time"
TIME_ZERO_FLIGHT_3 = 1719934641407.07
TIME_ZERO_FLIGHT_2 = 1719932234439.18
TIME_ZERO_FLIGHT_1 = 1719929186518.76
TIME_ZERO = TIME_ZERO_FLIGHT_2

to_offset_path = "../../../ExperimentData/July_2_2024_Flight_2/Nemo/iperf_processed.csv"
syncd_path = "../../../ExperimentData/July_2_2024_Flight_2/Nemo/iperf_processed_syncd.csv"
to_offset_df = pandas.read_csv(to_offset_path)
# to_offset_df[OFFSET_TIME_COL] = to_offset_df[TIME_COL] + TIME_OFFSET
to_offset_df[RELATIVE_TIME_COL] = to_offset_df[OFFSET_TIME_COL] - TIME_ZERO

to_offset_df.to_csv(syncd_path, index=False)
