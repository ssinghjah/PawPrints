import csv
import os
import copy
import common
import json
import pandas
import argparse

OUTPUT_FOLDER = "./WorkSpace/Data/"

# Default Options
PAWPRINTS_LOG_PATH = "./pawprints.jsonl"
MERGE_DEFAULT = "per-cell-kpi" # Can be all or per-cell or per-cell-kpi
OUTPUT_CSV_PREFIX = "pawprints"

def append_to_csv(path, single_row):
    with open(path, 'a') as f_pointer:
        csv_pointer = csv.writer(f_pointer)
        if isinstance(single_row, list):
            csv_pointer.writerow(single_row)
        else:
            csv_pointer.writerow([single_row])
    
def get_csv_kpi_path(pci, kpi):
    return os.path.join(OUTPUT_FOLDER, OUTPUT_CSV_PREFIX + "_" + str(pci) + "_" + kpi + ".csv")
    
def process_log_row(log_row, csv_data, options):
    if log_row["type"] == "cellular":
        # Process cellular log
        if options.mergemode == "per-cell-kpi":
            # Write per cell logs
            abs_time = log_row["companion_abs_time"]
            rel_time = log_row["rel_time"]            
            for cell in log_row["cells"]:
                    for kpi in cell:
                        if kpi != "pci":
                            append_to_csv(get_csv_kpi_path(cell["pci"], kpi), cell[kpi])
                    append_to_csv(get_csv_kpi_path(cell["pci"], "abs_time"), abs_time)
                    append_to_csv(get_csv_kpi_path(cell["pci"], "rel_time"), rel_time)

            # Write connected cell logs
            connected_pci = log_row["connected_pci"]
            append_to_csv(get_csv_kpi_path("connected", "pci"), connected_pci)
            append_to_csv("abs_time.csv", abs_time)
            append_to_csv("rel_time.csv", rel_time)
            connected_index = log_row["connected_index"]
            if connected_pci != -1:
                connected_cell = log_row["cells"][connected_index]
                for kpi in connected_cell:
                    if kpi != "pci":
                        append_to_csv(get_csv_kpi_path('connected', kpi), connected_cell[kpi])

        elif options.mergemode == "all":
            pd_json = log_row.copy()
            for cell in log_row["cells"]:
                pci = cell["pci"]
                for kpi in cell:
                    if kpi != "pci":
                        pd_json[str(pci) + "_" + kpi] = cell[kpi]

            connected_pci = log_row["connected_pci"]
            connected_index = log_row["connected_index"]
            if connected_pci != -1:
                connected_cell = log_row["cells"][connected_index]
                for kpi in connected_cell:
                    if kpi != "pci":
                        pd_json["connected_" + kpi] = cell[kpi]
            del pd_json["cells"]
            csv_data["data"] = pandas.concat([csv_data["data"], pandas.DataFrame(pd_json, index = [0])], ignore_index = True)
        
    # Write metadata about seen cells
    seen_pcis = []
    for cell in log_row["cells"]:
        seen_pcis.append(cell["pci"])

    # append_to_csv(os.path.join(OUTPUT_FOLDER, 'num_seen_cells.csv', ), len(log_row["cells"]))
    append_to_csv(os.path.join(OUTPUT_FOLDER, 'seen_pci.csv'), seen_pcis)

def process_log(options):
    handover_count = 0
    
    csv_data = {"name":"", "data": None}
    if options.mergemode== "all":
        csv_data["data"] = pandas.DataFrame()
    
    with open(PAWPRINTS_LOG_PATH) as f:
        log_rows = f.readlines()
        for log_row_string in log_rows:
           log_row = json.loads(log_row_string)
           process_log_row(log_row, csv_data, options)

    if options.mergemode == "all":
        csv_data["data"].to_csv(os.path.join(OUTPUT_FOLDER + options.csvprefix + ".csv"))
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
    options = parser.parse_args()
    process_log(options)

if __name__ == "__main__":
    main()