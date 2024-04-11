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
WORKFOLDER = "../../WorkArea/"
DEFAULT_GPS_PATH = os.path.join(WORKFOLDER, "gps.csv")
GPS_TIME_PATH = os.path.join(WORKFOLDER, "gps_abs_time.csv")
MERGE_MODE = 2 # Merge mode. 0 = use a third reference time scale. 1 = use cellular.
DRAW_TYPE = "point"
LINE_WIDTH = 3
USE_PCI_MAP = True
MARKER_WIDTH = 1 

# Constants
METER_TO_DEGREE = 1/111320.0
COLOR_MAP = {1: {"r": 0, "g": 0.6, "b": 0} , 2: {"r": 1.0, "g": 0.6, "b": 0.0}}
GPS_LON_INDEX = 1
GPS_LAT_INDEX = 2
GPS_ALT_INDEX = 3
GPS_TIME_INDEX = 0

def generate_kml(options):
    kpi_path = os.path.join(WORKFOLDER, options.pci + "_" + options.kpi + ".csv")
    gps_path = DEFAULT_GPS_PATH
    
    kpi_times_path = os.path.join(WORKFOLDER, options.pci + "_abs_time.csv")
    kpi_times = common.read_csv(kpi_times_path)
    gps_times = common.read_csv(GPS_TIME_PATH)
    
    (kpi_indices, gps_indices) = time_merger.merge(kpi_times, gps_times, MERGE_MODE)
    
    kpi_log = common.read_csv(kpi_path)
    gps_log = common.read_csv(gps_path)

    # Compare length
    if len(gps_indices) != len(kpi_indices):
        print("Error. Count of KPI Indices does not match that of GPS indices")
        exit

    # Iterate length-1 times
    numEntries = len(gps_indices)
    kml = simplekml.Kml()

    kpi_min = min(kpi_log)
    kpi_max = max(kpi_log)
    kpi_min = -98
    kpi_max = -75

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
        if DRAW_TYPE == "line":
            gps_next_coord = gps_log[gps_index+1] if (gps_index + 1) < len(gps_times) else gps_log[gps_index]
            geom = kml.newlinestring(coords=[(gps_coord[GPS_LON_INDEX], gps_coord[GPS_LAT_INDEX], gps_coord[GPS_ALT_INDEX]),(gps_next_coord[GPS_LON_INDEX], gps_next_coord[GPS_LAT_INDEX], gps_next_coord[GPS_ALT_INDEX])])
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = LINE_WIDTH

        elif DRAW_TYPE == "point":
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = [(gps_coord[GPS_LON_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_LAT_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]),
                                    (gps_coord[GPS_LON_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_LAT_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]), 
                                    (gps_coord[GPS_LON_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_LAT_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]),
                                    (gps_coord[GPS_LON_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_LAT_INDEX] + 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX]),
                                    (gps_coord[GPS_LON_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_LAT_INDEX] - 0.5*MARKER_WIDTH*METER_TO_DEGREE, gps_coord[GPS_ALT_INDEX])]
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = LINE_WIDTH

    kml_fName = os.path.join(WORKFOLDER, options.pci + "_" + options.kpi + ".kml")
    print("Number of data points: " + str(numEntries))
    print("Writing to " + str(kml_fName))
    kml.save(kml_fName)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate KML file of the specified KPI and cell PCI')
    parser.add_argument('-k', '--kpi', type=str, default = DEFAULT_KPI, help="KPI to plot. Default is " + DEFAULT_KPI )
    parser.add_argument('-p', '--pci', type = str, default = DEFAULT_PCI, help="PCI of the chosen cell. Default is " + DEFAULT_PCI)    
    parser.add_argument('-g', '--gps', type = str, default = DEFAULT_GPS_PATH, help="GPS log path. Default is " + DEFAULT_GPS_PATH)    
    parser.add_argument('-m', '--mergemode', type=int, default = 0, help="Merge mode. 0 = use a third reference time scale. 1 = use cellular.")
    options = parser.parse_args()
    generate_kml(options)
