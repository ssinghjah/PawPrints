import csv
import os
import copy
import common
import json
import pandas
import argparse
import time_merger
from datetime import datetime
import process_gps_log
import toml
import process_iperf_log

OUTPUT_FOLDER = "../../ExperimentData/April_15_2024_Lake_Wheeler/"
GPS_LAT_INDEX = 1
GPS_LON_INDEX = 2

# Default Options
PAWPRINTS_LOG_PATH = "../../ExperimentData/April_15_2024_Lake_Wheeler/pawprints.jsonl"
MERGE_DEFAULT = "per-cell-kpi" # Can be all or per-cell or per-cell-kpi
OUTPUT_CSV_PREFIX = ""
OUTPUT_DEFAULT = "csv"

def append_to_csv(path, single_row):
    with open(path, 'a') as f_pointer:
        csv_pointer = csv.writer(f_pointer)
        if isinstance(single_row, list):
            csv_pointer.writerow(single_row)
        else:
            csv_pointer.writerow([single_row])

def write_to_csv(path, all_rows):
    with open(path, 'w+') as f_pointer:
        csv_pointer = csv.writer(f_pointer)
        if isinstance(all_rows, list):
            for row in all_rows:
                csv_pointer.writerow([row])
        else:
            csv_pointer.writerow([all_rows])
    
def get_csv_kpi_path(pci, kpi, output_folder):
    return os.path.join(output_folder, OUTPUT_CSV_PREFIX + str(pci) + "_" + kpi + ".csv")
    
def process_log_row(log_row, data, options):
    log_row["type"] = "cellular" # Temp fix. Change upstream
    if log_row["type"] == "cellular":
        # Process cellular log
        if options.mergemode == "per-cell-kpi":
            # Write per cell logs
            abs_time = log_row["companion_abs_time"]
            rel_time = log_row["rel_time"]

            for cell in log_row["cells"]:
                if (str(cell["pci"]) + "_rel_time") not in data:
                    data[str(cell["pci"]) + "_rel_time"] = []
                    data[str(cell["pci"]) + "_abs_time"] = []
                data[str(cell["pci"]) + "_rel_time"].append(rel_time) 
                data[str(cell["pci"]) + "_abs_time"].append(abs_time)       
                for kpi in cell:
                    if kpi != "pci":
                        key = cell["pci"] + "_" + kpi
                        if key not in data:
                            data[key] = []
                        data[key].append(cell[kpi])           

            # Write connected cell logs
            connected_pci = log_row["connected_pci"]
            append_to_csv(get_csv_kpi_path("connected", "pci", options.output), connected_pci)
            append_to_csv(get_csv_kpi_path("connected", "abs_time", options.output), abs_time)
            append_to_csv(get_csv_kpi_path("connected","rel_time", options.output), rel_time)
            connected_index = 0
            #connected_index = log_row["connected_index"]
            if connected_pci != -1:
                connected_cell = log_row["cells"][connected_index]
                for kpi in connected_cell:
                        if "connected_" + kpi not in data:
                            data["connected_" + kpi] = []
                        data["connected_" + kpi].append(connected_cell[kpi])

            if "nr_signal_strength" in log_row and len(log_row['nr_signal_strength'].keys()) > 1:
                nr_sig_strength = log_row["nr_signal_strength"]
                if "nr_signal_strength_rel_time" not in data:
                    data["nr_signal_strength_rel_time"] = []
                    data["nr_signal_strength_abs_time"] = []
                
                data["nr_signal_strength_rel_time"].append(rel_time)
                data["nr_signal_strength_abs_time"].append(abs_time)

                for kpi in nr_sig_strength:
                    if "nr_signal_strength_" + kpi not in data:
                        data["nr_signal_strength_" + kpi] = []
                    data["nr_signal_strength_" + kpi].append(nr_sig_strength[kpi])

        elif options.mergemode == "all":
            panda_cell = log_row.copy()
            
            if "nr_signal_strength" in log_row and len(log_row['nr_signal_strength'].keys()) > 1:
                panda_cell = log_row["nr_signal_strength"].copy()
                panda_cell["phone_abs_time"] = log_row["abs_time"]
                panda_cell["rel_time"] = log_row["rel_time"]

                if "companion_abs_time" in log_row:
                    panda_cell["companion_abs_time"] = log_row["companion_abs_time"]
   
                data['nr_signal_strength'] = pandas.concat([data["nr_signal_strength"], pandas.DataFrame(panda_cell, index =[0])], ignore_index = True)
                # Add companion and phone time

            for cell in log_row["cells"]:
                panda_cell = cell.copy()
                panda_cell["phone_abs_time"] = log_row["abs_time"]
                panda_cell["rel_time"] = log_row["rel_time"]    
                panda_cell["is_connected"] = 0
                if int(cell["pci"]) == log_row["connected_pci"]:
                    panda_cell["is_connected"] = 1 

                if "companion_abs_time" in log_row:
                    panda_cell["companion_abs_time"] = log_row["companion_abs_time"]

                data["cell_info"] = pandas.concat([data["cell_info"], pandas.DataFrame(panda_cell, index = [0])], ignore_index = True)

    # Write metadata about seen cells
    seen_pcis = []
    for cell in log_row["cells"]:
        seen_pcis.append(cell["pci"])

    append_to_csv(os.path.join(options.output, 'seen_pci.csv'), seen_pcis)

