import sys
import pandas
import numpy as np
import matplotlib.pyplot as plt
import math
import os

sys.path.append("../")
import common

REF_GPS_LOG_PATH = "../../ExperimentData/July_2_2024_Flight_3/Companion/gps.csv"
FIXED_REF_GPS_LOG_PATH = "../../ExperimentData/July_2_2024_Flight_3/Companion/gps_processed.csv"
TO_SYNC_GPS_LOG_PATH = "../../ExperimentData/July_2_2024_Flight_3/Nemo/gps_processed.csv"
WORKAREA = "./WorkSpace"

FLIGHT_THRESHOLD = 20 # meters
NUM_GRAD_DESC_STEPS = 50 
GRADIENT_BREAK_POINT = 45 # degrees
FINE_TIME_STEP = 25 # milliseconds
COARSE_TIME_STEP = 100 # milliseconds
TIME_STEP = COARSE_TIME_STEP # milliseconds

def _get_takeoff_level_crossing(altitudes):
    num_vals = len(altitudes)
    state = "zero"
    cumulative_rise = 0
    index = -1
    rise_start_index = -1
    for index in range(num_vals - 1):
        if altitudes[index+1] > altitudes[index]:
            state = "rising"
            cumulative_rise += altitudes[index+1]  - altitudes[index]
            if rise_start_index == -1:
                rise_start_index = index
        elif altitudes[index+1] < altitudes[index]:
            state = "falling"
            cumulative_rise = 0
            rise_start_index = -1
        else:
            state = "zero"
            cumulative_rise = 0
            rise_start_index = -1
        
        if cumulative_rise > FLIGHT_THRESHOLD:
            return index, rise_start_index

# Assumes that the time at which the gps log ends is when the drone lands
def _correct_altitude_drift(pos_df, rise_start_index, t_end, time_col):
    t_start = pos_df.iloc[rise_start_index][time_col]
    alt_start = pos_df.iloc[rise_start_index]["altitude"]
    pos_df["altitude"] = pos_df["altitude"] - alt_start
    alt_end = pos_df.iloc[-1]["altitude"]
    # t_end = pos_df.iloc[-1][time_col]
    correction_per_second = - (alt_end)/ (t_end - t_start)     
    end_index = len(pos_df)
    row_num = rise_start_index + 1
    t_end_reached = False
    while not t_end_reached:
    # for row_num in range(rise_start_index+1, end_index):
        pos_df.at[row_num, "altitude"] += (pos_df.iloc[row_num][time_col] - t_start)*correction_per_second
        row_num += 1
        t_end_reached = pos_df.iloc[row_num][time_col] >= t_end
    return correction_per_second


def _get_forward_deltas(values):
    deltas = []
    num_values = len(values)
    for index in range(num_values - 1):
        delta = (values[index + 1] - values[index])
        deltas.append(delta)
    return deltas

REF_TIME_COL = "time_ms"
TO_SYNC_TIME_COL = "time_ms"

def _interpolate(to_sync_df_prev, to_sync_df_next, interp_time, kpis_to_sync):
    interpolated_values = {}
    ratio =  (interp_time  - to_sync_df_prev[TO_SYNC_TIME_COL]) / (to_sync_df_next[TO_SYNC_TIME_COL] - to_sync_df_prev[TO_SYNC_TIME_COL]) 
    for kpi in kpis_to_sync:
        interpolated_values[kpi] = to_sync_df_prev[kpi] + ratio*(to_sync_df_next[kpi] - to_sync_df_prev[kpi])
    return interpolated_values

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

def calculate_error(t_offset, ref_df, to_sync_df, kpis_to_sync):
    to_sync_values = calc_values_at_time_offset(t_offset, ref_df[REF_TIME_COL].to_list(), to_sync_df, kpis_to_sync)
    rms_errors = {}
    mean_errors = {}
    dist_errs = []
    for index, row in ref_df.iterrows():
        dist_err = common.lla_distance([ref_df.iloc[index]["latitude"], ref_df.iloc[index]["longitude"], 0], [to_sync_values["latitude"][index], to_sync_values["longitude"][index], 0])
        if math.isnan(dist_err):
            raise Exception("distance error is nan")
        dist_errs.append(dist_err)

    for kpi in kpis_to_sync:
        rms_errors[kpi] = np.sqrt(np.mean(np.square(to_sync_values[kpi] - ref_df[kpi])))
        mean_errors[kpi] = np.mean(to_sync_values[kpi] - ref_df[kpi])
    
    err = np.mean(dist_errs)
    return err, to_sync_values

def get_next_t(prev_error, curr_error, prev_t, curr_t, current_direction):
    next_t = 0
    gradient = round(math.atan(abs((curr_error - prev_error)*1000.0/(curr_t - prev_t)))*180/math.pi, 3)
    print("Gradient = " + str(gradient) + " deg")
    if gradient < GRADIENT_BREAK_POINT:
        TIME_STEP = FINE_TIME_STEP
    else:
        TIME_STEP = COARSE_TIME_STEP

    next_t = curr_t + current_direction*TIME_STEP

    return next_t

