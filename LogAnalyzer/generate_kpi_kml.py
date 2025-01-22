import warnings
warnings.filterwarnings("ignore")
import common
import simplekml
import os
import argparse
import time_merger
import pandas as pd
import math
import numpy as np

# Options
# DEFAULT_PCI = "connected"
DEFAULT_PCI = "connected"
DEFAULT_KPI = "rsrp"
DEFAULT_KPI_UNITS = ""
DEFAULT_WORKFOLDER = ""
DEFAULT_LOG_NAME = "pawprints_all.csv"
DEFAULT_PCI_COL_NAME = "pci"
DEFAULT_ALT_COL = "altitude"

DEFAULT_LOG_TYPE = "all" # can be "per-cell-kpi" or "all"
DEFAULT_MERGE_MODE = 1 # Merge mode. 0 = use a third reference time scale. 1 = use cellular. 2 = use gps
DRAW_TYPE = "line, point"
LINE_WIDTH = 1 
USE_PCI_MAP = False
MARKER_WIDTH = 8
DIRECTED_MARKER_LENGTH = 5
DIRECTED_MARKER_SCALE = 1.0

# Constants
METER_TO_DEGREE = 1/111320.0

COLOR_MAP = {1: {"r": 0, "g": 0.6, "b": 0} , 2: {"r": 1.0, "g": 0.6, "b": 0.0}}
LON_INDEX = 1
LAT_INDEX = 2
GPS_ALT_INDEX = 3
TIME_INDEX = 0

DEFAULT_OUTPUT_KML = "output.kml"

def add_labels(row,  labels, label_units, custom_label):
    description = ""
    description += f'<p><strong>{custom_label}</strong></p>'

    if len(label_units) != len(labels):
        raise Exception("Length of label units should be equal to length of labels.")
    
    for label,label_unit in zip(labels, label_units):
        description += f'<p>{label} = {row[label]} {label_unit}</p>'

    return description

def _create_kml_circle(latitude, longitude, altitude, radius_meters):
    # Create a Placemark for the circle
    pts = []
    for angle in range(0, 360, 1):  # Create points for the circle
        x = radius_meters * math.cos(math.radians(angle))
        y = radius_meters * math.sin(math.radians(angle))
        pts += [(longitude + x*METER_TO_DEGREE, latitude + y*METER_TO_DEGREE, altitude)]  # Convert feet to degrees
    pts.append(pts[0])
    return(pts)

def _create_kml_polygon(latitude, longitude, altitude, radius_meters, num_sides):
    pts = []
    for angle in range(0, 360, int(360/num_sides)): 
        x = radius_meters * math.cos(math.radians(angle))
        y = radius_meters * math.sin(math.radians(angle))
        pts += [(longitude + x*METER_TO_DEGREE, latitude + y*METER_TO_DEGREE, altitude)]  
    pts.append(pts[0])
    return(pts)

def _create_kml_rect_triangle(curr_pt, next_pt):
    pts = []
    
    curr_pt_ecef = common.lla_to_ecef(curr_pt)
    nxt_pt_ecef = common.lla_to_ecef(next_pt)

    trans_vec = common.create_3D_vec(curr_pt_ecef, nxt_pt_ecef, normalize=True)
    dist = common.point_dist_3D(curr_pt_ecef, nxt_pt_ecef)
    rot_vec = [trans_vec[1], -trans_vec[0], 0]

    rect_mid_left = common.move_ecef_point_along_vec(curr_pt_ecef, rot_vec, 4)
    rect_mid_right = common.move_ecef_point_along_vec(curr_pt_ecef, rot_vec, -4)

    rect_start_left = common.move_ecef_point_along_vec(rect_mid_left, trans_vec, DIRECTED_MARKER_LENGTH/4.0)
    rect_start_right = common.move_ecef_point_along_vec(rect_mid_right, trans_vec, -DIRECTED_MARKER_LENGTH/4.0)

    rect_end_left = common.move_ecef_point_along_vec(rect_mid_left, trans_vec, DIRECTED_MARKER_LENGTH/4.0)
    rect_end_right = common.move_ecef_point_along_vec(rect_mid_right, trans_vec, DIRECTED_MARKER_LENGTH/4.0)

    tip = common.move_ecef_point_along_vec(curr_pt_ecef, )

    pts.append(common.flip_lat_lon(common.ecef_to_lla(rect_start_left)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(rect_end_left)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(nxt_pt_ecef)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(rect_end_right)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(rect_start_right)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(rect_start_left)))
    return(pts)

