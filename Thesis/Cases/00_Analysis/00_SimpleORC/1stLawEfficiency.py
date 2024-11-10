import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

import os.path

print(os.path.abspath("../../"))

with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
    results_a = json.load(file)
with open("../../00_SimpleORC_additional_fluids/sensitivity_results.json", "r") as file:
    results_b = json.load(file)

results = results_a + results_b

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
eta_plant_best = [[0 for q in qs] for t in ts]
eta_cycle_best = [[0 for q in qs] for t in ts]
eta_recov_best = [[0 for q in qs] for t in ts]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        # tmax = result["Tmax"]
        # tmin = result["Tmin"]

        # power = (1 - tmin/tmax)*100
        plant = result["eta_I_plant"] * 100
        cycle = result["eta_I_cycle"] * 100
        recov = result["eta_I_recov"] * 100

        Wnet[f_id][t_id][q_id] = plant

        if plant > eta_plant_best[t_id][q_id]:
            eta_plant_best[t_id][q_id] = plant
            eta_cycle_best[t_id][q_id] = cycle
            eta_recov_best[t_id][q_id] = recov


qs = [q * 100 for q in qs]

colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Oranges(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
          plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
          plt.cm.Purples(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts)))]


## plotting the net power for the best fluids
if __name__ == "__main__":
    fig, ax = plt.subplots(3)
    # ax.set_title("Best Working Fluid")

    ts.reverse()
    eta_plant_best.reverse()
    eta_cycle_best.reverse()
    eta_recov_best.reverse()

    colors_ = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(eta_cycle_best):
        # label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
        ax[0].plot(qs, t, color=colors_[i])
    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("\\(\\eta_{cycle}\\)/\\unit{\\percent}")
    ax[0].set_ylim(0, 35)

    colors_ = plt.cm.Greens([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(eta_recov_best):
        # label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
        ax[1].plot(qs, t, color=colors_[i])
    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("\\(\\eta_{cycle}\\)/\\unit{\\percent}")
    ax[1].set_ylim(50, 100)

    colors_ = plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(eta_plant_best):
        # label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
        ax[2].plot(qs, t, color=colors_[i])
    colors_ = plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(eta_plant_best):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
        ax[2].plot([0, 0], [0, 0], label=label, color=colors_[i])


    ax[2].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[2].set_ylabel("\\(\\eta_{cycle}\\)/\\unit{\\percent}")
    ax[2].set_ylim(0, 35)

    # ax[0].set_xlabel("Inlet Steam Quality/%")
    # ax[0].set_ylabel("1st Law Plant Efficiency/%")
    # ax[0].set_ylim(0, 25)
    ax[2].legend(loc="lower right")

    tikzplotlib.save("Plots/Eta1stLaw_plant_best_WF.tex", figure=fig)

## plotting the net power for the all fluids and the best fluid
if __name__ == "__main_":
    fig1, ax1 = plt.subplots(len(ts))
    for t_id, t in enumerate(ts):
        title = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"
        ax1[t_id].set_title(title)

        for f_id, f_res in enumerate(Wnet):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].plot(qs, Wnet_best[t_id], "k:", linewidth=3, label="Best WF")

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Net electric power/\\unit{\\mega\watt}")
        ax1[t_id].set_ylim(0, 25)

    ax1[-1].legend()

    tikzplotlib.save("Plots/Eta1stLaw_by_T.tex", figure=fig1)


## plotting the net power for IsoPentane
if __name__ == "__main_":
    f_id = fluids.index(["Isopentane", 1])
    fig, ax = plt.subplots()

    for i, t in enumerate(Wnet[f_id]):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[f_id][i])

    ax.set_xlabel("Inlet Steam Quality/%")
    ax.set_ylabel("Net electric power/MW")
    ax.legend()

    tikzplotlib.save("Plots/Eta1stLaw_IsoPentane.tex")


plt.show()
