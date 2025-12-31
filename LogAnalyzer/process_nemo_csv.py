import argparse
import pandas
import math
import time_merger
import common
from datetime import datetime
import gps_log_time_syncer

# Settings
LTE_CELL_ID_FIELD = "Physical layer identity (LTE detected)"
NR_CELL_ID_FIELD = "Physical cell identity (NR SpCell)"

DEFAULT_GPS_PATH = r"C:\Users\ssingh28\PawPrints\LogAnalyzer\Workspace/companion_gps_processed.csv"
DEFAULT_NEMO_PATH = r"C:\Users\ssingh28\PawPrints\LogAnalyzer\Workspace/nemo.csv"
DEFAULT_OUTPUT_PATH = r"C:\Users\ssingh28\PawPrints\LogAnalyzer\Workspace/nemo_processed.csv"
DEFAULT_NEMO_GPS_PATH = r"C:\Users\ssingh28\PawPrints\LogAnalyzer\Workspace/nemo_gps_processed.csv"
DEFAULT_GPS_SOURCE = "companion"

DATE = "2025-09-08" # Year, Month, Date
COMPANION_TIME_OFFSET_MS = -12524069.802978516 # milliseconds 
HEIGHT_OFFET = 78

TIME_COLUMNS = ["time", "active time", "companion_abs_time_ms"] # Columns representing time fields. These are duplicated when exploding KPI rows (i.e. comma-separated multiple KPI entries in a single row)

def _splitCellValue(cellValue):
    if isinstance(cellValue, (int, float)): 
        cell_arr = [cell_arr for i in range(cellValue)]
    else:
        cell_arr = cellValue.split(",")
    return cell_arr

def _isSeriesNonNaN(pd_series):
    return False in pandas.isna(pd_series).unique()    

def _isVariableNaN(var):
    return isinstance(var, (float, int)) and math.isnan(var)

def _validTimeFormat(time_str):
    try:
        datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return True
    except Exception as e:
        return False

def _processLog(nemo_raw_df, processed_nemo_json, companion_time_offset):
    for index, row in nemo_raw_df.iterrows():
        print(index)
        if not _validTimeFormat(row["time"]):
            continue

        # row["Time"] = DATE + " " + row["Time"]

        # Dont process a row with Time as NaN.  
        if _isVariableNaN(row["time"]):
            continue

        if not _isSeriesNonNaN(row.drop("time")):
            continue

        for kpi_name in processed_nemo_json:
            if kpi_name.lower() == "companion_abs_time_ms":
                time_str = row["time"]
                time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
                time_ms = time_obj.timestamp() * 1000.0
                time_ms += companion_time_offset
                processed_nemo_json["companion_abs_time_ms"].append(time_ms)  
            else:
                processed_nemo_json[kpi_name].append(row[kpi_name])

def _processRadioLog(nemo_raw_df, processed_nemo_json, cell_id_col, companion_time_offset):
    # Loop over PCIs. Split PCIs and append KPI of each unique PCI to the corresponding field of the JSON.
    # This assumes that number of PCI entries = number of KPI entries, per row, in raw nemo dataframe.
    row_type = "downlink"
    for index, row in nemo_raw_df.iterrows():
        print(index)
        if not _validTimeFormat(row["time"]):
            continue

        # Dont process a row with Time as NaN.  
        if _isVariableNaN(row["time"]):
            continue

        if not _isSeriesNonNaN(row.drop("time")):
            continue
        
        pcis_str = row[cell_id_col]
        if not isinstance(pcis_str, str) and math.isnan(pcis_str):
            # PCI is NaN for a row with Uplink info. Dont encapsulate pcis in an array.
            row_type = "uplink"
            num_exploded_rows = 1
        elif isinstance(pcis_str, (int, float)):
            row_type = "downlink"
            pci_arr = [pcis_str]
            num_exploded_rows = len(pci_arr)
        elif isinstance(pcis_str, str):
            row_type = "downlink"
            pci_arr = pcis_str.split(",")
            num_exploded_rows = len(pci_arr)
    
        # row["Time"] = DATE + " " + row["Time"]
        for kpi_name in processed_nemo_json:
            # If the KPI is not time, split the string to array, validate with pci count, and store in json. 
            if kpi_name.lower() not in TIME_COLUMNS:
                kpi_arr = row[kpi_name]

                if row_type == "uplink":
                    kpi_arr = [row[kpi_name]]
                elif isinstance(kpi_arr, (int, float)): 
                    kpi_arr = [kpi_arr for i in range(num_exploded_rows)]
                else:
                    kpi_arr = kpi_arr.split(",")
                    if len(kpi_arr) != len(pci_arr):
                        raise Exception("Nemo parsing error. KPI count != PCI cell count.")

                for kpi_val in kpi_arr:
                    processed_nemo_json[kpi_name].append(kpi_val)

            elif kpi_name.lower() == "companion_abs_time_ms":
                    time_str = row["time"]
                    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    time_ms = time_obj.timestamp() * 1000.0
                    time_ms -= companion_time_offset
                    processed_nemo_json["companion_abs_time_ms"].extend([time_ms for i in range(num_exploded_rows)])   
            else:
                processed_nemo_json[kpi_name].extend([row[kpi_name] for i in range(num_exploded_rows)])
            

