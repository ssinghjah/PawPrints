import matplotlib.pyplot as plt
import matplotlib as mpl
import common
import numpy as np

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 30}

V_MIN = -20
V_MAX = -5
DECIMAL_STEPS = 10

rgbs = []

mpl.rcParams.update({'font.size': 25})


for v in range(V_MIN, V_MAX):
    for i in range(DECIMAL_STEPS):        
        color = common.rgb_to_hex(common.value_to_color(v + i / DECIMAL_STEPS, V_MIN, V_MAX))
        rgbs.append(color)

my_map = mpl.colors.ListedColormap(rgbs, name = "my_map")

fig, ax = plt.subplots(figsize=(3, 6))
fig.subplots_adjust(right=0.5)

norm = mpl.colors.Normalize(vmin=V_MIN, vmax=V_MAX)

my_map = "summer"
# my_map = "autumn"

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=my_map,
                                norm=norm,
                                orientation='vertical', location='right')
cb1.set_label('RSRQ (dB)')
cb1.set_ticks(np.arange(V_MIN, V_MAX, DECIMAL_STEPS))

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