def clean_up_old_logs(output_folder):
    if os.path.exists(get_csv_kpi_path("connected", "pci", output_folder)):
        os.remove(get_csv_kpi_path("connected", "pci", output_folder))

    if os.path.exists(get_csv_kpi_path("connected", "abs_time", output_folder)):
        os.remove(get_csv_kpi_path("connected", "abs_time", output_folder))

    if os.path.exists(get_csv_kpi_path("connected", "rel_time", output_folder)):
        os.remove(get_csv_kpi_path("connected", "rel_time", output_folder))

def format_gps_times(str_time):
    epoch_time =  datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f').timestamp()
    return epoch_time*1000.0

def merge_logs(data, options, config):

    bMergeGPS = options.gps_log is not None
    bMergeIPerf = options.iperf_log is not None

    cell_info = data["cell_info"]
    nr_signal_strength = data["nr_signal_strength"]

    if not bMergeGPS and not bMergeIPerf:
        return

    # Common operations 
    cell_info_times = cell_info["companion_abs_time"] if "companion_abs_time" in cell_info else cell_info["phone_abs_time"]
    cell_info = data["cell_info"]
    nr_signal_strength = data["nr_signal_strength"]

    gps_data = None
    if bMergeGPS:
          gps_data = pandas.read_csv(options.gps_log)
          gps_data["gps_times"] = gps_data.iloc[:, 7].apply(format_gps_times)

    iperf_data = None
    if bMergeIPerf:
          iperf_data = process_iperf_log.process_log(options.iperf_log)
          iperf_times = iperf_data["abs_time"]

    # Specific operations
    if bMergeGPS:
        # get gps_indices using pawprints time as a reference. Threshold for interpolation? if time_delay > x seconds, do not interpolate.
        cell_indices, gps_indices = time_merger.merge(cell_info_times, gps_data["gps_times"], mode=1)

        # generate columns of gps lat, lon, altitude using gps_indices
        cell_info["longitude"] = gps_data.iloc[gps_indices, config["gps"]["lon_index"]].to_list()
        cell_info["latitude"] = gps_data.iloc[gps_indices, config["gps"]["lat_index"]].to_list()
        cell_info["altitude"] = gps_data.iloc[gps_indices, config["gps"]["alt_index"]].to_list()

        nr_signal_strength_times = nr_signal_strength["companion_abs_time"] if "companion_abs_time" in nr_signal_strength else nr_signal_strength["phone_abs_time"]
        nr_signal_strength_indices, gps_indices = time_merger.merge(nr_signal_strength_times, gps_data["gps_times"], mode=1)
        nr_signal_strength["longitude"] = gps_data.iloc[gps_indices, config["gps"]["lon_index"]].to_list()
        nr_signal_strength["latitude"] = gps_data.iloc[gps_indices, config["gps"]["lat_index"]].to_list()
        nr_signal_strength["altitude"] = gps_data.iloc[gps_indices, config["gps"]["alt_index"]].to_list()

    if bMergeIPerf:        
        # get iperf indices using pawprints indices as a reference. Threshold for interpolation? if time_delay > x seconds, do not interpolate.
        cell_indices, iperf_indices = time_merger.merge(cell_info_times, iperf_times, mode=1)

        # generate  columns of gps lat, lon, altitude using gps_indices
        cell_info["iperf_client_mbps"] = [iperf_data["throughput"][i] for i in iperf_indices]
        # cell_info["iperf_client_cwnd"] = iperf_data.iloc[iperf_indices, "cwnd"].to_list()

        nr_signal_strength_indices, iperf_indices = time_merger.merge(nr_signal_strength_times, iperf_times, mode=1)
        nr_signal_strength["iperf_client_mbps"] = [iperf_data["throughput"][i] for i in iperf_indices]
        # nr_signal_strength["iperf_client_cwnd"] = iperf_data.iloc[iperf_indices, "cwnd"].to_list()   

    if bMergeIPerf and bMergeGPS:
        iperf_indices, gps_indices = time_merger.merge(iperf_times, gps_data["gps_times"], mode=1)
        iperf_data["longitude"] = gps_data.iloc[gps_indices, config["gps"]["lon_index"]].to_list()
        iperf_data["latitude"] = gps_data.iloc[gps_indices, config["gps"]["lat_index"]].to_list()
        iperf_data["altitude"] = gps_data.iloc[gps_indices, config["gps"]["alt_index"]].to_list()
        
        # Write Iperf to CSV
        iperf_data_pd = pandas.DataFrame(iperf_data)
        output_path = os.path.join(options.output, "iperf_client.csv")
        print("Writing to " + output_path)
        iperf_data_pd.to_csv(output_path,  index=False)


