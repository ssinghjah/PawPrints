import numpy as np
import pandas as pd
import common
import matplotlib.pyplot as plt
import math
import numpy
import tqdm


# All angles are in degrees
LOG_PATH = "/home/simran/Work/AERPAW/AeroConf/Data/5G_all_nemo.csv"
AZIMUTH_PATTERN = "/home/simran/Work/AERPAW/AeroConf/Data/5G_azimuth_sorted.json"
ELEVATION_PATTERN = "/home/simran/Work/AERPAW/AeroConf/Data/5G_elevation_sorted.json"
BS_ANT_BEARING = 330 # Fix to 342? Degrees wrt North, clockwise direction is considered positive
BS_FREQUENCY = 3.4e9 # Hz
PT_Watts_Total = 5 # Watts
PT_dBm_Total = 36.99 # dBm
PT_SS_RSRP_Fraction = 1/(273*12)# Power is divided equally among 273 PRBs and 12 subcarriers per PRB
PT_SS_RSRP = PT_Watts_Total * PT_SS_RSRP_Fraction # Watts
PT_SS_RSRP_dBm = 10 * math.log10(PT_SS_RSRP * 1000) # dBm

def calculate_free_space_path_loss(AZIMUTH_PATTERN, ELEVATION_PATTERN, LOG_PATH, BS_ANT_BEARING, bWrite=True):
    # Read antenna patterns from JSON files
    # These files should contain sorted azimuth and elevation patterns in dB
    azimuth_pattern = common.read_json(AZIMUTH_PATTERN) 
    elevation_pattern = common.read_json(ELEVATION_PATTERN)

    azimuth_pattern = {float(k): v for k, v in azimuth_pattern.items()}
    elevation_pattern = {float(k): v for k, v in elevation_pattern.items()}

    # Read the radio log data
    # This log should contain columns for latitude, longitude, altitude, bs_bearing, and bs_elevation
    # The bearing and elevation should be in degrees
    df = pd.read_csv(LOG_PATH)

    for index, row in df.iterrows():
        if not common.isNan(row["bs_bearing"]) and not common.isNan(row["bs_elevation"]):
            bs_to_uav_bearing = row["bs_bearing"]

            # Adjust for antenna orientation
            azimuth_deg = float(bs_to_uav_bearing) -  BS_ANT_BEARING

            # Check for negative bearing, adjust range to 0 to 360 
            if azimuth_deg < 0:
                azimuth_deg += 360 # degrees
            
            elevation_deg = float(row["bs_elevation"])
            
            # Find the closest azimuth and elevation patterns
            closest_azimuth = common.get_closest_number_in_list(list(azimuth_pattern.keys()), azimuth_deg)
            closest_elevation = common.get_closest_number_in_list(list(elevation_pattern.keys()), elevation_deg)
            closest_azimuth_dB = azimuth_pattern[closest_azimuth]
            closest_elevation_dB = elevation_pattern[closest_elevation]

            # Total gain = sum of azimuth and elevation gains, in log-scale
            total_gain_dB = closest_azimuth_dB + closest_elevation_dB

            # Free space path loss in dB
            free_space_path_loss_dB = 20*math.log10(4 * math.pi * row["bs_distance"] * BS_FREQUENCY / 3e8)  

            # Calculate theoretical SS RSRP by considering the transmitter antenna gain and the free space path loss
            theoretical_rsrp = PT_SS_RSRP_dBm + total_gain_dB - free_space_path_loss_dB
            df.at[index, "free_space_ss_rsrp"] = theoretical_rsrp
            df.at[index, "5G_antenna_elevation_gain"] = closest_elevation_dB
            df.at[index, "5G_antenna_azimuth_gain"] = closest_azimuth_dB

            # Future extension
            '''
            for pattern in ant_rad_patterns:
                pass
                # Calculate attenuation
                # theoretical_attn = common.calculate_attenuation(pattern["hor_pattern"], pattern["vert_pattern"], azimuth_deg, elevation_deg)
                # df.at[index, "thoeretical_attn_pci_" + pattern["pci"]] = theoretical_attn
            '''
        else:
            df.at[index, "free_space_ss_rsrp"] = None

    if bWrite:
        df.to_csv(LOG_PATH, index=False)

    return df

def tune():
    bs_bearing_range = np.arange(300, 360, 1)
    correlations = []
    rms_errors = []
    for bs_bearing in tqdm.tqdm(bs_bearing_range):
        df = calculate_free_space_path_loss(AZIMUTH_PATTERN, ELEVATION_PATTERN, LOG_PATH, bs_bearing, bWrite=False)
        correlation = df["free_space_ss_rsrp"].corr(df["ss_rsrp"])
        rms_error = numpy.sqrt(numpy.mean((df["free_space_ss_rsrp"] - df["ss_rsrp"]) ** 2))
        correlations.append((bs_bearing, correlation))
        rms_errors.append((bs_bearing, rms_error))
    
    best_bearing, best_corr = max(correlations, key=lambda x: x[1])
    fig, ax1 = plt.subplots()
    ax1.plot(bs_bearing_range, [c[1] for c in correlations])
    ax1.set_xlabel("BS antenna bearing (degrees)")
    ax1.set_ylabel("Correlation of free space SS RSRP with measured SS RSRP")

    ax2 = ax1.twinx()
    ax2.plot(bs_bearing_range, [r[1] for r in rms_errors], color='orange')
    ax2.set_ylabel("RMS error of free space SS RSRP with measured SS RSRP")
    plt.show()
    print(f"Best BS Bearing: {best_bearing} degrees with correlation: {best_corr}")
    return best_bearing, best_corr

if __name__ == "__main__":
    # best_bearing, best_corr = tune()
    best_bearing = BS_ANT_BEARING
    free_space_df = calculate_free_space_path_loss(AZIMUTH_PATTERN, ELEVATION_PATTERN, LOG_PATH, best_bearing)