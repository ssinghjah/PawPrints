import pandas
import numpy as np
import matplotlib.pyplot as plt
import math
import argparse

REF_GPS_LOG_PATH = "./gps_ref.csv" # Path of the reference GPS
TO_SYNC_GPS_LOG_PATH = "./gps_to_sync.csv" # Path of the GPS log to sync

FLIGHT_THRESHOLD = 20 # meters
NUM_GRAD_DESC_STEPS = 500 
FINE_TIME_STEP = 100 # milliseconds
COARSE_TIME_STEP = 100 # milliseconds

TIME_STEP = COARSE_TIME_STEP # milliseconds

REF_TIME_COL = "time_ms" # Timestamp column of the reference log

TO_SYNC_TIME_COL = "time_ms" # Timestamp column of the log to sync

# Calculate euclidean distance between two LLA points
def lla_distance(lla1, lla2):
    ecef1 = lla_to_ecef(lla1)
    ecef2 = lla_to_ecef(lla2)
    return point_dist_3D(ecef1, ecef2)

# Convert a point from LLA to ECEF format
def lla_to_ecef(lla):
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lla[0])
    lon_rad = math.radians(lla[1])

    # WGS84 parameters
    a = 6378137.0  # semi-major axis
    f_inv = 298.257223563  # inverse flattening
    f = 1.0 / f_inv
    e2 = 1 - (1 - f) * (1 - f)

    # Radius of curvature in the prime vertical
    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)

    # Convert LLA to ECEF
    X = (N + lla[2]) * math.cos(lat_rad) * math.cos(lon_rad)
    Y = (N + lla[2]) * math.cos(lat_rad) * math.sin(lon_rad)
    Z = (N * (1 - e2) + lla[2]) * math.sin(lat_rad)
    return [X, Y, Z]

# Euclidean distance 3D
def point_dist_3D(p1, p2):
    dist = math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2) + pow(p1[2] - p2[2], 2))
    return dist

# Calculate the timestamp and index at which the altitude crosses a pre-set threshold
def _get_takeoff_level_crossing(altitudes):
    num_vals = len(altitudes)
    cumulative_rise = 0
    index = -1
    for index in range(num_vals - 1):
        if altitudes[index+1] > altitudes[index]:
            cumulative_rise += altitudes[index+1]  - altitudes[index]
        elif altitudes[index+1] < altitudes[index]:
            cumulative_rise = 0
        else:
            cumulative_rise = 0
        
        if cumulative_rise > FLIGHT_THRESHOLD:
            return index

# Interpolate the values of a GPS log, based on the given time offset
def _interpolate(to_sync_df_prev, to_sync_df_next, interp_time, kpis_to_sync):
    interpolated_values = {}
    ratio =  (interp_time  - to_sync_df_prev[TO_SYNC_TIME_COL]) / (to_sync_df_next[TO_SYNC_TIME_COL] - to_sync_df_prev[TO_SYNC_TIME_COL]) 
    for kpi in kpis_to_sync:
        interpolated_values[kpi] = to_sync_df_prev[kpi] + ratio*(to_sync_df_next[kpi] - to_sync_df_prev[kpi])
    return interpolated_values

# Interpolate the values of a GPS log, based on the given time offset
def _clamp_min_max(ts, tOffset, to_sync_df, kpis_to_sync, to_sync_values):
    min_index = 0
    max_index = len(ts)
    for index, t in enumerate(ts):
        if t < to_sync_df[TO_SYNC_TIME_COL][0] + tOffset:
            for kpi in kpis_to_sync:
                to_sync_values[kpi][index] = to_sync_df.iloc[0][kpi]
        else:
            min_index = index
            break
    
    ts_len = len(ts)
    for index, t in enumerate(reversed(ts)):
        if t > to_sync_df[TO_SYNC_TIME_COL].to_list()[-1] + tOffset:
            for kpi in kpis_to_sync:
                to_sync_values[kpi][ts_len - index - 1] = to_sync_df.iloc[-1][kpi]
        else:
            max_index = ts_len - index
            break
    
    return (min_index, max_index)

