import csv
import os
import copy
import common
import json
import pandas
import argparse
import time_merger
from datetime import datetime
import numpy as np
import toml
import process_iperf_log
# import pawprints_gps_to_csv
# -i ~/Work/AERPAW/ExperimentData/NCSU_Sep_18_2024/wifi.txt -o ~/Work/AERPAW/ExperimentData/NCSU_Sep_18_2024/

OUTPUT_FOLDER = "./"
GPS_LAT_INDEX = 1
GPS_LON_INDEX = 2

# Default Options
GPS_SOURCE_TYPE_DEFAULT = "companion" 
PAWPRINTS_LOG_PATH = "../../ExperimentData/April_15_2024_Lake_Wheeler/pawprints.jsonl"
MERGE_DEFAULT = "all" # Can be all or per-cell or per-cell-kpi
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

def process_wifi_row(log_row, data, options):
    rel_time = log_row["rel_time"]
    abs_time = log_row["abs_time"]
    for ap in log_row["aps"]:
        panda_ap = ap.copy()
        panda_ap["phone_abs_time"] = log_row["abs_time"]
        panda_ap["rel_time"] = log_row["rel_time"]    
        panda_ap["is_connected"] = 1 if ("connected_bssid" in log_row and log_row["connected_bssid"] == ap["bssid"]) else 0
        panda_ap["connected_rssi"] = np.nan if "connected_rssi" not in log_row else log_row["connected_rssi"]
        panda_ap["connected_link_speed"] = np.nan if "connected_link_speed" not in log_row else log_row["connected_link_speed"]
        panda_ap["connected_bssid"] = " " if "connected_bssid" not in log_row else log_row["connected_bssid"]
        panda_ap["num_aps_detected"] = log_row["num_detected"] 
        panda_ap["connected_network_id"] = np.nan if "connected_network_id" not in log_row else log_row["connected_network_id"]

        # if "connected_network_id" in log_row:
        #     panda_ap["connected_rssi"] = log_row["connected_rssi"] 
        #     panda_ap["connected_link_speed"] = log_row["connected_link_speed"]
        #     panda_ap["connected_bssid"] = log_row["connected_bssid"] 

        #     if ap["bssid"] == log_row["connected_bssid"]:
        #         panda_ap["is_connected"] = 1

        if "companion_abs_time" in log_row:
            panda_ap["companion_abs_time"] = log_row["companion_abs_time"]
            panda_ap["time_readable"] = common.epoch_ms_to_readable(panda_ap["companion_abs_time"])
        else:
            panda_ap["time_readable"] = common.epoch_ms_to_readable(panda_ap["phone_abs_time"])

        data["wifi_info"] = pandas.concat([data["wifi_info"], pandas.DataFrame(panda_ap, index = [0])], ignore_index = True)
        # pandas.DataFrame(panda_ap, index=[0]).to_csv(os.path.join(options.output_dir, options.prefix + "wifi.csv"), mode="a", header=False, index=False)
        # pandas.DataFrame(panda_ap.keys()).to_csv(os.path.join(options.output_dir, options.prefix + "wifi_headers.csv"), mode="w", header=True, index=False)
        
    
