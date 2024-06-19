import csv
import settings
import enums
from datetime import datetime
import matplotlib.pyplot as plt
import math
import numpy as np

import warnings
warnings.filterwarnings("ignore")

def get_kpi_type(kpi):
    import json
    with open("./kpis.json") as f:
        KPI_DEFINITIONS = json.load(f)
        type = None
        for technology in KPI_DEFINITIONS:
            if kpi in KPI_DEFINITIONS[technology]:
                type = KPI_DEFINITIONS[technology][kpi]["type"]
        return type


def create_3D_vec(start, end):
    vec = (end[0] - start[0], end[1] - start[1], end[2] - start[2])
    return vec

def dot_prod(vec1, vec2):
    pass

def project_point_on_line_seg(point_3d, line_seg_start, line_seg_end):
    line_vec = create_3D_vec(line_seg_start, line_seg_end)
    line_start_to_point_vec = create_3D_vec(line_seg_start, point_3d)
    proj_dist = np.dot(line_start_to_point_vec, line_vec) / np.linalg.norm(line_vec)
    return proj_dist

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))*360.0/math.pi

def write_csv(fName, values):
    with open(fName, 'w') as f:
        csv_writer = csv.writer(f)
        # csv_writer.writerow([cell_param])
        for value in values:
            if not isinstance(value, list):
                csv_writer.writerow([value])
            else:
                csv_writer.writerow(value)

def write_file(fName, content):
    with open(fName, "w") as f:
        f.write(content)

def first_indices_greater_than(elem1, elem2, list):
    elem1_index = -1
    elem2_index = -1
    for index, elem in enumerate(list):
        if elem1_index == -1 and elem >= elem1:
            elem1_index = index
        if elem2_index == -1 and elem >= elem2:
            elem2_index = index

        if elem2_index != -1 and elem1_index != -1:
            break
    return int(elem1_index), int(elem2_index)

def format_gps_times(str_time):
    epoch_time =  datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f').timestamp()
    return epoch_time*1000.0

def epoch_ms_to_readable(epoch_time_ms):
    date_obj = datetime.fromtimestamp(epoch_time_ms/1000.0)
    return date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

def epoch_s_to_readable(epoch_time_s):
    date_obj = datetime.fromtimestamp(epoch_time_s)
    return date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')


def read_csv(csv_path):
    rows = []
    with open(csv_path) as csv_handle:
        csv_reader = csv.reader(csv_handle, delimiter=',')
        row_num = 0
        for row in csv_reader:
            row_num += 1
            if len(row) > 1:
                rows.append([try_float_convert(val) for val in row])
            elif len(row) > 0:
                rows.append(try_float_convert(row[0]))
    return rows

def lla_to_ecef(lla):
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lla[0])
    lon_rad = math.radians(lla[1])

    # WGS84 parameters
    a = 6378137.0  # semi-major axis
    f_inv = 298.257223563  # inverse flattening
    f = 1.0 / f_inv
    e2 = 1 - (1 - f) * (1 - f)

    # Radius of curvature in the prime vertical
    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)

    # Convert LLA to ECEF
    X = (N + lla[2]) * math.cos(lat_rad) * math.cos(lon_rad)
    Y = (N + lla[2]) * math.cos(lat_rad) * math.sin(lon_rad)
    Z = (N * (1 - e2) + lla[2]) * math.sin(lat_rad)
    return [X, Y, Z]



def point_dist_3D(p1, p2):
    dist = math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2) + pow(p1[2] - p2[2], 2))
    return dist

def lineseg_dist(p, a, b):
    # normalized tangent vector
    d = np.divide(b - a, np.linalg.norm(b - a))

    # signed parallel distance components
    s = np.dot(a - p, d)
    t = np.dot(p - b, d)

    # clamped parallel distance
    h = np.maximum.reduce([s, t, 0])

    # perpendicular distance component
    c = np.cross(p - a, d)

    return np.hypot(h, np.linalg.norm(c))

def hex_to_rgb(hex):
    rgb = []
    for i in (1, 3, 5):
        decimal = int(hex[i:i + 2], 16)/255.0
        rgb.append(decimal)

    return {"r": rgb[0], "g": rgb[1], "b": rgb[2]}

def generate_discrete_color_map(values):
    num_values = len(values)
    colors = {}
    for i in range(num_values):
        colors[values[i]] = value_to_color(i+1, 1, num_values)
    return colors

def generate_discrete_colors(num_colors):
    colors = []
    for i in range(num_colors):
        colors.append(value_to_color(i+1, 1, num_colors))
    return colors

# r,g,b range is from 0-1
def rgb_to_kml_hex(rgb_dict):
    hex = 'ff{:02x}{:02x}{:02x}'.format(int(rgb_dict["b"]*255.0), int(rgb_dict["g"]*255.0), int(rgb_dict["r"]*255.0))
    return hex

def rgb_to_hex(rgb_dict):
    hex = '#{:02x}{:02x}{:02x}ff'.format(int(rgb_dict["r"] * 255.0), int(rgb_dict["g"] * 255.0), int(rgb_dict["b"] * 255.0))
    return hex

def try_float_convert(string_input):
    if string_input.isdigit():
        return int(string_input)
    else:
        try:
            float_string = float(string_input)
            return float_string
        except ValueError:
            return string_input
        
def value_to_color(v, vmin, vmax, colormap = None):
    color = {"r": 1.0, "g": 1.0, "b":1.0} # r,g,b

    if colormap != None:
        norm = plt.Normalize(vmin, vmax)
        cmap = plt.cm.get_cmap(colormap)
        rgba = cmap(norm(v))
        color["r"] = rgba[0]
        color["g"] = rgba[1]
        color["b"] = rgba[2]
        return color

    if (v < vmin):
        v = vmin
    if (v > vmax):
        v = vmax
    dv = vmax - vmin;
    if (v < (vmin + 0.25 * dv)):
        color["r"] = 0;
        color["g"] = 4 * (v - vmin) /dv;
    elif (v < (vmin + 0.5 * dv)):
        color["r"] = 0;
        color["b"] = 1 + 4 * (vmin + 0.25 * dv - v) / dv
    elif (v < (vmin + 0.75 * dv)):
        color["r"] = 4 * (v - vmin - 0.5 * dv) / dv
        color["b"] = 0
    else:
        color["g"] = 1 + 4 * (vmin + 0.75 * dv - v) / dv
        color["b"] = 0
    return color


def rsrp_to_quality(rsrp):
    if rsrp >= settings.RSRP_GOOD_THRESH:
        rsrp_quality = enums.SIG_QUALITY.GOOD
    elif rsrp >= settings.RSRP_ACCEPTABLE_THRESH:
        rsrp_quality = enums.SIG_QUALITY.ACCEPTABLE
    else:
        rsrp_quality = enums.SIG_QUALITY.POOR
    return rsrp_quality

def rsrq_to_quality(rsrq):
    if rsrq >= settings.RSRQ_GOOD_THRESH:
        rsrq_quality = enums.SIG_QUALITY.GOOD
    elif rsrq >= settings.RSRQ_ACCEPTABLE_THRESH:
        rsrq_quality = enums.SIG_QUALITY.ACCEPTABLE
    else:
        rsrq_quality = enums.SIG_QUALITY.POOR
    return rsrq_quality