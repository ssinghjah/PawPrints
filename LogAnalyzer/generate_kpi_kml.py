import common
import simplekml
import os
import argparse
import time_merger
import pandas as pd
import numpy as np

# Options
DEFAULT_PCI = "connected"
DEFAULT_KPI = "rsrp"
DEFAULT_KPI_UNITS = "dBm"
WORKFOLDER = "../../WorkArea/"
DEFAULT_GPS_PATH = os.path.join(WORKFOLDER, "gps.csv")
GPS_TIME_PATH = os.path.join(WORKFOLDER, "gps_abs_time.csv")
DEFAULT_MERGE_MODE = 2 # Merge mode. 0 = use a third reference time scale. 1 = use cellular.
DRAW_TYPE = "line, point"
LINE_WIDTH = 5
USE_PCI_MAP = False
MARKER_WIDTH = 2 

# Constants
METER_TO_DEGREE = 1/111320.0
COLOR_MAP = {1: {"r": 0, "g": 0.6, "b": 0} , 2: {"r": 1.0, "g": 0.6, "b": 0.0}}
LON_INDEX = 1
LAT_INDEX = 2
GPS_ALT_INDEX = 3
TIME_INDEX = 0

def generate_kml(options):
    kpi_path = os.path.join(WORKFOLDER, options.pci + "_" + options.kpi + ".csv")
    gps_path = DEFAULT_GPS_PATH
    
    kpi_times_path = os.path.join(WORKFOLDER, options.pci + "_abs_time.csv")
    kpi_times = common.read_csv(kpi_times_path)
    gps_times = common.read_csv(GPS_TIME_PATH)
    
    (kpi_indices, gps_indices) = time_merger.merge(kpi_times, gps_times, options.mergemode)
    
    kpi_log = common.read_csv(kpi_path)
    gps_log = common.read_csv(gps_path)

    print(len(kpi_log), len(kpi_indices), len(gps_indices))

    # Compare length
    if len(gps_indices) != len(kpi_indices):
        print("Error. Count of KPI Indices does not match that of GPS indices")
        exit

    # Iterate length-1 times
    numEntries = len(gps_indices)
    kml = simplekml.Kml()

    kpi_min = min(kpi_log)
    kpi_max = max(kpi_log)
    kpi_min = 200
    kpi_max = 600

    # Add a KML line segment with given coordinates. Calculate color as a function of the KPI. Add color to the line.
    for index in range(numEntries-1):
        kpi_index = kpi_indices[index]
        gps_index = gps_indices[index]
        kpi = kpi_log[kpi_index]

        if USE_PCI_MAP:
            if kpi in COLOR_MAP:
                color = COLOR_MAP[kpi]
            else:
                color = {"r": 0, "g": 0, "b": 0}
        else:
            color = common.value_to_color(kpi, kpi_min, kpi_max)

        kml_color = simplekml.Color.rgb(round(color["r"]*255), round(color["g"]*255), round(color["b"]*255))

        gps_coord = gps_log[gps_index]

        if "line" in DRAW_TYPE:
            gps_next_coord = gps_log[gps_index+1] if (gps_index + 1) < len(gps_times) else gps_log[gps_index]
            geom = kml.newlinestring(coords=[(gps_coord[LON_INDEX], gps_coord[LAT_INDEX], gps_coord[GPS_ALT_INDEX]),(gps_next_coord[LON_INDEX], gps_next_coord[LAT_INDEX], gps_next_coord[GPS_ALT_INDEX])])
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = LINE_WIDTH
            geom.description = f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({gps_coord[LAT_INDEX]},{gps_coord[LON_INDEX]})</p><p> altitude = {gps_coord[GPS_ALT_INDEX]} m</p>'
        

        if "point" in DRAW_TYPE:
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = [(gps_coord[LON_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[LAT_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]),
                                    (gps_coord[LON_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[LAT_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]), 
                                    (gps_coord[LON_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[LAT_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]),
                                    (gps_coord[LON_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[LAT_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]),
                                    (gps_coord[LON_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[LAT_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX])]
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({gps_coord[LAT_INDEX]},{gps_coord[LON_INDEX]})</p><p> altitude = {gps_coord[GPS_ALT_INDEX]} m</p>'



    kml_fName = os.path.join(WORKFOLDER, options.pci + "_" + options.kpi + ".kml")
    print("Number of data points: " + str(numEntries))
    print("Writing to " + str(kml_fName))
    kml.save(kml_fName)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate KML file of the specified KPI and cell PCI')
    parser.add_argument('-k', '--kpi', type=str, default = DEFAULT_KPI, help="KPI to plot. Default is " + DEFAULT_KPI )
    parser.add_argument('-p', '--pci', type = str, default = DEFAULT_PCI, help="PCI of the chosen cell. Default is " + DEFAULT_PCI)    
    parser.add_argument('-g', '--gps', type = str, default = DEFAULT_GPS_PATH, help="GPS log path. Default is " + DEFAULT_GPS_PATH)    
    parser.add_argument('-m', '--mergemode', type=int, default = DEFAULT_MERGE_MODE, help="Merge mode. 0 = use a third reference time scale. 1 = use cellular.")
    parser.add_argument('-u', '--kpi-units', type=str, default=DEFAULT_KPI_UNITS, help= "KPI units. Default is dBm, for RSRP.")
    options = parser.parse_args()
    generate_kml(options)
