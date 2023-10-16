from datetime import datetime

BS_ID = 0
KPI = "rsrp"

GPS_TIME_OFFSET = 0 # milliseconds
START_TIME = "2023-08-26 12:00:22"
END_TIME = "2023-08-26 13:35:47"

# Convert to Milliseconds since Epoch
START_TIME_MS = datetime.strptime(START_TIME, '%Y-%m-%d %H:%M:%S')
END_TIME_MS = datetime.strptime(START_TIME, '%Y-%m-%d %H:%M:%S')

# Parse GPS Log and get portion between start & end

# Parse KPI Log and get portion between start & end

# Return array slice