def optimize(ref_df, to_sync_df, kpis_to_sync, ref_level_crossing_index, to_sync_level_crossing_index):
    # Initialize
    errors = []
    tOffsets = []
    best_tOffset = None
    min_error = float('inf')
    # _correct_altitude_drift(ref_df, REF_TIME_COL)
    tOffset_init = ref_df[REF_TIME_COL][ref_level_crossing_index] - to_sync_df[TO_SYNC_TIME_COL][to_sync_level_crossing_index]
    prev_err, to_sync_values = calculate_error(tOffset_init, ref_df, to_sync_df, kpis_to_sync)
    prev_tOffset = tOffset_init
    curr_tOffset = tOffset_init + TIME_STEP
    curr_error, to_sync_values = calculate_error(curr_tOffset, ref_df, to_sync_df, kpis_to_sync)
    direction = (curr_tOffset - prev_tOffset)/abs(curr_tOffset - prev_tOffset)
    if abs(curr_error) > abs(prev_err):
        direction = -direction

    # Step through the gradient
    for step_num in range(NUM_GRAD_DESC_STEPS):
        errors.append(prev_err)
        tOffsets.append(prev_tOffset)

        if abs(prev_err) < min_error:
            best_tOffset = prev_tOffset
            min_error = abs(prev_err)

        print("step number:", step_num, "| error:", prev_err, " m| time offset:", prev_tOffset, "ms")
        curr_err, to_sync_values = calculate_error(curr_tOffset, ref_df, to_sync_df, kpis_to_sync)
        next_tOffset = get_next_t(prev_err, curr_err, prev_tOffset, curr_tOffset, direction)
        
        prev_err = curr_err
        prev_tOffset = curr_tOffset
        curr_tOffset = next_tOffset
    
    return best_tOffset, min_error, errors, tOffsets


def run(ref_gps_path = REF_GPS_LOG_PATH, to_sync_gps_path = TO_SYNC_GPS_LOG_PATH, ref_time_col = REF_TIME_COL, to_sync_time_col = TO_SYNC_TIME_COL):
    ref_df = pandas.read_csv(ref_gps_path)
    to_sync_df = pandas.read_csv(to_sync_gps_path)

    ref_level_crossing_index, ref_rise_start_index = _get_takeoff_level_crossing(ref_df["altitude"].to_list())
    ref_df.to_csv(os.path.join(WORKAREA, "ref_pos.csv"), index=False, header=False)
    to_sync_df.to_csv(os.path.join(WORKAREA, "to_sync_pos.csv"), index=False, header=False)

    # _correct_altitude_drift(ref_df, ref_rise_start_index, ref_df.iloc[-1][REF_TIME_COL], REF_TIME_COL)
    # ref_df[[REF_TIME_COL, "latitude", "longitude", "altitude"]].to_csv(os.path.join(WORKAREA,"ref_pos_fixed.csv"), index=False, header=False)

    to_sync_level_crossing_index, to_sync_rise_start_index = _get_takeoff_level_crossing(to_sync_df["altitude"].to_list())
   
    fig, axs = plt.subplots(2)
    fig.suptitle('Altitudes (m)')

    axs[0].scatter(to_sync_df[to_sync_time_col], to_sync_df["altitude"])
    axs[1].scatter(ref_df[ref_time_col], ref_df["altitude"])

    axs[0].scatter(to_sync_df[to_sync_time_col][to_sync_level_crossing_index], to_sync_df["altitude"][to_sync_level_crossing_index], marker="o")
    axs[1].scatter(ref_df[ref_time_col][ref_level_crossing_index], ref_df["altitude"][ref_level_crossing_index], marker="o")

    axs[0].grid()
    axs[1].grid()
    plt.show()

    best_tOffset, min_error, errors, tOffsets = optimize(ref_df, to_sync_df, ["latitude", "longitude", "altitude"], ref_level_crossing_index, to_sync_level_crossing_index)
    print("Best time offset = " + str(best_tOffset) + " ms")
    print("Minmum error = " + str(min_error))

    to_sync_df["ref_time"] = to_sync_df[TO_SYNC_TIME_COL] + best_tOffset
    to_sync_df["altitude"] = to_sync_df["altitude"] + (ref_df["altitude"][ref_rise_start_index] - to_sync_df["altitude"][to_sync_rise_start_index])
    # # _correct_altitude_drift(to_sync_df, to_sync_rise_start_index, ref_df.iloc[-1][REF_TIME_COL], "ref_time")
    # to_sync_df[["ref_time", "latitude", "longitude", "altitude"]].to_csv(os.path.join(WORKAREA, "to_sync_pos_fixed.csv"), index=False, header=False)

    plt.scatter(tOffsets, errors)
    plt.xlabel("Time offset (ms)")
    plt.ylabel("Mean error in distance between datapoints, after interpolation")
    plt.grid()
    plt.show()
    print("Takeoff timestamp (from ref gps log) = " + str(ref_df[REF_TIME_COL][ref_rise_start_index]) + " ms")

    fig, ax1 = plt.subplots()
    ax1.scatter(to_sync_df[to_sync_time_col] + best_tOffset, to_sync_df["altitude"])
    ax1.scatter(ref_df[ref_time_col], ref_df["altitude"])
    ax1.grid()
    ax1.set_xlabel("Time since Unix Epoch (ms)")
    ax1.set_ylabel("Altitude (m)")
    plt.show()


    # return offset and take-off time from reference gps log
    return best_tOffset, ref_df[REF_TIME_COL][ref_rise_start_index]


if __name__ == "__main__":
    run()
   



