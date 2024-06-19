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
DEFAULT_KPI_UNITS = ""
DEFAULT_WORKFOLDER = ""
DEFAULT_LOG_NAME = "pawprints_all.csv"

DEFAULT_LOG_TYPE = "all" # can be "per-cell-kpi" or "all"
DEFAULT_MERGE_MODE = 1 # Merge mode. 0 = use a third reference time scale. 1 = use cellular. 2 = use gps
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

DEFAULT_OUTPUT_KML = "output.kml"

def generate_kml(options):
    numEntries = -1
    kpi_log = []
    gps_log = []
    if options.log_type == "per-cell-kpi":
        kpi_path = os.path.join(options.workarea, options.pci + "_" + options.kpi + ".csv")
        gps_path = os.path.join(options.workarea, "gps.csv")
        gps_time_path = os.path.join(options.workarea, "gps_abs_time.csv")
        
        kpi_times_path = os.path.join(options.workarea, options.pci + "_abs_time.csv")
        kpi_times = common.read_csv(kpi_times_path)
        gps_times = common.read_csv(gps_time_path)
        
        (kpi_indices, gps_indices) = time_merger.merge(kpi_times, gps_times, options.merge_mode)
        
        kpi_log = common.read_csv(kpi_path)
        gps_log = common.read_csv(gps_path)

        print(len(kpi_log), len(kpi_indices), len(gps_indices))

         # Compare length
        if len(gps_indices) != len(kpi_indices):
            print("Error. Count of KPI Indices does not match that of GPS indices")
            exit

        # Iterate length-1 times
        numEntries = len(gps_indices)

    elif options.log_type == "all":
        log_path = os.path.join(options.workarea, options.input_log)
        log_pd = pd.read_csv(log_path)
        
        # Filter by PCI
        if options.pci == "connected" and "is_connected" in log_pd.columns:
            # Filter rows of the connected cell
            indices = log_pd["is_connected"] == 1
            kpi_gps_pd = log_pd.loc[indices][["latitude", "longitude", "altitude", options.kpi]]
        else:
            # Expect latitude, longitude, and altitude to be present in the merged csv
            kpi_gps_pd = log_pd
            print(kpi_gps_pd)

        kpi_indices = np.arange(numEntries)
        gps_indices = np.arange(numEntries)

    else:
        print("Invalid log type.")
        return
    
    kml = simplekml.Kml()

    kpi_min = min(kpi_gps_pd[options.kpi]) if options.kpi_min == None else options.kpi_min
    kpi_max = max(kpi_gps_pd[options.kpi]) if options.kpi_max == None else options.kpi_max
    numRows = len(kpi_gps_pd)

    for i in range(numRows):
        lat = kpi_gps_pd.iloc[i]["latitude"]
        lon = kpi_gps_pd.iloc[i]["longitude"]
        alt = kpi_gps_pd.iloc[i]["altitude"]
        kpi = kpi_gps_pd.iloc[i][options.kpi]

        if options.use_pci_colormap:
            if kpi in COLOR_MAP:
                color = COLOR_MAP[kpi]
            else:
                color = {"r": 0, "g": 0, "b": 0}
        else:
            color = common.value_to_color(kpi, kpi_min, kpi_max)

        kml_color = simplekml.Color.rgb(round(color["r"]*255), round(color["g"]*255), round(color["b"]*255))


        if "line" in DRAW_TYPE:
            if i == numRows - 1:
                break
            else:
                next_index = i + 1
                geom = kml.newlinestring(coords=[(lon, lat, alt), (kpi_gps_pd.iloc[i+1]["longitude"], kpi_gps_pd.iloc[i+1]["latitude"], kpi_gps_pd.iloc[i+1]["altitude"])])
                geom.altitudemode = simplekml.AltitudeMode.relativetoground
                geom.style.linestyle.color = kml_color
                geom.style.linestyle.width = LINE_WIDTH
                geom.description = f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'
        
        if "point" in DRAW_TYPE:
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = [(lon - 0.5*MARKER_WIDTH*METER_TO_DEGREE, lat - 0.5*MARKER_WIDTH*METER_TO_DEGREE, alt),
                                    (lon+ 0.5*MARKER_WIDTH*METER_TO_DEGREE, lat - 0.5*MARKER_WIDTH*METER_TO_DEGREE, alt), 
                                    (lon + 0.5*MARKER_WIDTH*METER_TO_DEGREE, lat + 0.5*MARKER_WIDTH*METER_TO_DEGREE, alt),
                                    (lon - 0.5*MARKER_WIDTH*METER_TO_DEGREE, lat + 0.5*MARKER_WIDTH*METER_TO_DEGREE, alt),
                                    (lon - 0.5*MARKER_WIDTH*METER_TO_DEGREE, lat - 0.5*MARKER_WIDTH*METER_TO_DEGREE, alt)]
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'

    if options.output_log:
        kml_fName = os.path.join(options.workarea, options.output_log)
    else:
        kml_fName = os.path.join(options.workarea, options.pci + "_" + options.kpi + ".kml")
    
    print("Number of data points: " + str(numRows))
    print("Writing to " + str(kml_fName))
    kml.save(kml_fName)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate KML file of the specified KPI and cell PCI')
    parser.add_argument('-t', '--log-type', type=str, default = DEFAULT_LOG_TYPE, help="Log type. Can be 'all' or 'per-cell-kpi'. Default is " + DEFAULT_LOG_TYPE)
    parser.add_argument('-i', '--input-log', type=str, default = DEFAULT_LOG_NAME, help="Merged log name. Default is " + DEFAULT_LOG_NAME)
    parser.add_argument('-g', '--gps-log', type=str, default = None, help="GPS log file. Optional")
    parser.add_argument('-o', '--output-log', type=str, default = None, help="Output kml file. Default is the name of the KPI")
    parser.add_argument('-k', '--kpi', type=str, default = DEFAULT_KPI, help="KPI to plot. Default is " + DEFAULT_KPI )
    parser.add_argument('--kpi-min', type=float, default = None, help="Minimum value of the KPI color bar. Default is minimum of all KPIs.")
    parser.add_argument('--kpi-max', type=float, default = None, help="Maximum value of the KPI color bar. Default is maximum of all KPIs.")
    parser.add_argument('-p', '--pci', type = str, default = DEFAULT_PCI, help="PCI of the chosen cell. Default is " + DEFAULT_PCI)    
    parser.add_argument('--use-pci-colormap', action="store_true", help="Specifies whether to use a provided PCI color map.")
    parser.add_argument('-w', '--workarea', type = str, default = DEFAULT_WORKFOLDER, help="Workarea path, containing radio, vehicle and traffic logs. Default is " + DEFAULT_WORKFOLDER)    
    parser.add_argument('-m', '--merge-mode', type=int, default = DEFAULT_MERGE_MODE, help="Merge mode. 0 = use a third reference time scale. 1 = use cellular.")
    parser.add_argument('-u', '--kpi-units', type=str, default=DEFAULT_KPI_UNITS, help= "KPI units. Default is dBm, for RSRP.")
    options = parser.parse_args()
    generate_kml(options)
