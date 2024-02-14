import common
import simplekml
import os

# Options
BS_PCI = "connected"
KPI = "rsrq"
LINE_WIDTH = 3
USE_PCI_MAP = False

# Constants
KPI_LOG_PATH = "./WorkSpace/Data/" + BS_PCI + "_" + KPI + ".csv"
GPS_LOG_PATH = "./WorkSpace/Data/gps.csv"
GPS_INDICES = "./WorkSpace/Data/gps_merged_time_indices.csv"
KPI_INDICES = "./WorkSpace/Data/cell_merged_time_indices.csv"
LON_INDEX = 1
LAT_INDEX = 2
ALTITUDE_INDEX = 3
WORKSPACE = "./WorkSpace/"

kpi_log = common.read_csv(KPI_LOG_PATH)
gps_coords = common.read_csv(GPS_LOG_PATH)

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

color_map = {1: {"r": 0, "g": 0.6, "b": 0} , 2: {"r": 1.0, "g": 0.6, "b": 0.0}}

# Add a KML line segment with given coordinates. Calculate color as a function of the KPI. Add color to the line.
for index in range(numEntries-1):
    kpi_index = kpi_indices[index]
    gps_index = gps_indices[index]
    kpi = kpi_log[kpi_index]
    gps_coord = gps_coords[gps_index]
    gps_next_coord = gps_coords[gps_index+1]
    line = kml.newlinestring(coords=[(gps_coord[LON_INDEX], gps_coord[LAT_INDEX], gps_coord[ALTITUDE_INDEX]),(gps_next_coord[LON_INDEX], gps_next_coord[LAT_INDEX], gps_next_coord[ALTITUDE_INDEX])])
    line.altitudemode = simplekml.AltitudeMode.relativetoground
    if USE_PCI_MAP:
        if kpi in color_map:
            color = color_map[kpi]
        else:
            color = {"r": 0, "g": 0, "b": 0}
    else:
        color = common.value_to_color(kpi, kpi_min, kpi_max)
    kml_color = simplekml.Color.rgb(round(color["r"]*255), round(color["g"]*255), round(color["b"]*255))
    line.style.linestyle.color = kml_color
    line.style.linestyle.width = LINE_WIDTH

kml_fName = os.path.join(WORKSPACE, BS_PCI + "_" + KPI + ".kml")
kml.save(kml_fName)
