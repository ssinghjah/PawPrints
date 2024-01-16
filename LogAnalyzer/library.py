import toml
CONFIG_PATH = "./log_format.toml"

def parse_for_viz(log_line):
    viz_info = init_viz_info()
    log_entries = log_line.split(",")
    if log_entries[LOG_CONFIG["LOG_TYPE_INDEX"]] == LOG_CONFIG["START_DELIM"]["CELLULAR"]:
        viz_info["type"] = "cellular"
        viz_info["abs_time"] = log_entries[LOG_CONFIG["CELLULAR_HEADER"]["ABS_TIME_INDEX"]]
        viz_info["num_bs_seen"] = log_entries[LOG_CONFIG["CELLULAR_HEADER"]["NUM_BS_SEEN_INDEX"]]
        # viz_info["connected_cell"] = {}
        iter_index = 0
        while iter_index < len(log_entries):
                    if log_entries[iter_index] == LOG_CONFIG["START_DELIM"]["CELL_INFO"]:
                        iter_index = process_BS_log(log_entries, iter_index, viz_info)
                    else:
                        iter_index += 1
        # info["connected_cell"]["rssi"] = log_entries
    result = {"status":1, "result":viz_info}
    print(result)
    return result

def parse_to_json(log_line):
    log_json = {}
    log_entries = log_line.split(",")
    if log_entries[LOG_CONFIG["LOG_TYPE_INDEX"]] == LOG_CONFIG["START_DELIM"]["CELLULAR"]:
        log_json["abs_time"] = int(log_entries[LOG_CONFIG["CELLULAR_HEADER"]["ABS_TIME_INDEX"]])
        log_json["rel_time"] = log_entries[LOG_CONFIG["CELLULAR_HEADER"]["REL_TIME_INDEX"]]
        log_json["num_cells_seen"] = int(log_entries[LOG_CONFIG["CELLULAR_HEADER"]["NUM_BS_SEEN_INDEX"]])
        log_json["type"] = "cellular"
        log_json["cells"] = {}
        log_json["connected_pci"] = -1 
        iter_index = 0
        while iter_index < len(log_entries):
                    if log_entries[iter_index] == LOG_CONFIG["START_DELIM"]["CELL_INFO"]:
                        iter_index = process_BS_log(log_entries, iter_index, log_json)
                    else:
                        iter_index += 1
    result = {"status":1, "result": log_json}
    return result


def init_viz_info():
     viz_info = {}
     viz_info["source_id"] = None
     viz_info["rssi"] = {}
     viz_info["rsrq"] = {}
     viz_info["rsrp"] = {}
     viz_info["cqi"] = {}
     viz_info["ci"] = {}
     viz_info["asu"] = {}
     viz_info["connected_pci"] = -1
     viz_info["network_type"] = ""
     viz_info["network_override"] = ""
     viz_info["freq_band"] = {}
     viz_info["earfcn"] = {}
     viz_info["mcc"] = {}
     viz_info["mnc"] = {}
     viz_info["bandwidth"] = {}
     viz_info["ta"] = {}
     viz_info["tac"] = {}     
     return viz_info

def process_BS_log(log_entries, iter_index, log_json):
    iter_index += 1
    if log_entries[iter_index] == LOG_CONFIG["LTE"]["INDICATOR"]:
       iter_index = process_LTE_log_for_json(log_entries, iter_index, log_json)
    else:
        # handle other cell technologies here
        pass
    return iter_index


