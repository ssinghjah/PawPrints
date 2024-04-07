#!/bin/bash
IPERF_LOG_PATH="/data/local/tmp/iperf_results" 
adb shell "tail -f $IPERF_LOG_PATH"

