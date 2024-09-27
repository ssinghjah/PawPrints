import common
import os
from datetime import datetime

GPS_RAW_LOG = "../../ExperimentData/Aug_26_2023_Packapalooza/gps.csv"
OUTPUT_FOLDER = "../../ExperimentData/Aug_26_2023_Packapalooza/"
TIME_INDEX = 7
ALTITUDE_INDEX = 3
LAT_INDEX = 1
LON_INDEX = 2

def process_gps_log(gps_log_path=GPS_RAW_LOG, output_folder=OUTPUT_FOLDER):
    epoch_times = []
    altitudes = []
    latlons = []
    gps_log = common.read_csv(gps_log_path)
    for row in gps_log:
        str_time = row[TIME_INDEX]
        altitude = row[ALTITUDE_INDEX]
        latitude = row[LAT_INDEX]
        longitude = row[LON_INDEX]
        latlons.append([latitude, longitude])
        altitudes.append(altitude)
        # Convert to milliseconds since epoch
        epoch_time = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f')
        epoch_times.append(epoch_time.timestamp()*1000.0)
    common.write_csv(os.path.join(output_folder, "gps_coords.csv"), latlons)
    common.write_csv(os.path.join(output_folder, "gps_altitude.csv"), altitudes)
    common.write_csv(os.path.join(output_folder, "gps_abs_time.csv"), epoch_times)


if __name__ == "__main__":
    process_gps_log()
