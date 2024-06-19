import numpy as np

import common
import os
import simplekml
import custom_color_maps

# Options
LOG_FOLDER = "../../WorkArea/"
BS_PCI = "connected_"
KPI = "pci"

KPI_LOG_PATH = os.path.join(LOG_FOLDER, BS_PCI + "_" + KPI + ".csv")
GPS_COORDS_LOG_PATH = os.path.join(LOG_FOLDER, "gps_raw.csv")
ALTITUDE_LOG_PATH = os.path.join(LOG_FOLDER, "gps_altitude.csv")

GPS_INDICES = os.path.join(LOG_FOLDER, "gps_interpolated_time_indices.csv")
KPI_INDICES = os.path.join(LOG_FOLDER, "connected_bs_interpolated_time_indices.csv")

LON_INDEX = 1
LAT_INDEX = 2
ALTITUDE_INDEX = 3

LINE_WIDTH = 7

kpi_log = common.read_csv(KPI_LOG_PATH)
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

kpi_min = min(kpi_log)
kpi_max = max(kpi_log)

# Add a KML line segment with given coordinates. Calculate color as a function of the number. Add color to the line.
for index in range(numEntries-1):
    kpi_index = kpi_indices[index]
    gps_index = gps_indices[index]
    pci = kpi_log[kpi_index]
    gps_coord = gps_coords[gps_index]
    gps_next_coord = gps_coords[gps_index+1]
    line = kml.newlinestring(coords=[(gps_coord[LON_INDEX], gps_coord[LAT_INDEX], gps_coord[ALTITUDE_INDEX]),(gps_next_coord[LON_INDEX], gps_next_coord[LAT_INDEX], gps_next_coord[ALTITUDE_INDEX])])
    line.altitudemode = simplekml.AltitudeMode.relativetoground
    # color = common.value_to_color(kpi, kpi_min, kpi_max)
    color = bs_colors.get_color(pci)
    color = common.hex_to_rgb(bs_colors.get_color(pci))
    # color = color_map[pci]
    kml_color = simplekml.Color.rgb(round(color["r"]*255.0), round(color["g"]*255.0), round(color["b"]*255.0))
    line.style.linestyle.color = kml_color
    line.style.linestyle.width = LINE_WIDTH

kml_fName = LOG_FOLDER + BS_PCI + "_" + KPI + ".kml"
kml.save(kml_fName)
