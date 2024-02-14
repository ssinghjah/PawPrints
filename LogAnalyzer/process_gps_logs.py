import common
import os
from datetime import datetime

GPS_RAW_LOG = "./WorkSpace/gps.csv"
OUTPUT_FOLDER = "./WorkSpace/Data"
TIME_INDEX = 7
ALTITUDE_INDEX = 3
LAT_INDEX = 1
LON_INDEX = 2
def process_gps_log():
    epoch_times = []
    altitudes = []
    latlons = []
    gps_log = common.read_csv(GPS_RAW_LOG)
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
    common.write_csv(os.path.join(OUTPUT_FOLDER, "gps_coords.csv"), latlons)
    common.write_csv(os.path.join(OUTPUT_FOLDER, "gps_altitude.csv"), altitudes)
    common.write_csv(os.path.join(OUTPUT_FOLDER, "gps_abs_time.csv"), epoch_times)

process_gps_log()
