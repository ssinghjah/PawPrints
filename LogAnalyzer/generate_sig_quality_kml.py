import numpy as np

import common
import simplekml
import custom_color_maps

LOG_FOLDER = "../Data/"
BS_PCI = "connected_bs"

RSRP_LOG_PATH = "../Data/" + BS_PCI + "_rsrp.csv"
RSRQ_LOG_PATH = "../Data/" + BS_PCI + "_rsrq.csv"
GPS_COORDS_LOG_PATH = "../Data/gps_raw.csv"
ALTITUDE_LOG_PATH = "../Data/gps_altitude.csv"

GPS_INDICES = "../Data/gps_interpolated_time_indices.csv"
KPI_INDICES = "../Data/connected_bs_interpolated_time_indices.csv"

LON_INDEX = 1
LAT_INDEX = 2
ALTITUDE_INDEX = 3

LINE_WIDTH = 5

rsrp_log = common.read_csv(RSRP_LOG_PATH)
rsrq_log = common.read_csv(RSRQ_LOG_PATH)

gps_coords = common.read_csv(GPS_COORDS_LOG_PATH)
gps_altitude = common.read_csv(ALTITUDE_LOG_PATH)

gps_indices = common.read_csv(GPS_INDICES)
kpi_indices = common.read_csv(KPI_INDICES)

# Compare length
if len(gps_indices) != len(kpi_indices):
    print("Error. Count of KPI Indices does not match that of GPS indices")
    exit

# Iterate length-1 times
numEntries = len(gps_indices)
kml = simplekml.Kml()

# Add a KML line segment with given coordinates. Calculate color as a function of the number. Add color to the line.
for index in range(numEntries-1):
    kpi_index = kpi_indices[index]
    gps_index = gps_indices[index]

    gps_coord = gps_coords[gps_index]
    gps_next_coord = gps_coords[gps_index+1]

    rsrq = rsrq_log[kpi_index]
    rsrp = rsrp_log[kpi_index]
    rsrq_qual = common.rsrq_to_quality(rsrq)
    rsrp_qual = common.rsrp_to_quality(rsrp)
    color = custom_color_maps.get_sig_qual_color(rsrp_qual, rsrq_qual)

    line = kml.newlinestring(coords=[(gps_coord[LON_INDEX], gps_coord[LAT_INDEX], gps_coord[ALTITUDE_INDEX]),(gps_next_coord[LON_INDEX], gps_next_coord[LAT_INDEX], gps_next_coord[ALTITUDE_INDEX])])
    line.altitudemode = simplekml.AltitudeMode.relativetoground

    kml_color = simplekml.Color.rgb(round(color["r"]*255.0), round(color["g"]*255.0), round(color["b"]*255.0))
    line.style.linestyle.color = kml_color
    line.style.linestyle.width = LINE_WIDTH

kml_fName = LOG_FOLDER + BS_PCI + "_sig_quality.kml"
kml.save(kml_fName)