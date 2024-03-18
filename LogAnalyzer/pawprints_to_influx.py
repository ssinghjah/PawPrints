import library
import time, datetime
import os
import pytz
import json
import argparse

DEFAULT_URL="http://localhost:8086"
DEFAULT_ORG = "aerpaw"
DEFAULT_TOKEN = "WhbRxhbE2aA8_IPfKp3ddov8-uwq9iS2K72l31aF9GPu4f5Me4JSQXCQ1MqhXmIVvTbsxBUCBAhTcFoa8itKUw=="

import os, time
from influxdb_client import InfluxDBClient, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS


DEFAULT_LOG_PATH = "./pawprints.jsonl"
THROTTLE = 0.3 # seconds
BUCKET_RETENTION_PERIOD = 24 * 180 # 180 days * 24 hours per day

def create_bucket_if_doesnt_exists(buckets_api, bucket_name):
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

def run(options):
    client = InfluxDBClient(url=options.url, token=options.token, org=options.org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    buckets_api = BucketsApi(client)

    created_buckets = []
    with open(options.input) as f:
        log_lines = f.readlines()
        for log_line in log_lines:
            log_line_json = json.loads(log_line)

            if options.bucket == None:
                bucket_name = log_line_json["device_name"] + "-" + log_line_json["campaign_name"]
            else:
                bucket_name = options.bucket_name

            if bucket_name not in created_buckets:
                create_bucket_if_doesnt_exists(buckets_api, bucket_name)
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


            write_api.write(bucket=bucket_name, token=options.token, org=options.org, record=influx_data)

            if cell == log_line_json["connected_pci"]:
                influx_data["tags"]["pci"] = "connected"
                write_api.write(bucket=bucket_name, token=options.token, org=options.org, record=influx_data)
            
            if options.verbose:
                print(f"Writing time step: {rel_time} s")
            time.sleep(THROTTLE)

    print("Created buckets:")
    print(created_buckets)

if __name__ == "__main__":
    options = argparse.ArgumentParser(description="Write PawPrints log to Influx database")
    options.add_argument('-v', '--verbose', action='store_true', default=False, 
                        help="Print progress on console")
    options.add_argument('-b', '--bucket', type = str, default=None,
                        help='Bucket name. By default, a combination of campaign name and device name is used.')
    options.add_argument('-t', '--token', type = str, default = DEFAULT_TOKEN,
                            help='Influx token')
    options.add_argument('-u', '--url', type = str, default = DEFAULT_URL,
                            help='Influx URL. Default is http://localhost:8086.')
    options.add_argument('-o', '--org', type = str, default = DEFAULT_ORG,
                            help='Influx organization. Default is aerpaw.')
    options.add_argument('-i', '--input', type = str, default = DEFAULT_LOG_PATH,
                            help='PawPrints log path. Default is ./pawprints.jsonl')
    options = options.parse_args()
    run(options)
    print("Bucket name: ")
    print(options.bucket)