def _create_kml_triangle(curr_pt, next_pt):
    pts = []
    
    curr_pt_ecef = common.lla_to_ecef(curr_pt)
    nxt_pt_ecef = common.lla_to_ecef(next_pt)

    trans_vec = common.create_3D_vec(curr_pt_ecef, nxt_pt_ecef, normalize=True)
    dist = common.point_dist_3D(curr_pt_ecef, nxt_pt_ecef)
    rot_vec = [trans_vec[1], -trans_vec[0], 0]

    tri_left = common.move_ecef_point_along_vec(curr_pt_ecef, rot_vec, 4)
    tri_right = common.move_ecef_point_along_vec(curr_pt_ecef, rot_vec, -4)

    pts.append(common.flip_lat_lon(common.ecef_to_lla(tri_left)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(nxt_pt_ecef)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(tri_right)))
    pts.append(common.flip_lat_lon(common.ecef_to_lla(tri_left)))
    return(pts)

# -i ~/Work/AERPAW/ExperimentData/July_2_2024_Flight_3/PawPrints/pawprints_all.csv -k rsrp --draw-type triangle --pci connected --custom-label PawPrints -u dBm --kpi-min -90 --kpi-max -60

def generate_kml(options, additional_filters = None):
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
        log_pd["altitude"] = log_pd[options.alt_col]
        
        columns = ["latitude", "longitude", "altitude", options.kpi]
        columns.extend(options.labels)
        
        if "directed" in options.draw_type:
            columns.extend(["roll", "pitch", "yaw", "vx", "vy", "vz"])

        # Filter by PCI
        if options.pci == "connected" and "is_connected" in log_pd.columns:
            # Filter rows of the connected cell
            indices = log_pd["is_connected"] == 1
            kpi_gps_pd = log_pd.loc[indices][columns]
        elif options.pci:
            # Expect latitude, longitude, and altitude to be present in the merged csv
            pci_col = "pci"
            if options.pci_col:
                pci_col = options.pci_col
            indices = log_pd[options.pci_col] == int(options.pci)
            kpi_gps_pd = log_pd.loc[indices][columns]
        else:
            kpi_gps_pd = log_pd[columns]
            kpi_gps_pd = kpi_gps_pd.dropna(subset=[options.kpi])
            print(kpi_gps_pd)

        kpi_indices = np.arange(numEntries)
        gps_indices = np.arange(numEntries)

    else:
        print("Invalid log type.")
        return
    
    kml = simplekml.Kml()

    kpi_min = min(kpi_gps_pd[options.kpi]) if options.kpi_min == None else options.kpi_min
    kpi_max = max(kpi_gps_pd[options.kpi]) if options.kpi_max == None else options.kpi_max
    print(kpi_min, kpi_max)
    if kpi_min == kpi_max:
        kpi_min = kpi_max - 1
    numRows = len(kpi_gps_pd)

    for i in range(numRows):
        lat = kpi_gps_pd.iloc[i]["latitude"]
        lon = kpi_gps_pd.iloc[i]["longitude"]
        alt = kpi_gps_pd.iloc[i]["altitude"]
        kpi = kpi_gps_pd.iloc[i][options.kpi]
        if common.isNan(kpi) or common.isNan(lat) or common.isNan(lon) or common.isNan(alt):
            continue

        if options.use_pci_colormap:
            if kpi in COLOR_MAP:
                color = COLOR_MAP[kpi]
            else:
                color = {"r": 0, "g": 0, "b": 0}
        else:
            color = common.value_to_color(kpi, kpi_min, kpi_max)

        

        kml_color = simplekml.Color.rgb(round(color["r"]*255), round(color["g"]*255), round(color["b"]*255))

        if "line" in options.draw_type:
            if i == numRows - 1:
                break
            else:
                next_index = i + 1
                geom = kml.newlinestring(coords=[(lon, lat, alt), (kpi_gps_pd.iloc[i+1]["longitude"], kpi_gps_pd.iloc[i+1]["latitude"], kpi_gps_pd.iloc[i+1]["altitude"])])
                geom.altitudemode = simplekml.AltitudeMode.relativetoground
                geom.style.linestyle.color = kml_color
                geom.style.linestyle.width = LINE_WIDTH
                geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
                geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'


        if "point" in options.draw_type:
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
            geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
            geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'

        if "circle" in options.draw_type:
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = _create_kml_circle(lat, lon, alt, MARKER_WIDTH)
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
            geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'

        if "directed" in options.draw_type:
            yaw = kpi_gps_pd.iloc[i]["yaw"]
            pitch = kpi_gps_pd.iloc[i]["pitch"]
            roll = kpi_gps_pd.iloc[i]["roll"]
            vx = kpi_gps_pd.iloc[i]["vx"]
            vy = kpi_gps_pd.iloc[i]["vy"]
            vz = kpi_gps_pd.iloc[i]["vz"]

            center = (lat, lon, alt)

            poly_rear, poly_front = common.create_ref_directed_poly(center, 25, roll = roll, pitch = pitch, yaw = yaw, split=True)     
            poly_rear = common.flip_lat_lon_poly(poly_rear)
            poly_front = common.flip_lat_lon_poly(poly_front)

            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = poly_rear
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
            geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p><p>yaw = {round(yaw*180/math.pi,2)} ° </p><p> pitch = {round(pitch*180/math.pi,2)} °</p> <p> roll = {round(roll*180/math.pi,2)} °</p><p> v_north = {round(vx,2) } m/s</p><p> v_east = {round(vy,2) } m/s</p><p> v_down = {round(vz,2) } m/s</p>'

            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = poly_front
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
            geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p><p>yaw = {round(yaw*180/math.pi,2)} ° </p><p> pitch = {round(pitch*180/math.pi,2)} °</p> <p> roll = {round(roll*180/math.pi,2)} °</p><p> v_north = {round(vx,2) } m/s</p><p> v_east = {round(vy,2) } m/s</p><p> v_down = {round(vz,2) } m/s</p>'            
            
            geom = kml.newlinestring(coords=[(lon, lat, alt+5), (lon, lat, alt+5-vz*METER_TO_DEGREE)])
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = LINE_WIDTH

            eom = kml.newlinestring(coords=[(lon, lat, alt+5), (lon, lat+vx*METER_TO_DEGREE, alt+5)])
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.style.linestyle.color = kml_color/home/simran/Downloads/waste_gen_prediction.py
            geom.style.linestyle.width = LINE_WIDTH

            eom = kml.newlinestring(coords=[(lon, lat, alt+5), (lon+vy*METER_TO_DEGREE, lat, alt+5)])
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = LINE_WIDTH



        if "project" in options.draw_type:
            geom = kml.newlinestring(coords=[(lon, lat, alt), (lon, lat, 0)])
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = LINE_WIDTH

        if "triangle" in options.draw_type:
            if len(kpi_gps_pd) == i+1:
                continue
            next_pt = kpi_gps_pd.iloc[i+1]["latitude"], kpi_gps_pd.iloc[i+1]["longitude"], kpi_gps_pd.iloc[i+1]["altitude"]
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            if common.lla_distance((lat, lon, alt), next_pt) < 0.5:
                geom.outerboundaryis = _create_kml_polygon(lat, lon, alt, MARKER_WIDTH, 4)
            else:
                geom.outerboundaryis = _create_kml_triangle((lat, lon, alt), next_pt)
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
            geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'
            
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = _create_kml_circle(next_pt[0], next_pt[1], next_pt[2], 1)
            geom.style.polystyle.color = simplekml.Color.rgb(0,0,0)
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH


        if "octagon" in options.draw_type:
            geom = kml.newpolygon()
            geom.altitudemode = simplekml.AltitudeMode.relativetoground
            geom.outerboundaryis = _create_kml_polygon(lat, lon, alt, MARKER_WIDTH, 8)
            geom.style.polystyle.color = kml_color
            geom.style.linestyle.color = kml_color
            geom.style.linestyle.width = MARKER_WIDTH
            geom.description = add_labels(kpi_gps_pd.iloc[i], options.labels, options.label_units, options.custom_label)
            geom.description += f'<p>{options.kpi} = {kpi} {options.kpi_units}</p><p>(lat, lon) = ({lat},{lon})</p><p> altitude = {alt} m</p><p> index = {i}</p>'

    if options.output_log:
        kml_fName = os.path.join(options.workarea, options.output_log)
    else:
        kml_fName = os.path.join(options.workarea, options.pci + "_" + options.kpi + ".kml")
    
    print("Number of data points: " + str(numRows))
    print("Writing to " + str(kml_fName))
    kml.save(kml_fName)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate KML file of the specified KPI and cell PCI')
    parser.add_argument('-i', '--input-log', type=str, default = DEFAULT_LOG_NAME, help="Merged log name. Default is " + DEFAULT_LOG_NAME)
    parser.add_argument('-o', '--output-log', type=str, default = None, help="Output kml file. Default is the name of the KPI")
    parser.add_argument('-k', '--kpi', type=str, default = DEFAULT_KPI, help="KPI to plot. Default is " + DEFAULT_KPI )
    parser.add_argument('--kpi-min', type=float, default = None, help="Minimum value of the KPI color bar. Default is minimum of all KPIs.")
    parser.add_argument('--kpi-max', type=float, default = None, help="Maximum value of the KPI color bar. Default is maximum of all KPIs.")
    parser.add_argument('-p', '--pci', type = str, default = DEFAULT_PCI, help="PCI of the chosen cell. Default is " + DEFAULT_PCI)    
    parser.add_argument('--use-pci-colormap', action="store_true", help="Specifies whether to use a provided PCI color map.")
    parser.add_argument('-w', '--workarea', type = str, default = DEFAULT_WORKFOLDER, help="Workarea path, containing radio, vehicle and traffic logs. Default is " + DEFAULT_WORKFOLDER)    
    parser.add_argument('-u', '--kpi-units', type=str, default=DEFAULT_KPI_UNITS, help= "KPI units. Default is dBm, for RSRP.")
    parser.add_argument('--draw-type', type=str, default=DRAW_TYPE, help= "Draw type. Can be line or point or circle or any combination such as line,point or circle,point.")
    parser.add_argument('--pci-col', type=str, default=DEFAULT_PCI_COL_NAME, help= "PCI Column name.")   
    parser.add_argument('--custom-label', type=str, default=None, help= "A custom text to add to the pop-up label, at all data points.")   
    parser.add_argument('--labels', nargs='+', default=[], help= "Fields to display in the pop-up label. Please also provide --label-units along with --labels.")   
    parser.add_argument('--log-type', nargs='+', default=DEFAULT_LOG_TYPE, help= "Input CSV log type.")   
    parser.add_argument('--alt-col', nargs='+', default=DEFAULT_ALT_COL, help= "Altitude column.")   

    parser.add_argument('--label-units', nargs='+', default=[], help= "Units of the fields to display in the pop-up label.")   
    parser.add_argument('--filters', type=str,)
    options = parser.parse_args()
    generate_kml(options)
