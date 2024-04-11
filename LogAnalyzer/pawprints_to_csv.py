import csv
import os
import copy
import common
import json
import pandas
import argparse

OUTPUT_FOLDER = "../../WorkArea/"

# Default Options
PAWPRINTS_LOG_PATH = "../../WorkArea/pawprints.jsonl"
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
    
def get_csv_kpi_path(pci, kpi):
    return os.path.join(OUTPUT_FOLDER, OUTPUT_CSV_PREFIX + str(pci) + "_" + kpi + ".csv")
    
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
            append_to_csv(get_csv_kpi_path("connected", "pci"), connected_pci)
            append_to_csv(get_csv_kpi_path("connected", "abs_time"), abs_time)
            append_to_csv(get_csv_kpi_path("connected","rel_time"), rel_time)
            connected_index = 0
            #connected_index = log_row["connected_index"]
            if connected_pci != -1:
                connected_cell = log_row["cells"][connected_index]
                for kpi in connected_cell:
                        if "connected_" + kpi not in data:
                            data["connected_" + kpi] = []
                        data["connected_" + kpi].append(connected_cell[kpi])

            if "nr_signal_strength" in log_row:
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
            for cell in log_row["cells"]:
                panda_cell = cell.copy()
                
                panda_cell["abs_time"] = log_row["abs_time"]
                panda_cell["rel_time"] = log_row["rel_time"]

                if "companion_abs_time" in panda_cell:
                    panda_cell["companion_abs_time"] = log_row["companion_abs_time"]

                panda_cell["is_connected"] = 0
                if cell["pci"] == log_row["connected_pci"]:
                    panda_cell["is_connected"] = 1 

                data["data"] = pandas.concat([data["data"], pandas.DataFrame(panda_cell, index = [0])], ignore_index = True)

    # Write metadata about seen cells
    seen_pcis = []
    for cell in log_row["cells"]:
        seen_pcis.append(cell["pci"])

    append_to_csv(os.path.join(OUTPUT_FOLDER, 'seen_pci.csv'), seen_pcis)

def clean_up_old_logs():
    if os.path.exists(get_csv_kpi_path("connected", "pci")):
        os.remove(get_csv_kpi_path("connected", "pci"))

    if os.path.exists(get_csv_kpi_path("connected", "abs_time")):
        os.remove(get_csv_kpi_path("connected", "abs_time"))

    if os.path.exists(get_csv_kpi_path("connected", "rel_time")):
        os.remove(get_csv_kpi_path("connected", "rel_time"))



def process_log(options):

    clean_up_old_logs()

    handover_count = 0
    
    data = {}
    if options.mergemode== "all":
        data["data"] = pandas.DataFrame(index=None)
    
    with open(PAWPRINTS_LOG_PATH) as f:
        log_rows = f.readlines()
        for log_row_string in log_rows:
           log_row = json.loads(log_row_string)
           process_log_row(log_row, data, options)
    
    if options.output == "csv" and options.mergemode == "all":
        data["data"].to_csv(os.path.join(OUTPUT_FOLDER, "pawprints.csv"))
    if options.output == "csv" and options.mergemode == "per-cell-kpi":
        for key in data:
            write_to_csv(os.path.join(OUTPUT_FOLDER, key + ".csv"),data[key])

    
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
    parser.add_argument('-p', '--csvprefix', type=str, default=OUTPUT_CSV_PREFIX, help="Prefix of the output csv file(s)")
    parser.add_argument('-m', '--mergemode', type = str, default = MERGE_DEFAULT,
                        help='Options to merge the output CSV. "all" = creates one csv containing all kpis of all cell. "per-cell-kpi" = creates multiple csvs, one for each kpi of all cell')
    parser.add_argument('-o', '--output', type = str, default = OUTPUT_DEFAULT,
                        help='Output options. csv or influx')
    options = parser.parse_args()
    process_log(options)

if __name__ == "__main__":
    main()
