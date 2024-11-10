import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
    results = json.load(file)

ts = []
qs = []
fluids = []
for result in results:
    if result:
        ts.append(result["Hot fluid input1"])
        qs.append(result["Hot fluid input2"])

ts = list(set(ts))
ts.sort()
qs = list(set(qs))
qs.sort()

Wnet = [[np.NAN + 0 for q in qs] for t in ts]

for result in results:
    if result:
        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])

        Wnet[t_id][q_id] = -result["NetPow_elec"] * 1e-6

qs = [q * 100 for q in qs]


fig, ax = plt.subplots()
ts.reverse()
Wnet.reverse()
colors = plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25])

for i, t in enumerate(Wnet):
    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
    # ax.plot(qs, t, label="\\qty{"+str(ts[i])+"}{\\K}", color=colors[i])
    ax.plot(qs, t, label=label, color=colors[i])


ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
ax.set_ylabel("Net electric power/\\unit{\\mega\\watt}")
ax.legend()

tikzplotlib.save("Plots/DSC_SingleFlash.tex")

plt.show()
