import numpy as np
import pandas as pd
import common
import matplotlib.pyplot as plt
import math
import numpy
import tqdm


# All angles are in degrees 
LOG_PATH = "C:/Users/ssingh28/AeroConf_Aerial_Radio_Propagation_Modeling/Data/5G_all.csv"
AZIMUTH_PATTERN = "C:/Users/ssingh28/AeroConf_Aerial_Radio_Propagation_Modeling/Data/5G_azimuth_sorted.json"
ELEVATION_PATTERN = "C:/Users/ssingh28/AeroConf_Aerial_Radio_Propagation_Modeling/Data/5G_elevation_sorted.json"
BS_ANT_BEARING = 330 # Fix to 342? Degrees wrt North, clockwise direction is considered positive
BS_ANT_ELEVATION = 0 # Degrees, positive is above horizon
BS_FREQUENCY = 3.4e9 # Hz
PT_Watts_Total = 5 # Watts
PT_dBm_Total = 36.99 # dBm
N_VERT_ANTENNA_ELEM = 32 # Number of vertical antenna elements
PT_SS_RSRP_Fraction = 1/(273*12)# Power is divided equally among 273 PRBs and 12 subcarriers per PRB
PT_SS_RSRP = PT_Watts_Total * PT_SS_RSRP_Fraction # Watts
PT_SS_RSRP_dBm = 10 * math.log10(PT_SS_RSRP * 1000) # dBm


def calculate_elevation_path_loss(elevation_angle_deg):    
    elevation_path_loss_dB = 10*math.log10(abs(math.sin(N_VERT_ANTENNA_ELEM * elevation_angle_deg * math.pi / (180.0*2.0)) /  (N_VERT_ANTENNA_ELEM * math.sin(math.pi * elevation_angle_deg / (180.0*2.0)))))
    return elevation_path_loss_dB

def calculate_free_space_path_loss(AZIMUTH_PATTERN, ELEVATION_PATTERN, LOG_PATH, BS_ANT_BEARING, BS_ANT_ELEVATION, bWrite=True):
    # Read antenna patterns from JSON files
    # These files should contain sorted azimuth and elevation patterns in dB
    azimuth_pattern = common.read_json(AZIMUTH_PATTERN) 
    elevation_pattern = common.read_json(ELEVATION_PATTERN) 

    # Convert json keys to float for easier matching. By detault, json keys are strings in python. So, conversion to float is required.
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
             
            elevation_deg = float(row["bs_elevation"]) - BS_ANT_ELEVATION
            
            # Find the closest azimuth and elevation patterns
            closest_azimuth_dB = common.interpolate_in_list(azimuth_pattern, azimuth_deg)
            if abs(elevation_deg) < 10:
                elevation_path_loss = common.interpolate_in_list(elevation_pattern, elevation_deg)
            else:
                elevation_path_loss = calculate_elevation_path_loss(elevation_deg)
                

            # closest_azimuth_dB = azimuth_pattern[closest_azimuth]
            # closest_elevation_dB = elevation_pattern[closest_elevation]

            # Total gain = sum of azimuth and elevation gains, in log-scale
            total_gain_dB = closest_azimuth_dB + elevation_path_loss

            # Free space path loss in dB
            free_space_path_loss_dB = 20*math.log10(4 * math.pi * row["bs_distance"] * BS_FREQUENCY / 3e8)  

            # Calculate theoretical SS RSRP by considering the transmitter antenna gain and the free space path loss
            theoretical_rsrp = PT_SS_RSRP_dBm + total_gain_dB - free_space_path_loss_dB
            df.at[index, "free_space_ss_rsrp"] = theoretical_rsrp
            df.at[index, "5G_antenna_elevation_gain"] = elevation_path_loss
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
    bs_elevation_range = np.arange(-10, 10, 1)
    correlations = []
    errors = []
    bs_bearing = 330
    for bs_elevation in tqdm.tqdm(bs_elevation_range):
        df = calculate_free_space_path_loss(AZIMUTH_PATTERN, ELEVATION_PATTERN, LOG_PATH, bs_bearing, bs_elevation, bWrite=False)
        df = df.dropna(subset=["ss_rsrp"])
        correlation = df["free_space_ss_rsrp"].corr(df["ss_rsrp"])
        mean_error = abs(np.mean((df["ss_rsrp"] - df["free_space_ss_rsrp"])))
        correlations.append((bs_elevation, correlation))
        errors.append((bs_elevation, mean_error))
    
    plt.rcParams.update({'font.size': 28})
    best_elevation, best_err = min(errors, key=lambda x: x[1])
    fig, ax1 = plt.subplots()
    ax1.scatter(bs_elevation_range, [e[1] for e in errors])
    ax1.set_xlabel("BS antenna elevation (degrees)")
    ax1.set_ylabel("Mean absolute error of free space SS RSRP, PawPrints")
    ax1.grid(True)
    ax1.set_xticks(bs_elevation_range)

    # ax2 = ax1.twinx()
    # ax2.plot(bs_elevation_range, [r[1] for r in rms_errors], color='orange')
    # ax2.set_ylabel("RMS error of free space SS RSRP with measured SS RSRP")
    plt.show()
    print(f"Best BS Elevation: {best_elevation} degrees with error: {best_err}")
    return best_elevation, best_err

if __name__ == "__main__":
    # best_elevation, best_corr = tune()
    # best_bearing = BS_ANT_BEARING
    free_space_df = calculate_free_space_path_loss(AZIMUTH_PATTERN, ELEVATION_PATTERN, LOG_PATH, BS_ANT_BEARING, BS_ANT_ELEVATION, bWrite=True)