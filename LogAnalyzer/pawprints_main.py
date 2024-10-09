import os

################
# This section is to be changed by the user for each run
ROOT = "~/Work/AERPAW/ExperimentData/Oct_7_Elk/"
SESSION_PREFIXES = ["elkback"]
GENERATE_KMLs = True
ALT_COL = "constant_altitude"
########################

## User is not required to change the below code/settings
WIFI_SUFFIX = "_wifi_log.txt"
CELL_SUFFIX = "_log.txt"
POS_SUFFIX = "_location.txt"

WIFI_PROCESSED_SUFFIX = "wifi_info.csv"
CELL_PROCESSED_SUFFIX = "cell_info.csv"

for session_prefix in SESSION_PREFIXES:
    wifi_log = os.path.join(ROOT, session_prefix + WIFI_SUFFIX)
    cell_log = os.path.join(ROOT, session_prefix + CELL_SUFFIX)
    pos_log = os.path.join(ROOT, session_prefix + POS_SUFFIX)
    pos_processed = os.path.join(ROOT,  session_prefix + "_pos.csv")
    wifi_processed = os.path.join(ROOT,  session_prefix + "_" + WIFI_PROCESSED_SUFFIX)
    cell_processed = os.path.join(ROOT,  session_prefix + "_" + CELL_PROCESSED_SUFFIX)

    os.system("python3 pawprints_to_csv.py --input " + wifi_log + " --output-dir " + ROOT + " --prefix " + session_prefix + "_")
    os.system("python3 pawprints_to_csv.py --input " + cell_log + " --output-dir " + ROOT + " --prefix " + session_prefix + "_")
    os.system("python3 pawprints_gps_to_csv.py --input " + pos_log + " --output " + pos_processed)  
    # os.system("python3 pawprints_merge_logs.py -i " + wifi_processed + " -g " + pos_processed + " -o " + wifi_processed)
    os.system("python3 pawprints_merge_logs.py -i " + cell_processed + " -g " + pos_processed + " -o " + cell_processed)

    if GENERATE_KMLs:
        try:
            rsrp_cell_kml = os.path.join(ROOT,  session_prefix + "_cellular_connected_rsrp.kml")
            os.system("python3 generate_kpi_kml.py --input " + cell_processed + " --kpi rsrp -p connected --draw-type point --alt-col " + ALT_COL + " -o " + rsrp_cell_kml)
            
            rsrq_cell_kml = os.path.join(ROOT,  session_prefix + "_cellular_connected_rsrq.kml")
            os.system("python3 generate_kpi_kml.py --input " + cell_processed + " --kpi rsrq -p connected --draw-type point --alt-col " + ALT_COL + " -o " + rsrq_cell_kml)

        except Exception as e:
            input(e)
            continue

        # rssi_wifi_kml = os.path.join(ROOT,  session_prefix + "_wifi_connected_rssi.kml")
        # os.system("python3 generate_kpi_kml.py --input " + wifi_processed + " --kpi connected_rssi --alt-col " + ALT_COL + " --draw-type point -o " + rssi_wifi_kml)
        
        # rsrq_cell_kml = os.path.join(ROOT,  session_prefix + "_cellular_connected_rsrq.kml")
        # os.system("python3 generate_kpi_kml.py --input " + wifi_processed + " --kpi rsrq -p connected --draw-type point -o " + rsrq_cell_kml)

