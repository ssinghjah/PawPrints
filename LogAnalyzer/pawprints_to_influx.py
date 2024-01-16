import library
import time, datetime
import os
import pytz

BUCKET="PawPrints" 
ORG ="AerialWireless"
URL="http://localhost:8086"
ORG = "AerialWireless"
TOKEN = "PQg-9gCEe2Iut_CRyfsQ_K_e9ym1rPM_b-xoahFQsoXJcNHui0DtwOm0EDUwsGDOu32tB7BAzJk68aCrx1PD5Q=="

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# # Read log line by line
# # Convert log line into JSON
# # Iterate over cells in the log line
# # Get all KPIs of the cell

# for value in range(5):
#   rsrp = -106
#   point = (
#     Point("cellular")
#     .tag("pci", "connected")
#     .field("rsrp", rsrp + 1)
#   )
#   write_api.write(bucket=bucket, org=ORG, record=point)
#   time.sleep(1) # separate points by 1 second

# query_api = client.query_api()

# query = """from(bucket: "PawPrints")
#  |> range(start: -10m)
#  |> filter(fn: (r) => r._measurement == "cellular")"""
# tables = query_api.query(query, org=ORG)

# for table in tables:
#   for record in table.records:
#     print(record)

LOG_PATH = "./pawprints_log.txt"
STREAM_INTERVAL = 1 # seconds
SOURCE_NAME = "Helikite"

def read_stream_from_log():
    with open(LOG_PATH) as f:
        log_lines = f.readlines()
        for log_line in log_lines:
          
           parse_result = library.parse_to_json(log_line)
           if parse_result["status"] == 1:
               log_json = parse_result["result"]
               if log_json["num_cells_seen"] > 0:
                   for cell in log_json["cells"]:
                        influx_data = {}
                        influx_data["measurement"] = "cellular"
                        influx_data["fields"] = {}
                        influx_data["tags"] = {}
                        time_obj = datetime.datetime.fromtimestamp(log_json["abs_time"]/1e3)
                        eastern_tz = pytz.timezone('US/Eastern')
                        time_obj = eastern_tz.localize(time_obj)
                        influx_data["time"] = time_obj.isoformat()                        
                        influx_data["tags"]["cell_pci"] = cell
                        for kpi in log_json["cells"][cell]:
                          influx_data["fields"][kpi] = log_json["cells"][cell][kpi]
                        print(influx_data)
                        print(write_api.write(bucket=BUCKET, token=TOKEN, org=ORG, record = influx_data))

                        if log_json["cells"][cell]["is_connected"] == "TRUE":
                          influx_data["tags"]["cell_pci"] = "connected"
                          print(write_api.write(bucket=BUCKET, token=TOKEN, org=ORG, record = influx_data))

                

                           
           time.sleep(0.3)

read_stream_from_log()