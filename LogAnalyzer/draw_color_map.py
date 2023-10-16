import matplotlib.pyplot as plt
import matplotlib as mpl
import common

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

V_MIN = -79
V_MAX = -51
DECIMAL_STEPS = 10

rgbs = []

for v in range(V_MIN, V_MAX):
    for i in range(DECIMAL_STEPS):
        color = common.rgb_to_hex(common.value_to_color(v + i / DECIMAL_STEPS, V_MIN, V_MAX))
        rgbs.append(color)

my_map = mpl.colors.ListedColormap(rgbs, name = "my_map")

fig, ax = plt.subplots(figsize=(6, 1))
fig.subplots_adjust(bottom=0.5)

norm = mpl.colors.Normalize(vmin=V_MIN, vmax=V_MAX)
mpl.rc('font', **font)

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=my_map,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('RSSI (dBm)')
cb1.set_ticks([-79, -75, -70, -65, -60, -55, -51])
fig.show()
plt.show()