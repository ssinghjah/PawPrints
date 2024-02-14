import csv
import settings
import enums
import matplotlib.pyplot as plt

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


def read_csv(csv_path):
    rows = []
    with open(csv_path) as csv_handle:
        csv_reader = csv.reader(csv_handle, delimiter=',')
        for row in csv_reader:
            if len(row) > 1:
                rows.append([try_float_convert(val) for val in row])
            else:
                rows.append(try_float_convert(row[0]))
    return rows

def hex_to_rgb(hex):
    rgb = []
    for i in (1, 3, 5):
        decimal = int(hex[i:i + 2], 16)/255.0
        rgb.append(decimal)

    return {"r":rgb[0], "g":rgb[1], "b":rgb[2]}

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
        color["b"] = 1 + 4 * (vmin + 0.25 * dv - v) /dv
    elif (v < (vmin + 0.75 * dv)):
        color["r"] = 4 * (v - vmin - 0.5 * dv) /dv
        color["b"] = 0
    else:
        color["g"] = 1 + 4 * (vmin + 0.75 * dv - v) /dv
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