def process_log_row(log_row, data, options):
    log_row["type"] = "cellular" if "cells" in log_row else "wifi" if "aps" in log_row else "" # Temp fix. Change upstream
    if log_row["type"] == "cellular":
        # Process cellular log
        if options.mergemode == "per-cell-kpi":
            # Write per cell logs
            abs_time = log_row["companion_abs_time"]
            rel_time = log_row["rel_time"]

            connected_pci = log_row["connected_pci"]
            connected_index = -1
            cell_index = 0 
            for cell in log_row["cells"]:
                if (str(cell["pci"]) + "_rel_time") not in data:
                    data[str(cell["pci"]) + "_rel_time"] = []
                    data[str(cell["pci"]) + "_abs_time"] = []
                data[str(cell["pci"]) + "_rel_time"].append(rel_time) 
                data[str(cell["pci"]) + "_abs_time"].append(abs_time)     
                if cell["pci"] == connected_pci:
                    connected_index = cell_index   
                for kpi in cell:
                    if kpi != "pci":
                        key = cell["pci"] + "_" + kpi
                        if key not in data:
                            data[key] = []
                        data[key].append(cell[kpi])
                cell_index += 1

            # Write connected cell logs
            append_to_csv(get_csv_kpi_path("connected", "pci", options.output_dir), connected_pci)
            append_to_csv(get_csv_kpi_path("connected", "abs_time", options.output_dir), abs_time)
            append_to_csv(get_csv_kpi_path("connected","rel_time", options.output_dir), rel_time)
            # connected_index = 0
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
            # panda_cell = log_row.copy()
            
            if "nr_signal_strength" in log_row and len(log_row['nr_signal_strength'].keys()) > 1:
                panda_cell = log_row["nr_signal_strength"].copy()
                panda_cell["phone_abs_time"] = log_row["abs_time"]
                panda_cell["rel_time"] = log_row["rel_time"]

                if "companion_abs_time" in log_row:
                    panda_cell["companion_abs_time"] = log_row["companion_abs_time"]
                    panda_cell["time_readable"] = common.epoch_ms_to_readable(panda_cell["companion_abs_time"])
                else:
                    panda_cell["time_readable"] = common.epoch_ms_to_readable(panda_cell["phone_abs_time"])
   
                data['nr_signal_strength'] = pandas.concat([data["nr_signal_strength"], pandas.DataFrame(panda_cell, index =[0])], ignore_index = True)
                # Add companion and phone time

                # pandas.DataFrame(panda_cell, index=[0]).to_csv(os.path.join(options.output_dir, options.prefix + "nr_signal_strength.csv"), mode="a", header= False, index=False)
                # pandas.DataFrame(panda_cell.keys()).to_csv(os.path.join(options.output_dir, options.prefix + "nr_signal_strength_headers.csv"), mode="w", header= True, index=False)
                
            for cell in log_row["cells"]:
                panda_cell = cell.copy()
                panda_cell["phone_abs_time"] = log_row["abs_time"]
                panda_cell["rel_time"] = log_row["rel_time"]    
                panda_cell["is_connected"] = 0
                if int(cell["pci"]) == log_row["connected_pci"]:
                    panda_cell["is_connected"] = 1 

                if "companion_abs_time" in log_row:
                    panda_cell["companion_abs_time"] = log_row["companion_abs_time"]
                    panda_cell["time_readable"] = common.epoch_ms_to_readable(panda_cell["companion_abs_time"])
                else:
                    panda_cell["time_readable"] = common.epoch_ms_to_readable(panda_cell["phone_abs_time"])

                data["cell_info"] = pandas.concat([data["cell_info"], pandas.DataFrame(panda_cell, index = [0])], ignore_index = True)
                # pandas.DataFrame(panda_cell, index=[0]).to_csv(os.path.join(options.output_dir, options.prefix + "cellular.csv"), mode="a", header=False, index=False)
                # pandas.DataFrame(panda_cell.keys()).to_csv(os.path.join(options.output_dir, options.prefix + "cellular_headers.csv"), mode="w", header=True, index=False)        
        
        # Write metadata about seen cells
        seen_pcis = []
        for cell in log_row["cells"]:
            seen_pcis.append(cell["pci"])
        append_to_csv(os.path.join(options.output_dir, 'seen_pci.csv'), seen_pcis)


    elif log_row["type"] == "wifi":
        process_wifi_row(log_row,data, options)

    
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

