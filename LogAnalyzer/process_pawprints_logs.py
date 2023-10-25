import csv
import common

LOG_FOLDER = "../Data/"
PAWPRINTS_LOG_PATH = "../Data/pawprints_log.txt"

# 4G LTE SECTION INDICES
REL_TIME_INDEX = 2
PCI_INDEX = 12
CI_INDEX = 14
SIG_STRENGTH_INDEX = 4
RSSNR_INDEX = 5
RSRP_INDEX = 6
RSRQ_INDEX = 7
ASU_INDEX = 10
RSSI_INDEX = 8
CQI_INDEX = 9

IS_CONNECTED_INDEX = 1

# WRAPPER SECTION INDICES
ABS_TIME_INDEX = 1
NUM_BS_SEEN_INDEX = 3

BS_LOG_START = "BS_INFO_START"
BS_LOG_END = "BS_INFO_STOP"

# Index Map
def write_per_bs_measurements(per_bs_measurements):
    for cell_id in per_bs_measurements:
        for cell_param in per_bs_measurements[cell_id]:
            fName = LOG_FOLDER + cell_id + "_" + cell_param + ".csv"
            values = per_bs_measurements[cell_id][cell_param]
            with open(fName, 'w') as f:
                csv_writer = csv.writer(f)
                # csv_writer.writerow([cell_param])
                for value in values:
                    csv_writer.writerow([value])
def write_connected_cell_info(connected_bs_measurements):
    for cell_param in connected_bs_measurements:
        fName = LOG_FOLDER + "connected_bs_" + cell_param + ".csv"
        values = connected_bs_measurements[cell_param]
        with open(fName, 'w') as f:
            csv_writer = csv.writer(f)
            # csv_writer.writerow([cell_param])
            for value in values:
                csv_writer.writerow([value])

def write_pcis(per_bs_measurements):
    cell_ids = per_bs_measurements.keys()
    fName = LOG_FOLDER + "bs_pci.csv"
    with open(fName, 'w') as f:
        csv_writer = csv.writer(f)
        for value in cell_ids:
            csv_writer.writerow([value])
def write_total_seen_time(per_bs_measurements):
    cell_ids = per_bs_measurements.keys()
    fName = LOG_FOLDER + "bs_seen_time.csv"
    with open(fName, 'w') as f:
        csv_writer = csv.writer(f)
        # csv_writer.writerow(["pci", "seen_time"])
        for cell_id in cell_ids:
            csv_writer.writerow([cell_id, len(per_bs_measurements[cell_id]["rel_time"])])

def initialize_bs_info(bs_info):
    bs_info["rel_time"] = []
    bs_info["abs_time"] = []
    bs_info["sig_strength"] = []
    bs_info["rsrp"] = []
    bs_info["rsrq"] = []
    bs_info["rssnr"] = []
    bs_info["rssi"] = []
    bs_info["cqi"] = []
    bs_info["ci"] = []
    bs_info["asu"] = []


def analyze_rsrp_rsrq_quality(connected_bs_info):
    num_entries = len(connected_bs_info["rsrq"])
    for entry_index in range(num_entries):
        rsrq = connected_bs_info["rsrq"]
        rsrp = connected_bs_info["rsrp"]



def append_to_bs_info(bs_info, log_entries, iter_index, abs_time):
    bs_info["sig_strength"].append(log_entries[iter_index + SIG_STRENGTH_INDEX])
    bs_info["rsrp"].append(log_entries[iter_index + RSRP_INDEX])
    bs_info["rsrq"].append(log_entries[iter_index + RSRQ_INDEX])
    bs_info["rssnr"].append(log_entries[iter_index + RSSNR_INDEX])
    bs_info["rssi"].append(log_entries[iter_index + RSSI_INDEX])
    bs_info["cqi"].append(log_entries[iter_index + CQI_INDEX])
    bs_info["rel_time"].append(log_entries[iter_index + REL_TIME_INDEX])
    bs_info["ci"].append(log_entries[iter_index + CI_INDEX])
    bs_info["abs_time"].append(abs_time)
    bs_info["asu"].append(log_entries[iter_index + ASU_INDEX])

def process_LTE_log(abs_time, log_entries, iter_index, per_bs_measurements, connected_bs_info):
    pci = log_entries[iter_index + PCI_INDEX]
    ci = log_entries[iter_index + CI_INDEX]

    if pci not in per_bs_measurements:
        per_bs_measurements[pci] = {}
        initialize_bs_info(per_bs_measurements[pci])

    append_to_bs_info(per_bs_measurements[pci], log_entries, iter_index, abs_time)

    if log_entries[iter_index + IS_CONNECTED_INDEX] == "TRUE":
        append_to_bs_info(connected_bs_info, log_entries, iter_index, abs_time)
        connected_bs_info["pci"][-1] = pci

    while log_entries[iter_index] != BS_LOG_END:
        iter_index +=1

    return iter_index
def process_BS_log(abs_time, log_entries, iter_index, per_bs_measurements, connected_bs_info):
    iter_index += 1
    if log_entries[iter_index] == "4G_LTE":
       iter_index = process_LTE_log(abs_time, log_entries, iter_index, per_bs_measurements, connected_bs_info)
    else:
        # handle other cell technologies here
        pass
    return iter_index

def process_log():
    per_bs_measurements = {}
    connected_bs_info = {}
    initialize_bs_info(connected_bs_info)
    num_seen_bs = []
    abs_times = []
    connected_bs_info["pci"] = []
    handover_count = 0
    with open(PAWPRINTS_LOG_PATH) as f:
        log_rows = f.readlines()
        for log_row in log_rows:
            connected_bs_info["pci"].append(-1)
            log_entries = log_row.split(",")
            iter_index = 0
            abs_time = log_entries[ABS_TIME_INDEX]
            abs_times.append(abs_time)
            num_seen_bs.append(log_entries[NUM_BS_SEEN_INDEX])
            while iter_index < len(log_entries):
                if log_entries[iter_index] == BS_LOG_START:
                    iter_index = process_BS_log(abs_time, log_entries, iter_index, per_bs_measurements, connected_bs_info)
                else:
                    iter_index += 1
            if len(connected_bs_info["pci"]) > 1 and (connected_bs_info["pci"][-1] != connected_bs_info["pci"][-2]):
                handover_count += 1

    write_per_bs_measurements(per_bs_measurements)
    write_connected_cell_info(connected_bs_info)
    write_total_seen_time(per_bs_measurements)
    common.write_csv(LOG_FOLDER + "num_seen_bs.csv", num_seen_bs)
    common.write_csv(LOG_FOLDER + "pawprints_abs_time.csv", abs_times)
    print(handover_count)

process_log()