# Interpolate the values of a GPS log, based on the time offset
def calc_values_at_time_offset(tOffset, ts, to_sync_df, kpis_to_sync):
    values = {"time": ts}
    for value in kpis_to_sync:
        values[value] = [None]*len(ts) 
    
    (t_min_index, t_max_index) = _clamp_min_max(ts, tOffset, to_sync_df, kpis_to_sync, values)
    for t_index in range(t_min_index, t_max_index):
        t = ts[t_index]
        to_sync_index_start = 0
        for to_sync_index in range(to_sync_index_start, len(to_sync_df[TO_SYNC_TIME_COL])):
            t_to_sync_offset = to_sync_df[TO_SYNC_TIME_COL][to_sync_index] + tOffset
            if t_to_sync_offset > t:
                next = t_to_sync_offset
                values_at_t = _interpolate(to_sync_df.iloc[to_sync_index - 1], to_sync_df.iloc[to_sync_index], t - tOffset, kpis_to_sync)
                for kpi in kpis_to_sync:
                    values[kpi][t_index] = values_at_t[kpi]
                to_sync_index_start = to_sync_index
                break
    return values

# Calculates error in distance between two gps logs, based on their timestamps
def calculate_error(t_offset, ref_df, to_sync_df, kpis_to_sync, ref_time_col):
    to_sync_values = calc_values_at_time_offset(t_offset, ref_df[ref_time_col].to_list(), to_sync_df, kpis_to_sync)
    rms_errors = {}
    mean_errors = {}
    dist_errs = []
    for index, row in ref_df.iterrows():
        dist_err = lla_distance([ref_df.iloc[index]["latitude"], ref_df.iloc[index]["longitude"], 0], [to_sync_values["latitude"][index], to_sync_values["longitude"][index], 0])
        if math.isnan(dist_err):
            raise Exception("distance error is nan")
        dist_errs.append(dist_err)

    for kpi in kpis_to_sync:
        rms_errors[kpi] = np.sqrt(np.mean(np.square(to_sync_values[kpi] - ref_df[kpi])))
        mean_errors[kpi] = np.mean(to_sync_values[kpi] - ref_df[kpi])
    
    err = np.mean(dist_errs)
    return err, to_sync_values

# Obtain the next time offset at which to calculate the error
def get_next_t(prev_error, curr_error, prev_t, curr_t):
    next_t = 0
    # Keep going in the current direction if the error decreased. Otherwise, change direction
    current_direction = (curr_t - prev_t)/abs(curr_t - prev_t)
    if abs(curr_error) < abs(prev_error):
        next_t = curr_t + current_direction*TIME_STEP
    else:
        next_t = curr_t + -1*current_direction*TIME_STEP
    
    return next_t

# Minimize the distance error between two curves, using gradient descent
def optimize(ref_df, to_sync_df, kpis_to_sync, ref_level_crossing_index, to_sync_level_crossing_index, ref_time_col, to_sync_time_col):
    # Initialize
    errors = []
    tOffsets = []
    best_tOffset = None
    min_error = float('inf')
    tOffset_init = ref_df[ref_time_col][ref_level_crossing_index] - to_sync_df[to_sync_time_col][to_sync_level_crossing_index]
    prev_err, to_sync_values = calculate_error(tOffset_init, ref_df, to_sync_df, kpis_to_sync, ref_time_col)
    prev_tOffset = tOffset_init

    # Ensure that error reduces in the direction of search
    curr_tOffset = tOffset_init + TIME_STEP
    curr_err, to_sync_values = calculate_error(curr_tOffset, ref_df, to_sync_df, kpis_to_sync, ref_time_col)
    next_tOffset = get_next_t(prev_err, curr_err, prev_tOffset, curr_tOffset)
    direction = (next_tOffset - prev_tOffset) / abs(next_tOffset - prev_tOffset)

    # Step through the gradient
    for step_num in range(NUM_GRAD_DESC_STEPS):
        errors.append(prev_err)
        tOffsets.append(prev_tOffset)

        if abs(prev_err) < min_error:
            print("min error")
            best_tOffset = prev_tOffset
            min_error = abs(prev_err)

        print("step number:", step_num, "| error:", prev_err, "| time offset (ms):", prev_tOffset)
        curr_err, to_sync_values = calculate_error(curr_tOffset, ref_df, to_sync_df, kpis_to_sync, ref_time_col)
        next_tOffset = curr_tOffset + direction*curr_tOffset
        
        prev_err = curr_err
        prev_tOffset = curr_tOffset
        curr_tOffset = next_tOffset
    
    return best_tOffset, min_error, errors, tOffsets

