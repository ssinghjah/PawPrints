import csv

LOG_PATH = "./pawprints_log.txt"
REL_TIME_INDEX = 2
PCI_INDEX = 12
CI_INDEX = 14
SIG_STRENGTH_INDEX = 4
RSSNR_INDEX = 5
RSRP_INDEX = 6
RSRQ_INDEX = 7
RSSI_INDEX = 8
CQI_INDEX = 9
BS_LOG_START = "BS_INFO_START"
BS_LOG_END = "BS_INFO_STOP"

# Index Map

def write_files(parsed_measurements):
    for cell_id in parsed_measurements:
        for cell_param in parsed_measurements[cell_id]:
            fName = cell_id + "_" + cell_param + ".csv"
            values = parsed_measurements[cell_id][cell_param]
            with open(fName, 'w') as f:
                csv_writer = csv.writer(f)
                for value in values:
                    csv_writer.writerow([value])

def process_LTE_log(log_entries, iter_index, parsed_measurements):
    pci = log_entries[iter_index + PCI_INDEX]
    ci = log_entries[iter_index + CI_INDEX]

    if pci not in parsed_measurements:
        parsed_measurements[pci] = {}
        parsed_measurements[pci]["rel_time"] = []
        parsed_measurements[pci]["sig_strength"] = []
        parsed_measurements[pci]["rsrp"] = []
        parsed_measurements[pci]["rsrq"] = []
        parsed_measurements[pci]["rssnr"] = []
        parsed_measurements[pci]["rssi"] = []
        parsed_measurements[pci]["cqi"] = []

    parsed_measurements[pci]["sig_strength"].append(log_entries[iter_index + SIG_STRENGTH_INDEX])
    parsed_measurements[pci]["rsrp"].append(log_entries[iter_index + RSRP_INDEX])
    parsed_measurements[pci]["rsrq"].append(log_entries[iter_index + RSRQ_INDEX])
    parsed_measurements[pci]["rssnr"].append(log_entries[iter_index + RSSNR_INDEX])
    parsed_measurements[pci]["rssi"].append(log_entries[iter_index + RSSI_INDEX])
    parsed_measurements[pci]["cqi"].append(log_entries[iter_index + CQI_INDEX])
    parsed_measurements[pci]["rel_time"].append(log_entries[iter_index + REL_TIME_INDEX])

    while log_entries[iter_index] != BS_LOG_END:
        iter_index +=1
    return iter_index



def process_BS_log(log_entries, iter_index, parsed_measurements):
    iter_index += 1
    if log_entries[iter_index] == "4G_LTE":
       iter_index = process_LTE_log(log_entries, iter_index, parsed_measurements)
    else:
        # handle other cell technologies here
        pass
    return iter_index
def process_log():
    parsed_measurements = {}
    with open(LOG_PATH) as f:
        log_rows = f.readlines()
        for log_row in log_rows:
            log_entries = log_row.split(",")
            iter_index = 0
            while iter_index < len(log_entries):
                if log_entries[iter_index] == BS_LOG_START:
                    iter_index = process_BS_log(log_entries, iter_index, parsed_measurements)
                else:
                    iter_index += 1

    write_files(parsed_measurements)



process_log()


