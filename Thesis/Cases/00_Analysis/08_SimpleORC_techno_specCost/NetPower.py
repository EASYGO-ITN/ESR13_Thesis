import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

import os.path

print(os.path.abspath("../../"))

with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
    results_a = json.load(file)
with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
    results_b = json.load(file)
with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
    results_c = json.load(file)

results = results_a + results_b + results_c

ts = []
qs = []
fluids = []
for result in results:
    if result:
        ts.append(result["Hot fluid input1"])
        qs.append(result["Hot fluid input2"])

        if result["Working fluid comp"] not in fluids:
            fluids.append(result["Working fluid comp"])

ts = list(set(ts))
ts.sort()
qs = list(set(qs))
qs.sort()

fluids = [["n-Propane", 1],
          ["CycloPropane", 1],
          ["IsoButane", 1],
          ["n-Butane", 1],
          ["Isopentane", 1],
          ["Isohexane", 1],
          ["Cyclopentane", 1],
          ["n-Heptane", 1]]

Wnet = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Wnet_best = [[0 for q in qs] for t in ts]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        power = -result["NetPow_elec"] * 1e-6

        Wnet[f_id][t_id][q_id] = power

        if power > Wnet_best[t_id][q_id]:
            Wnet_best[t_id][q_id] = power

qs = [q * 100 for q in qs]

colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Oranges(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
          plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
          plt.cm.Purples(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts)))]


## plotting the net power for the best fluids
if __name__ == "__main__":
    fig, ax = plt.subplots()
    # ax.set_title("Best Working Fluid")

    ts.reverse()
    Wnet_best.reverse()
    colors_ = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(Wnet_best):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
        ax.plot(qs, t, label=label, color=colors_[i])

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Net electric power/\\unit{\\mega\watt}")
    ax.legend()

    tikzplotlib.save("Plots/SimpleORC_Wnet_Best_WF.tex", figure=fig)

    ts.reverse()
    Wnet_best.reverse()


## plotting the net power for the all fluids and the best fluid
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    for t_id, t in enumerate(ts):
        title = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"
        ax1[t_id].set_title(title)

        for f_id, f_res in enumerate(Wnet):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].plot(qs, Wnet_best[t_id], "k:", linewidth=3, label="Best WF")

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Net electric power/\\unit{\\mega\watt}")

    ax1[-1].legend()

    tikzplotlib.save("Plots/SimpleORC_Wnet_by_T.tex", figure=fig1)


## plotting the net power for IsoPentane
if __name__ == "__main__":
    f_id = fluids.index(["Isopentane", 1])
    fig, ax = plt.subplots()

    for i, t in enumerate(Wnet[f_id]):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[f_id][i])

    ax.set_xlabel("Inlet Steam Quality/%")
    ax.set_ylabel("Net electric power/MW")
    ax.legend()

    tikzplotlib.save("Plots/SimpleORC_Wnet_IsoPentane.tex")

# LEGACY
## plotting the net power for all fluids and the best
if __name__ == "__main_":
    for fluid in fluids:
        fig, ax = plt.subplots()
        ax.set_title("{}".format(fluid[0]))

        f_id = fluids.index(fluid)
        for i, t in enumerate(Wnet[f_id]):
            ax.plot(qs, t, label=ts[i], color=colors[f_id][i])

        ax.set_xlabel("Inlet Steam Quality/%")
        ax.set_ylabel("Net electric power/MW")
        ax.legend()


plt.show()
