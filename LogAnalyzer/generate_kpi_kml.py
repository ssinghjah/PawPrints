import common
import simplekml

LOG_FOLDER = "../Data/"
BS_PCI = "connected_bs"
KPI = "rsrq"

KPI_LOG_PATH = "../Data/" + BS_PCI + "_" + KPI + ".csv"
GPS_COORDS_LOG_PATH = "../Data/gps_raw.csv"
ALTITUDE_LOG_PATH = "../Data/gps_altitude.csv"

GPS_INDICES = "../Data/gps_interpolated_time_indices.csv"
KPI_INDICES = "../Data/connected_bs_interpolated_time_indices.csv"

LON_INDEX = 1
LAT_INDEX = 2
ALTITUDE_INDEX = 3

LINE_WIDTH = 3

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
    kpi = kpi_log[kpi_index]
    gps_coord = gps_coords[gps_index]
    gps_next_coord = gps_coords[gps_index+1]
    line = kml.newlinestring(coords=[(gps_coord[LON_INDEX], gps_coord[LAT_INDEX], gps_coord[ALTITUDE_INDEX]),(gps_next_coord[LON_INDEX], gps_next_coord[LAT_INDEX], gps_next_coord[ALTITUDE_INDEX])])
    line.altitudemode = simplekml.AltitudeMode.relativetoground
    color = common.value_to_color(kpi, kpi_min, kpi_max)
    kml_color = simplekml.Color.rgb(round(color["r"]*255), round(color["g"]*255), round(color["b"]*255))
    line.style.linestyle.color = kml_color
    line.style.linestyle.width = LINE_WIDTH

kml_fName = LOG_FOLDER + BS_PCI + "_" + KPI + ".kml"
kml.save(kml_fName)




