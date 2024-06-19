import argparse
import pandas
import math
import time_merger
import common
from datetime import datetime

# Settings
LTE_CELL_ID_FIELD = "Physical layer identity (LTE detected)"
NR_CELL_ID_FIELD = "Physical cell identity (NR SpCell)"

DEFAULT_NEMO_PATH = "./WorkSpace/nemo.csv"
DEFAULT_OUTPUT_PATH = "./WorkSpace/nemo_processed.csv"
DEFAULT_GPS_PATH = "./WorkSpace/gps.csv"
DEFAULT_GPS_SOURCE = "companion"

DATE = "2024-4-09" # Year, Month, Date
COMPANION_TIME_OFFSET_MS = (1*60*60)*1000 + (55*60)*1000 + (53.827037*1000) # Hours, min, sec to Milliseconds

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
        datetime.strptime(time_str, "%H:%M:%S.%f")
        return True
    except Exception as e:
        return False


def processNemo(options):
    nemo_raw_df = pandas.read_csv(options.nemo_log)
    CELL_ID_COL_NAME = LTE_CELL_ID_FIELD if LTE_CELL_ID_FIELD in nemo_raw_df.columns else NR_CELL_ID_FIELD if NR_CELL_ID_FIELD in nemo_raw_df.columns else None 
    # nemo_non_empty_rows =  nemo_raw_df[nemo_raw_df[CELL_ID_COL_NAME].notna()]
    # print(nemo_non_empty_rows)
    nemo_raw_df.dropna(axis=1, how="all")
    processed_nemo_json = {}
    # Initialize processed json with fields as the columns of the raw nemo dataframe
    for col in nemo_raw_df.columns:
        print(col)
        if _isSeriesNonNaN(nemo_raw_df[col]):
            processed_nemo_json[col] = []
        else:
            pass
    
    if options.time_offset:
        processed_nemo_json["companion_abs_time_ms"] = []

    # Loop over PCIs. Split PCIs and append KPI of each unique PCI to the corresponding field of the JSON.
    # This assumes that number of PCI entries = number of KPI entries, per row, in raw nemo dataframe.
    row_type = "downlink"
    for index, row in nemo_raw_df.iterrows():
        print(index)
        if not _validTimeFormat(row["Time"]):
            continue

        # Dont process a row with Time as NaN.  
        if _isVariableNaN(row["Time"]):
            continue

        if not _isSeriesNonNaN(row.drop("Time")):
            continue
        
        pcis_str = row[CELL_ID_COL_NAME]
        if not isinstance(pcis_str, str) and math.isnan(pcis_str):
            # PCI is NaN for a row with Uplink info. Dont encapsulate in pcis in an array.
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
                    time_str = row["Time"]
                    time_obj = datetime.strptime(DATE + " " + time_str, "%Y-%m-%d %H:%M:%S.%f")
                    time_ms = time_obj.timestamp() * 1000.0
                    time_ms += COMPANION_TIME_OFFSET_MS
                    processed_nemo_json["companion_abs_time_ms"].extend([time_ms for i in range(num_exploded_rows)])   
            else:
                processed_nemo_json[kpi_name].extend([row[kpi_name] for i in range(num_exploded_rows)])
        pass
    
    processed_nemo_df = pandas.DataFrame(processed_nemo_json)
    print("Raw cols = " + str((nemo_raw_df.shape[1])))
    print("Processed cols = " + str((processed_nemo_df.shape[1])))

    print("Raw rows = " + str((nemo_raw_df.shape[0])))
    print("Processed rows = " + str((processed_nemo_df.shape[0])))

    if options.gps_log is not None:
        gps_data = pandas.read_csv(options.gps_log)
        if options.gps_source == "companion":
            gps_data["gps_times"] = gps_data.iloc[:, 7].apply(common.format_gps_times)
            cell_indices, gps_indices = time_merger.merge(processed_nemo_df["companion_abs_time_ms"].to_list(), gps_data["gps_times"], mode=1, to_csv=True) 
            processed_nemo_df["longitude"] = gps_data.iloc[gps_indices, 1].to_list()
            processed_nemo_df["latitude"] = gps_data.iloc[gps_indices, 2].to_list()
            processed_nemo_df["altitude"] = gps_data.iloc[gps_indices, 3].to_list()
        elif options.gps_source == "nemo":
            pass

    processed_nemo_df.to_csv(options.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Nemo csv log')
    parser.add_argument("-g", "--gps-log", type=str, default=None, help="Input GPS log")
    parser.add_argument('-i', '--nemo-log', type = str, default = DEFAULT_NEMO_PATH, help='Input raw nemo log')
    parser.add_argument('-o', '--output', type = str, default = DEFAULT_OUTPUT_PATH, help='Output processed nemo csv')
    parser.add_argument('--time-offset', action = "store_true", default = False, help='Option to apply a time offset, with respect to companion computer')
    parser.add_argument('--gps-source', type= str, default = DEFAULT_GPS_SOURCE, help='Source of GPS log. Supported sources are companion or nemo')
    options = parser.parse_args()
    processNemo(options)