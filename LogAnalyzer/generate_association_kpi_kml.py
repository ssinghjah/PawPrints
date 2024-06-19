import common
import simplekml
import os
import time_merger

KPI_LOG_PATH = "./WorkSpace/connected_rssi.csv"
PCI_LOG_PATH = "./WorkSpace/connected_pci.csv"
GPS_LOG_PATH = "./WorkSpace/gps.csv"
KPI_TIME_PATH = "./WorkSpace/connected_abs_time.csv"
GPS_TIME_PATH = "./WorkSpace/gps_abs_time.csv"
MERGE_MODE = 0

# GPS_INDICES = "./WorkSpace/Data/gps_merged_time_indices.csv"
# KPI_INDICES = "./WorkSpace/Data/cell_merged_time_indices.csv"

LON_INDEX = 1
LAT_INDEX = 2
ALTITUDE_INDEX = 3
WORKSPACE = "./WorkSpace/"
LINE_WIDTH = 3

PCI_MAP = {1: "YlGn", 2:"Oranges"}

kpi_log = common.read_csv(KPI_LOG_PATH)
pci_log = common.read_csv(PCI_LOG_PATH)
gps_coords = common.read_csv(GPS_LOG_PATH)

kpi_times = common.read_csv(KPI_TIME_PATH)
gps_times = common.read_csv(GPS_TIME_PATH)
(kpi_indices, gps_indices) = time_merger.merge(kpi_times, gps_times, MERGE_MODE)

# Compare length
if len(gps_indices) != len(kpi_indices):
    print("Error. Count of KPI Indices does not match that of GPS indices")
    exit

# Iterate length-1 times
numEntries = len(gps_indices)
kml = simplekml.Kml()

kpi_min = -75
kpi_max = -55

# Add a KML line segment with given coordinates. Calculate color as a function of the number. Add color to the line.
for index in range(numEntries-1):
    kpi_index = kpi_indices[index]
    gps_index = gps_indices[index]
    kpi = kpi_log[kpi_index]
    pci = pci_log[kpi_index]
    colormap = "gray"
    if pci in PCI_MAP:
        colormap = PCI_MAP[pci]
    gps_coord = gps_coords[gps_index]
    gps_next_coord = gps_coords[gps_index+1]
    line = kml.newlinestring(coords=[(gps_coord[LON_INDEX], gps_coord[LAT_INDEX], gps_coord[ALTITUDE_INDEX]),(gps_next_coord[LON_INDEX], gps_next_coord[LAT_INDEX], gps_next_coord[ALTITUDE_INDEX])])
    line.altitudemode = simplekml.AltitudeMode.relativetoground
    color = common.value_to_color(kpi, kpi_min, kpi_max, colormap=colormap)
    kml_color = simplekml.Color.rgb(round(color["r"]*255), round(color["g"]*255), round(color["b"]*255))
    line.style.linestyle.color = kml_color
    line.style.linestyle.width = LINE_WIDTH

kml_fName = os.path.join(WORKSPACE, "connected_rssi_pci.kml")
kml.save(kml_fName)