# Main function to calculate an initial sync point, based on altitude cross-over threshold, and adjust it in direction of decreasing error. 
# Error is calculated as the distance between the two GPS logs in 2D, considering only latitude and longitude.
def run(ref_gps_path = REF_GPS_LOG_PATH, to_sync_gps_path = TO_SYNC_GPS_LOG_PATH, ref_time_col = REF_TIME_COL, to_sync_time_col = TO_SYNC_TIME_COL):
    ref_df = pandas.read_csv(ref_gps_path)
    to_sync_df = pandas.read_csv(to_sync_gps_path)

    # Calculate the time instance at which the altitude threshold is crossed, as initial sync estimate, to be refined later.
    ref_level_crossing_index = _get_takeoff_level_crossing(ref_df["altitude"].to_list())
    to_sync_level_crossing_index = _get_takeoff_level_crossing(to_sync_df["altitude"].to_list())
    
    # Plot the initial synchronization points 
    fig, axs = plt.subplots(2)
    fig.suptitle('Altitudes (m)')

    axs[0].scatter(to_sync_df[to_sync_time_col], to_sync_df["altitude"])
    axs[1].scatter(ref_df[ref_time_col], ref_df["altitude"])

    axs[0].scatter(to_sync_df[to_sync_time_col][to_sync_level_crossing_index], to_sync_df["altitude"][to_sync_level_crossing_index], marker="o")
    axs[1].scatter(ref_df[ref_time_col][ref_level_crossing_index], ref_df["altitude"][ref_level_crossing_index], marker="o")

    axs[0].grid()
    axs[1].grid()
    plt.show()

    best_tOffset, min_error, errors, tOffsets = optimize(ref_df, to_sync_df, ["latitude", "longitude", "altitude"], ref_level_crossing_index, to_sync_level_crossing_index, ref_time_col, to_sync_time_col)
    print("Best time offset = " + str(best_tOffset) + " ms")
    print("Minmum error = " + str(min_error))

    # Plot the error minimization results
    plt.scatter(tOffsets, errors)
    plt.xlabel("Time offset (ms)")
    plt.ylabel("Mean error in distance between datapoints, after interpolation")
    plt.grid()
    plt.show()
    return best_tOffset

# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Synchronize two GPS logs. Returns and prints the time offset, which is to be added to the log_to_sync, to synchronize it to the reference. Does not modify the logs.')
    parser.add_argument('-r', '--ref', type = str, default = REF_GPS_LOG_PATH, help='Path to the reference GPS log')
    parser.add_argument('-s', '--to-sync', type = str, default = TO_SYNC_GPS_LOG_PATH, help='Path to the GPS log which will be synced to the reference')
    parser.add_argument('--to-sync-time-col', type = str, default = REF_TIME_COL, help='Name of the time column of the reference log')
    parser.add_argument('--ref-time-col', type = str, default = TO_SYNC_TIME_COL, help='Name of the time column of the log to sync to reference')
    options = parser.parse_args()
    run(options.ref, options.to_sync, options.ref_time_col, options.to_sync_time_col)
   