def to_sql(data):
    # Get all column names
    # Create SQL tables from column name and column data type
    # iterate over all rows and insert into the table 
    pass


def process_log(options, config):
    clean_up_old_logs(options.output)
    handover_count = 0
    
    data = {}
    if options.mergemode== "all":
        data["cell_info"] = pandas.DataFrame(index=None)
        data["nr_signal_strength"] = pandas.DataFrame(index=None)
    
    with open(options.input) as f:
        log_rows = f.readlines()
        for log_row_string in log_rows:
           log_row = json.loads(log_row_string)
           process_log_row(log_row, data, options)

    merge_logs(data, options, config)
    
    if options.output_format == "csv" and options.mergemode == "all":
        output_path = os.path.join(options.output, "pawprints_all.csv")
        print("Writing to " + output_path)
        data["cell_info"].to_csv(output_path, index=False)

        output_path = os.path.join(options.output, "pawprints_5G_signal_strength.csv")
        print("Writing to " + output_path)
        data["nr_signal_strength"].to_csv(output_path, index=False)
    
    if options.output_format == "csv" and options.mergemode == "per-cell-kpi":
        for key in data:
            write_to_csv(os.path.join(options.output, key + ".csv"),data[key])

    
    '''
    summary = {}
    summary["unique_num_cells_seen"] = 
    summary["unique_num_cells_connected"] =
    summary["rsrp_range"] =
    summary["rsrp_mean"] =
    summary["rsrq_range"] =
    summary["rsrq_mean"] =
    summary["rssi_range"] =
    summary["rssi_mean"]
    print("Summary:")
    '''
    
    # increment handover

def main():
    parser = argparse.ArgumentParser(description='Convert PawPrints log into .csv.')
    parser.add_argument('-i', '--input', type = str, default = PAWPRINTS_LOG_PATH, help='Input pawprints log file')
    parser.add_argument('--iperf-log', type = str, default = None, help='Standard Iperf client log file')
    parser.add_argument('-g', '--gps-log', type = str, default = None, help='GPS log file')
    parser.add_argument('-p', '--csvprefix', type=str, default=OUTPUT_CSV_PREFIX, help="Prefix of the output csv file(s)")
    parser.add_argument('-m', '--mergemode', type = str, default = MERGE_DEFAULT, help='Options to merge the output CSV. "all" = creates one csv containing all kpis of all cell. "per-cell-kpi" = creates multiple csvs, one for each kpi of all cell')
    parser.add_argument('-o', '--output', type = str, default = OUTPUT_FOLDER, help='Output Folder.')
    parser.add_argument('--output-format', type = str, default = OUTPUT_DEFAULT, help='Output options. csv or influx')

    options = parser.parse_args()
    config = toml.load("./log_converter.toml")
    process_log(options, config)

if __name__ == "__main__":
    main()
