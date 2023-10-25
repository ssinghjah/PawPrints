import common
import numpy as np

TIME_STEP = 1 # seconds
LOG_FOLDER = "../Data/"
PAWPRINTS_INTERPOLATED_TIMES = "pawprints_interpolated_time_indices.csv"
CONNECTED_PCIs = "connected_bs_pci.csv"
interpolated_indices = common.read_csv(LOG_FOLDER + PAWPRINTS_INTERPOLATED_TIMES)

# Calculate connection duration
connected_pcis = common.read_csv(LOG_FOLDER + CONNECTED_PCIs)
connected_pcis_interpolated = np.array(connected_pcis)[interpolated_indices]

(unique_bss, count_bss) = np.unique(connected_pcis_interpolated, return_counts=True)
num_bss = len(unique_bss)
connected_durations = []
for bs_index in range(num_bss):
    bs_pci = unique_bss[bs_index]
    connected_duration = count_bss[bs_index]* TIME_STEP
    connected_durations.append([bs_pci, connected_duration])

common.write_csv(LOG_FOLDER + "bs_connected_durations.csv", connected_durations)