import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI

with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
    results = json.load(file)

ts = []
qs = []
for result in results:
    if result:
        ts.append(result["Hot fluid input1"])
        qs.append(result["Hot fluid input2"])

ts = list(set(ts))
ts.sort()
qs = list(set(qs))
qs.sort()

Pin = [[np.NAN + 0 for q in qs] for t in ts]
Pflash = [[np.NAN + 0 for q in qs] for t in ts]
Pmin = [[np.NAN + 0 for q in qs] for t in ts]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])

        Pin[t_id][q_id] = result["Pin"]*1e-5
        Pflash[t_id][q_id] = result["Pflash"]*1e-5
        Pmin[t_id][q_id] = result["Pmin"]*1e-5

qs = [q * 100 for q in qs]

colors = [plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
          plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts))),
          ]

fig, axs = plt.subplots()

axs.plot([0,1], [1e-4, 1e-4], label="Inlet", color=colors[0][2])
axs.plot([0,1], [1e-4, 1e-4], label="Post-Flash", color=colors[1][2])
axs.plot([0,1], [1e-4, 1e-4], label="Condenser", color=colors[2][2])

for i, p in enumerate(Pin):
    label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
    axs.plot([0,1], [1e-4, 1e-4], label=label, color=colors[3][i])

for i, p in enumerate(Pin):
    label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
    axs.plot(qs, p, color=colors[0][i])

for i, p in enumerate(Pflash):
    label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
    axs.plot(qs, p, color=colors[1][i])

for i, p in enumerate(Pmin):
    label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
    axs.plot(qs, p, color=colors[2][i])

axs.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
axs.set_ylabel("Geofluid Pressure/\\unit{\\bar}")
axs.set_yscale("log")
axs.set_ylim([6e-2, 1e2])
axs.legend()

tikzplotlib.save("Plots/SingleFlash_OPs.tex")

plt.show()
