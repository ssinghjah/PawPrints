import matplotlib.pyplot as plt
import matplotlib as mpl
import common
import numpy as np

# Settings

FONT_SIZE = 18
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : FONT_SIZE}

LABEL_PAD = 15
TICK_ROTATION = 90
V_MIN = 200 # KPI MIN
V_MAX = 750  # KPI MAX
DECIMAL_STEPS = 0.5 # Used to interpolate color between V_MIN and V_MAX
TICK_STEP = 50 # KPI Steps
MY_MAP = "jet"
LABEL = "PDCP throughput (Mbps)" # Color bar label
cmap = MY_MAP

# Execution
if MY_MAP == "custom":
    rgbs = []
    for v in range(V_MIN, V_MAX):
        for i in range(DECIMAL_STEPS):        
            color = common.rgb_to_hex(common.value_to_color(v + i / DECIMAL_STEPS, V_MIN, V_MAX))
            rgbs.append(color)

    cmap = mpl.colors.ListedColormap(rgbs, name = "my_map")

fig, ax = plt.subplots(figsize=(2, 6))
fig.subplots_adjust(right=0.5)

norm = mpl.colors.Normalize(vmin=V_MIN, vmax=V_MAX)

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
                                norm=norm,
                                orientation='vertical', location='right')
cb1.set_label(LABEL, fontsize = FONT_SIZE, labelpad=15)
cb1.ax.tick_params(labelsize=FONT_SIZE, rotation=TICK_ROTATION) 

ticks = [V_MIN]
for v_tick in np.arange(V_MIN + TICK_STEP, V_MAX, TICK_STEP):
    ticks.append(v_tick)
ticks.append(V_MAX)

cb1.set_ticks(ticks)
mpl.rc('font', **font)
fig.show()
plt.show()
