import common, json, numpy
LOG_FOLDER = "../Data/"

GPS_TIME_LOG = "../Data/gps_abs_time.csv"
PAWPRINTS_TIME_LOG = "../Data/pawprints_abs_time.csv"

# Adjust GPS timestamps with offset. Create new file for synchronized GPS logs.
GPS_OFFSET = 0

# Get GPS start and end
gps_times = common.read_csv(GPS_TIME_LOG)
gps_times = numpy.array([(gps_time + GPS_OFFSET) for gps_time in gps_times])
gps_end = gps_times.max()
gps_start = gps_times.min()

# Get PawPrints start and end
pawprints_times = numpy.array(common.read_csv(PAWPRINTS_TIME_LOG))
pawprints_end = pawprints_times.max()
pawprints_start = pawprints_times.min()

# Overlap GPS and PawPrints
start_time = max(gps_start, pawprints_start)
end_time = min(gps_end, pawprints_end)

pawprints_start, pawprints_end = common.first_indices_greater_than(start_time, end_time, pawprints_times)
gps_start, gps_end = common.first_indices_greater_than(start_time, end_time, gps_times)

# Log the overlapped start and end times in a JSON file
common.write_file(LOG_FOLDER + "metadata.json", json.dumps({"start_time": start_time,
                                                            "end_time":end_time,
                                                            "pawprints_start_index": pawprints_start,
                                                            "pawprints_end_index":pawprints_end,
                                                            "gps_start_index":gps_start,
                                                            "gps_end_index":gps_end}))