import argparse
import pandas
import math
from datetime import datetime

DEFAULT_NEMO_PATH = "./nemo.csv"
DEFAULT_OUTPUT_PATH = "./nemo_processed.csv"
DATE = "2024-4-15" # Year, Month, Date
COMPANION_TIME_OFFSET_MINUTES = 90 # Minutes

def processNemo(raw_nemo_path, processed_log_path):
    nemo_raw_df = pandas.read_csv(raw_nemo_path)
    nemo_non_empty_rows =  nemo_raw_df[nemo_raw_df["Physical layer identity (LTE detected)"].notna()]
    print(nemo_non_empty_rows)
    processed_nemo_json = {}
    # Initialize processed json with fields as the columns of the raw nemo dataframe
    for col in nemo_raw_df.columns:
        print(col)
        processed_nemo_json[col] = []
    
    processed_nemo_json["abs_time_ms"] = []

    # Loop over PCIs. Split PCIs and append KPI of each unique PCI to the corresponding field of the JSON.
    # This assumes that number of PCI entries = number of KPI entries, per row, in raw nemo dataframe.
    for index, row in nemo_non_empty_rows.iterrows():
        pcis_str = row["Physical layer identity (LTE detected)"]
        pci_arr = pcis_str.split(",")
        num_pcis = len(pci_arr)
        
        for kpi_name in processed_nemo_json:
            # If the KPI is not time, split the string to array, validate with pci count, and store in json. 
            if "time" not in kpi_name.lower():
                kpi_arr = row[kpi_name]
                if isinstance(kpi_arr, (int, float)) and math.isnan(kpi_arr): 
                    kpi_arr = [kpi_arr for i in range(num_pcis)]
                else:
                    kpi_arr = kpi_arr.split(",")
                    if len(kpi_arr) != num_pcis:
                        raise Exception("Nemo parsing error. KPI count != PCI cell count.")

                for kpi_val in kpi_arr:
                    processed_nemo_json[kpi_name].append(kpi_val)

            elif kpi_name.lower() == "abs_time_ms":
                    time_str = row["Time"]
                    time_obj = datetime.strptime(DATE + " " + time_str, "%Y-%m-%d %H:%M:%S")
                    time_ms = time_obj.timestamp() * 1000.0
                    time_ms += COMPANION_TIME_OFFSET_MINUTES*60*1000.0
                    processed_nemo_json["companion_abs_time_ms"].extend([time_ms for i in range(num_pcis)])   
            else:
                processed_nemo_json[kpi_name].extend([row[kpi_name] for i in range(num_pcis)])
    

    processed_nemo_df = pandas.DataFrame(processed_nemo_json)
    processed_nemo_df.to_csv(processed_log_path)


if __name__ == "__main__":
    processNemo(raw_nemo_path=DEFAULT_NEMO_PATH, processed_log_path=DEFAULT_OUTPUT_PATH)