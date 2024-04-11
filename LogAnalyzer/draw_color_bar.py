import matplotlib.pyplot as plt
import matplotlib as mpl
import common
import numpy as np

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 30}

V_MIN = -75
V_MAX = -55
DECIMAL_STEPS = 5
MY_MAP = "Oranges"
LABEL = "RSSI (dBm)"
FONT_SIZE = 34

cmap = MY_MAP
if MY_MAP == "custom":
    rgbs = []
    # mpl.rcParams.update({'font.size': 25})

    for v in range(V_MIN, V_MAX):
        for i in range(DECIMAL_STEPS):        
            color = common.rgb_to_hex(common.value_to_color(v + i / DECIMAL_STEPS, V_MIN, V_MAX))
            rgbs.append(color)

    cmap = mpl.colors.ListedColormap(rgbs, name = "my_map")

fig, ax = plt.subplots(figsize=(2, 6))
fig.subplots_adjust(right=0.5)

norm = mpl.colors.Normalize(vmin=V_MIN, vmax=V_MAX)

# my_map = "YlGn"
# # my_map = "autumn"

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                norm=norm,
                                orientation='vertical', location='right')
cb1.set_label(LABEL, fontsize = FONT_SIZE-2, labelpad=30)
cb1.set_ticks(np.arange(V_MIN, V_MAX, DECIMAL_STEPS))
cb1.ax.tick_params(labelsize=FONT_SIZE) 

ticks = [V_MIN]
TICK_STEP = 5
for v_tick in np.arange(V_MIN + TICK_STEP, V_MAX, TICK_STEP):
    ticks.append(v_tick)
ticks.append(V_MAX)

cb1.set_ticks(ticks)
# plt.rcParams.update({'font.size', 20})
mpl.rc('font', **font)
# cb1.set_ticks([-79, -75, -70, -65, -60, -55, -51])
fig.show()
plt.show()
