import library
import time, datetime
import os
import pytz
import json

URL="http://localhost:8086"
ORG = "aerpaw"
TOKEN = "WhbRxhbE2aA8_IPfKp3ddov8-uwq9iS2K72l31aF9GPu4f5Me4JSQXCQ1MqhXmIVvTbsxBUCBAhTcFoa8itKUw=="

import os, time
from influxdb_client import InfluxDBClient, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
buckets_api = BucketsApi(client)


LOG_PATH = "./pawprints.jsonl"
STREAM_INTERVAL = 1 # seconds
SOURCE_NAME = "Helikite"
BUCKET_RETENTION_PERIOD = 24 * 180

def create_bucket_if_doesnt_exists(bucket_name):
    # Check if bucket exists
    buckets = buckets_api.find_buckets().buckets
    bucket_exists = any(bucket.name == bucket_name for bucket in buckets)

    # Create bucket if it doesn't exist
    if not bucket_exists:
        retention_period_seconds = BUCKET_RETENTION_PERIOD * 3600
        bucket_properties = {
            "orgID": "4781933da1b268d0",
            "name": bucket_name,
            "retentionRules": [{"type": "expire", "everySeconds": retention_period_seconds}],
        }
        buckets_api.create_bucket(bucket_properties)

def read_stream_from_log():
    created_buckets = []
    bucket_name = "PawPrints"
    with open(LOG_PATH) as f:
        log_lines = f.readlines()
        for log_line in log_lines:
            log_line_json = json.loads(log_line)
            # bucket_name = log_line_json["device_name"] + "-" + log_line_json["campaign_name"]
            
            if bucket_name not in created_buckets:
                create_bucket_if_doesnt_exists(bucket_name)
                created_buckets.append(bucket_name)

            abs_time = log_line_json["abs_time"]
            rel_time = log_line_json["rel_time"]
            time_obj = datetime.datetime.fromtimestamp(abs_time/1e3)
            eastern_tz = pytz.timezone('US/Eastern')
            influx_time = eastern_tz.localize(time_obj).isoformat()

            if log_line_json["type"] == "cellular":
                for cell in log_line_json["cells"]:
                    influx_data = {"fields":{"rel_time": rel_time}, 
                                   "tags":{}, 
                                   "measurement": log_line_json["type"],
                                   "time": influx_time
                                   }
                    influx_data["tags"]["device_name"] = log_line_json["device_name"]
                    influx_data["tags"]["campaign_name"] = log_line_json["campaign_name"]
                    influx_data["tags"]["pci"] = cell["pci"]
                    for key in cell:
                        if key != "pci":
                            influx_data["fields"][key] = cell[key]

                influx_data["tags"]["device_name"] = log_line_json["device_name"]
                influx_data["tags"]["campaign_name"] = log_line_json["campaign_name"]
                for key in cell:
                    if key != "pci":
                        influx_data["fields"][key] = cell[key]


            write_api.write(bucket=bucket_name, token=TOKEN, org=ORG, record=influx_data)

            if cell == log_line_json["connected_pci"]:
                influx_data["tags"]["pci"] = "connected"
                write_api.write(bucket=bucket_name, token=TOKEN, org=ORG, record=influx_data)
                    
            time.sleep(0.3)

# print(created_buckets)
        # influx_data["tags"]["type"] = "ue"
        # influx_data["fields"]["lat"] = ue["current_position_lla"][0]
        # influx_data["fields"]["lon"] = ue["current_position_lla"][1]
        # influx_data["fields"]["alt"] = float(ue["current_position_lla"][2])
        # write_api.write(bucket=BUCKET, token=TOKEN, org=ORG, record = data)
           
          #  parse_result = library.parse_to_json(log_line)
          #  if parse_result["status"] == 1:
          #      log_json = parse_result["result"]
          #      if log_json["num_cells_seen"] > 0:
          #          for cell in log_json["cells"]:
          #               influx_data = {}
          #               influx_data["measurement"] = "cellular"
          #               influx_data["fields"] = {}
          #               influx_data["tags"] = {}
          #               time_obj = datetime.datetime.fromtimestamp(log_json["abs_time"]/1e3)
          #               eastern_tz = pytz.timezone('US/Eastern')
          #               time_obj = eastern_tz.localize(time_obj)
          #               influx_data["time"] = time_obj.isoformat()                        
          #               influx_data["tags"]["cell_pci"] = cell
          #               for kpi in log_json["cells"][cell]:
          #                 influx_data["fields"][kpi] = log_json["cells"][cell][kpi]
          #               print(influx_data)
          #               print(write_api.write(bucket=BUCKET, token=TOKEN, org=ORG, record = influx_data))

          #               if log_json["cells"][cell]["is_connected"] == "TRUE":
          #                 influx_data["tags"]["cell_pci"] = "connected"
          #                 print(write_api.write(bucket=BUCKET, token=TOKEN, org=ORG, record = influx_data))

                

                           
        #   

read_stream_from_log()