def preprend_header(options, log_type):
    data = pandas.read_csv(os.path.join(options.outputdir, options.prefix + log_type + ".csv"), index_col=False)
    headers = pandas.read_csv(os.path.join(options.outputdir, options.prefix + log_type + "_headers.csv"), index_col=False)
    data.columns = headers
    data.to_csv(os.path.join(options.outputdir, options.prefix + log_type + ".csv"), index=False)


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
          if options.gps_source == "pawprints":
            gps_data = pawprints_gps_to_csv.run(options.gps_log)
          else:
            gps_data = pandas.read_csv(options.gps_log)
            gps_data["gps_times"] = gps_data.iloc[:, 7].apply(format_gps_times)


    iperf_data = None
    if bMergeIPerf:
          iperf_data = process_iperf_log.process_log(options.iperf_log)
          iperf_times = iperf_data["abs_time"]
          print(options.iperf_log)

    # Specific operations
    if bMergeGPS:
        print("Merging GPS ...")
        # get gps_indices using pawprints time as a reference. Threshold for interpolation? if time_delay > x seconds, do not interpolate.
        cell_indices, gps_indices = time_merger.merge(cell_info_times, gps_data["gps_times"], mode=1)

        # generate columns of gps lat, lon, altitude using gps_indices
        cell_info["longitude"] = gps_data.iloc[gps_indices, config["gps"]["lon_index"]].to_list()
        cell_info["latitude"] = gps_data.iloc[gps_indices, config["gps"]["lat_index"]].to_list()
        cell_info["altitude"] = gps_data.iloc[gps_indices, config["gps"]["alt_index"]].to_list()

        if not nr_signal_strength.empty:
            nr_signal_strength_times = nr_signal_strength["companion_abs_time"] if "companion_abs_time" in nr_signal_strength else nr_signal_strength["phone_abs_time"]
            nr_signal_strength_indices, gps_indices = time_merger.merge(nr_signal_strength_times, gps_data["gps_times"], mode=1)
            nr_signal_strength["longitude"] = gps_data.iloc[gps_indices, config["gps"]["lon_index"]].to_list()
            nr_signal_strength["latitude"] = gps_data.iloc[gps_indices, config["gps"]["lat_index"]].to_list()
            nr_signal_strength["altitude"] = gps_data.iloc[gps_indices, config["gps"]["alt_index"]].to_list()

    if bMergeIPerf:   
        print("Merging Iperf ...")     
        # get iperf indices using pawprints indices as a reference. Threshold for interpolation? if time_delay > x seconds, do not interpolate.
        cell_indices, iperf_indices = time_merger.merge(cell_info_times, iperf_times, mode=1)

        # generate  columns of gps lat, lon, altitude using gps_indices
        cell_info["iperf_client_mbps"] = [iperf_data["iperf_client_mbps"][i] for i in iperf_indices]
        # cell_info["iperf_client_cwnd"] = iperf_data.iloc[iperf_indices, "cwnd"].to_list()

        nr_signal_strength_indices, iperf_indices = time_merger.merge(nr_signal_strength_times, iperf_times, mode=1)
        nr_signal_strength["iperf_client_mbps"] = [iperf_data["iperf_client_mbps"][i] for i in iperf_indices]
        # nr_signal_strength["iperf_client_cwnd"] = iperf_data.iloc[iperf_indices, "cwnd"].to_list()   

    if bMergeIPerf and bMergeGPS:
        print("Merging Iperf & GPS ...")     
        iperf_indices, gps_indices = time_merger.merge(iperf_times, gps_data["gps_times"], mode=1)
        iperf_data["longitude"] = gps_data.iloc[gps_indices, config["gps"]["lon_index"]].to_list()
        iperf_data["latitude"] = gps_data.iloc[gps_indices, config["gps"]["lat_index"]].to_list()
        iperf_data["altitude"] = gps_data.iloc[gps_indices, config["gps"]["alt_index"]].to_list()
        
        # Write Iperf to CSV
        iperf_data_pd = pandas.DataFrame(iperf_data)
        output_path = os.path.join(options.output_dir, options.prefix + "iperf_client.csv")
        print("Writing to " + output_path)
        iperf_data_pd.to_csv(output_path,  index=False)


def to_sql(data):
    # Get all column names
    # Create SQL tables from column name and column data type
    # iterate over all rows and insert into the table 
    pass


def _write_csv(data, log_type, options):
    if log_type in data and not data[log_type].empty:
        output_path = os.path.join(options.output_dir, options.prefix + log_type + ".csv")
        print("Writing to " + output_path)
        data[log_type].to_csv(output_path, index=False)


def process_log(options, config):
    clean_up_old_logs(options.output_dir)
    handover_count = 0
    
    data = {}
    if options.mergemode== "all":
        data["cell_info"] = pandas.DataFrame(index=None)
        data["nr_signal_strength"] = pandas.DataFrame(index=None)
        data["wifi_info"] = pandas.DataFrame(index=None)

    
    with open(options.input) as f:
        log_rows = f.readlines()
        num_lines = len(log_rows)
        row_num = 0
        for index, log_row_string in enumerate(log_rows):
           print(f'{row_num + 1}/{num_lines}')
           row_num += 1
           log_row = json.loads(log_row_string)
           process_log_row(log_row, data, options)

    # merge_logs(data, options, config)
    
    if options.output_format == "csv" and options.mergemode == "all":
        _write_csv(data, "nr_signal_strength", options)
        _write_csv(data, "cell_info", options)
        _write_csv(data, "wifi_info", options)
    
    
    # if options.output_format == "csv" and options.mergemode == "per-cell-kpi":
    #     for key in data:
    #         write_to_csv(os.path.join(options.output, key + ".csv"),data[key])

    
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
    parser.add_argument('--iperf-log', type = str, default = None, help='Path to iperf client log file')
    parser.add_argument('-g', '--gps-log', type = str, default = None, help='GPS log file')
    parser.add_argument('-p', '--prefix', type=str, default=OUTPUT_CSV_PREFIX, help="Prefix of the output csv file(s)")
    parser.add_argument('-m', '--mergemode', type = str, default = MERGE_DEFAULT, help='Options to merge the output CSV. "all" = creates one csv containing all kpis of all cell. "per-cell-kpi" = creates multiple csvs, one for each kpi of all cell')
    parser.add_argument('-o', '--output-dir', type = str, default = OUTPUT_FOLDER, help='Output Folder.')
    parser.add_argument('--output-format', type = str, default = OUTPUT_DEFAULT, help='Output options. csv or influx')
    parser.add_argument('--gps-source', type = str, default = GPS_SOURCE_TYPE_DEFAULT, help='GPS log source. companion or pawprints')
    options = parser.parse_args()
    config = toml.load("./log_converter.toml")
    process_log(options, config)

if __name__ == "__main__":
    main()