def process_LTE_log_for_json(log_entries, iter_index, log_json):
    is_valid = log_entries[iter_index + LOG_CONFIG["LTE"]["END_INDEX"]] == LOG_CONFIG["END_DELIM"]["CELL_INFO"]
    if not is_valid:
         return
    
    pci = log_entries[iter_index + LOG_CONFIG["LTE"]["PCI_INDEX"]]
    if pci not in log_json["cells"]:
         log_json["cells"][pci] = {}
    log_json["cells"][pci]["ci"] = log_entries[iter_index + LOG_CONFIG["LTE"]["CI_INDEX"]]
    log_json["cells"][pci]["rssi"] = float(log_entries[iter_index + LOG_CONFIG["LTE"]["RSSI_INDEX"]])
    log_json["cells"][pci]["rsrq"] = float(log_entries[iter_index + LOG_CONFIG["LTE"]["RSRQ_INDEX"]])
    log_json["cells"][pci]["rsrp"] = float(log_entries[iter_index + LOG_CONFIG["LTE"]["RSRP_INDEX"]])
    log_json["cells"][pci]["cqi"] = log_entries[iter_index + LOG_CONFIG["LTE"]["CQI_INDEX"]]
    log_json["cells"][pci]["asu"] = int(log_entries[iter_index + LOG_CONFIG["LTE"]["ASU_INDEX"]])
    log_json["cells"][pci]["earfcn"] = log_entries[iter_index + LOG_CONFIG["LTE"]["EARFCN_INDEX"]]
    log_json["cells"][pci]["ta"] = log_entries[iter_index + LOG_CONFIG["LTE"]["TA_INDEX"]]
    log_json["cells"][pci]["tac"] = log_entries[iter_index + LOG_CONFIG["LTE"]["TAC_INDEX"]]
    log_json["cells"][pci]["bandwidth"] = log_entries[iter_index + LOG_CONFIG["LTE"]["BW_INDEX"]]
    log_json["cells"][pci]["mcc"] = log_entries[iter_index + LOG_CONFIG["LTE"]["MCC_INDEX"]]
    log_json["cells"][pci]["mnc"] = log_entries[iter_index + LOG_CONFIG["LTE"]["MNC_INDEX"]]
    log_json["cells"][pci]["is_connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["IS_CONNECTED_INDEX"]]


    is_connected = bool(log_entries[iter_index + LOG_CONFIG["LTE"]["IS_CONNECTED_INDEX"]])
    if is_connected:
       log_json["connected_pci"] = pci 

    iter_index += LOG_CONFIG["LTE"]["END_INDEX"]
    return iter_index

def process_LTE_log(log_entries, iter_index, viz_info):
    is_valid = log_entries[iter_index + LOG_CONFIG["LTE"]["END_INDEX"]] == LOG_CONFIG["END_DELIM"]["CELL_INFO"]
    if not is_valid:
         return
    
    pci = log_entries[iter_index + LOG_CONFIG["LTE"]["PCI_INDEX"]]
    viz_info["ci"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["CI_INDEX"]]
    viz_info["rssi"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["RSSI_INDEX"]]
    viz_info["rsrq"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["RSRQ_INDEX"]]
    viz_info["rsrp"][pci] = float(log_entries[iter_index + LOG_CONFIG["LTE"]["RSRP_INDEX"]])
    viz_info["cqi"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["CQI_INDEX"]]
    viz_info["asu"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["ASU_INDEX"]]
    viz_info["earfcn"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["EARFCN_INDEX"]]
    viz_info["ta"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["TA_INDEX"]]
    viz_info["tac"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["TAC_INDEX"]]
    viz_info["bandwidth"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["BW_INDEX"]]
    viz_info["mcc"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["MCC_INDEX"]]
    viz_info["mnc"][pci] = log_entries[iter_index + LOG_CONFIG["LTE"]["MNC_INDEX"]]

    is_connected = bool(log_entries[iter_index + LOG_CONFIG["LTE"]["IS_CONNECTED_INDEX"]])
    if is_connected:
         viz_info["connected_pci"] = pci
         viz_info["rssi"]["connected"] = viz_info["rssi"][pci]
         viz_info["ci"]["connected"] = viz_info["ci"][pci]
         viz_info["rsrq"]["connected"] = viz_info["rsrq"][pci]
         viz_info["rsrp"]["connected"] = viz_info["rsrp"][pci]
         viz_info["cqi"]["connected"] = viz_info["cqi"][pci]
         viz_info["asu"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["ASU_INDEX"]]
         viz_info["earfcn"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["EARFCN_INDEX"]]
         viz_info["ta"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["TA_INDEX"]]
         viz_info["tac"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["TAC_INDEX"]]
         viz_info["bandwidth"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["BW_INDEX"]]
         viz_info["mcc"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["MCC_INDEX"]]
         viz_info["mnc"]["connected"] = log_entries[iter_index + LOG_CONFIG["LTE"]["MNC_INDEX"]]

    iter_index += LOG_CONFIG["LTE"]["END_INDEX"]
    return iter_index

def read_config():
    log_config = {}
    with open(CONFIG_PATH, 'r') as f:
        log_config = toml.load(f)
    return log_config

LOG_CONFIG = read_config()

    
    
