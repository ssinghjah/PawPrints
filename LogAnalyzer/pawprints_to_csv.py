import csv
import os
import common
import json

OUTPUT_FOLDER = "./Data/"
PAWPRINTS_LOG_PATH = "./pawprints.jsonl"

def append_to_csv(path, single_row):
    with open(path, 'a') as f_pointer:
        csv_pointer = csv.writer(f_pointer)
        if isinstance(single_row, list):
            csv_pointer.writerow(single_row)
        else:
            csv_pointer.writerow([single_row])
    
def get_csv_kpi_path(pci, kpi):
    return os.path.join(OUTPUT_FOLDER, str(pci) + "_" + kpi + ".csv")
    
def process_log_row(log_row, options):
    '''
    if log_row["type"] == "cellular":
        # Process cellular log
    '''
    seen_pcis = []
    # Write per cell logs
    abs_time = log_row["companion_abs_time"]
    rel_time = log_row["rel_time"]
    
    for cell in log_row["cells"]:
        if options["csv_per_kpi"]:
            for kpi in cell:
                if kpi != "pci":
                    append_to_csv(get_csv_kpi_path(cell["pci"], kpi), cell[kpi])
            append_to_csv(get_csv_kpi_path(cell["pci"], "abs_time"), abs_time)
            append_to_csv(get_csv_kpi_path(cell["pci"], "rel_time"), rel_time)
        else:
            pass
        seen_pcis.append(cell["pci"])

    # Write connected cell logs
    connected_pci = log_row["connected_pci"]
    append_to_csv(get_csv_kpi_path("connected", "pci"), connected_pci)
    append_to_csv("abs_time.csv", abs_time)
    append_to_csv("rel_time.csv", rel_time)
    connected_index = log_row["connected_index"]
    if connected_pci != -1:
        connected_cell = log_row["cells"][connected_index]
        if options["csv_per_kpi"]:
            for kpi in connected_cell:
                if kpi != "pci":
                    append_to_csv(get_csv_kpi_path('connected', kpi), connected_cell[kpi])

    # Write metadata about seen cells
    append_to_csv(os.path.join(OUTPUT_FOLDER, 'num_seen_cells.csv', ), len(log_row["cells"]))
    append_to_csv(os.path.join(OUTPUT_FOLDER, 'seen_pci.csv'), seen_pcis)

def process_log(options):
    num_seen_bs = []
    abs_times = []
    handover_count = 0
    current_cell_pci = -1
    with open(PAWPRINTS_LOG_PATH) as f:
        log_rows = f.readlines()
        for log_row_string in log_rows:
           log_row = json.loads(log_row_string)
           process_log_row(log_row, options)
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


options = {"csv_per_kpi":True}
process_log(options)