def processNemo(options):
    nemo_raw_df = pandas.read_csv(options.nemo_log)
    cell_id_col = LTE_CELL_ID_FIELD if LTE_CELL_ID_FIELD in nemo_raw_df.columns else NR_CELL_ID_FIELD if NR_CELL_ID_FIELD in nemo_raw_df.columns else None 
    
    nemo_raw_df.dropna(axis=1, how="all") # Supposed to drop NaN rows but it does not. I drop it manually below.
    processed_nemo_json = {}

    companion_time_offset = None
    ref_time = None
    if options.time_offset:
        processed_nemo_json["companion_abs_time_ms"] = []
        companion_time_offset, ref_time = gps_log_time_syncer.run(ref_gps_path = options.gps_log, to_sync_gps_path = options.nemo_gps_path)
        # companion_time_offset = -1719947158074 + 1719934631306.83
        # ref_time = 1719934631306.83

    # Initialize processed json with fields as the columns of the raw nemo dataframe
    for col in nemo_raw_df.columns:
        print(col)
        if _isSeriesNonNaN(nemo_raw_df[col]):
            processed_nemo_json[col] = []

    if cell_id_col is not None:
        _processRadioLog(nemo_raw_df, processed_nemo_json, cell_id_col, companion_time_offset)
    else:
        _processLog(nemo_raw_df, processed_nemo_json, companion_time_offset)

    processed_nemo_df = pandas.DataFrame(processed_nemo_json)
    print("Raw cols = " + str((nemo_raw_df.shape[1])))
    print("Processed cols = " + str((processed_nemo_df.shape[1])))

    print("Raw rows = " + str((nemo_raw_df.shape[0])))
    print("Processed rows = " + str((processed_nemo_df.shape[0])))
    # processed_nemo_df["nemo_abs_time"] = processed_nemo_df["time"].apply(common.format_gps_times)

    if options.gps_log is not None:
        gps_data = pandas.read_csv(options.gps_log)
        if options.gps_source == "companion":
            # gps_data["gps_times"] = gps_data.iloc[:, 7].apply(common.format_gps_times)
            interp_locs = time_merger.merge_locs(processed_nemo_df["companion_abs_time_ms"].to_list(), gps_data["time_ms"].to_list(), gps_data["latitude"], gps_data["longitude"], gps_data["altitude"])
            processed_nemo_df["longitude"] = interp_locs["longitude"]
            processed_nemo_df["latitude"] = interp_locs["latitude"]
            processed_nemo_df["altitude"] = interp_locs["altitude"]
            processed_nemo_df["rel_time"] = processed_nemo_df["companion_abs_time_ms"] - ref_time 

        elif options.gps_source == "nemo":
            gps_data.drop_duplicates()
            gps_data["Time"] = DATE + " " + gps_data["Time"]
            gps_data["nemo_abs_time"] = gps_data["Time"].apply(common.format_gps_times)
            interp_locs = time_merger.merge_locs(processed_nemo_df["nemo_abs_time"].to_list(), gps_data["nemo_abs_time"].to_list(), gps_data["Latitude"], gps_data["Longitude"], gps_data["Height"])
            processed_nemo_df["longitude"] = interp_locs["longitude"]
            processed_nemo_df["latitude"] = interp_locs["latitude"]
            processed_nemo_df["altitude"] = interp_locs["altitude"]
            
    processed_nemo_df.to_csv(options.output, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Nemo csv log')
    parser.add_argument("-g", "--gps-log", type=str, default=DEFAULT_GPS_PATH, help="Input GPS log")
    parser.add_argument('-i', '--nemo-log', type = str, default = DEFAULT_NEMO_PATH, help='Input raw nemo log')
    parser.add_argument('-o', '--output', type = str, default = DEFAULT_OUTPUT_PATH, help='Output processed nemo csv')
    parser.add_argument('--time-offset', action = "store_true", default = True, help='Option to apply a time offset, with respect to companion computer')
    parser.add_argument('--nemo-gps-path', type = str, default = DEFAULT_NEMO_GPS_PATH, help='Nemo GPS path')
    parser.add_argument('--gps-source', type= str, default = DEFAULT_GPS_SOURCE, help='Source of GPS log. Supported sources are companion or nemo')
    options = parser.parse_args()
    processNemo(options)