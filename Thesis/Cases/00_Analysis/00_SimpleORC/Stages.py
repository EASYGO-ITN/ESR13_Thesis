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

Turb_stages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Turb_Vstages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Turb_Hstages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Turb_SP = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        Turb_stages[f_id][t_id][q_id] = result["Turbine_Stages"]
        Turb_Hstages[f_id][t_id][q_id] = result["Turbine_HStages"]
        Turb_Vstages[f_id][t_id][q_id] = result["Turbine_VStages"]
        Turb_SP[f_id][t_id][q_id] = result["Turbine_SP"]

qs = [q * 100 for q in qs]

colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts)))
          ]

## plotting the stages for all fluids
fig, ax = plt.subplots(nrows=len(fluids))
if __name__ == "__main__":
    for f_id, fluid in enumerate(fluids):
        ax[f_id].set_title("{}".format(fluid[0]))

        ax[f_id].plot([0,1], [-1,-1], "k", label="Stages")
        ax[f_id].plot([0,1], [-1,-1], "k--", label="Vr Stages")
        ax[f_id].plot([0,1], [-1,-1], "k:", label="H Stages")

        for i, t in enumerate(Turb_stages[f_id]):
            label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
            ax[f_id].plot(qs, t, label=label, color=colors[0][i])

        for i, t in enumerate(Turb_Vstages[f_id]):
            ax[f_id].plot(qs, t, "--", color=colors[0][i])

        for i, t in enumerate(Turb_Hstages[f_id]):
            ax[f_id].plot(qs, t, ":", color=colors[0][i])

        ax[f_id].set_xlabel("Inlet Steam Quality/%")
        ax[f_id].set_ylabel("Turbine Stages")
        ax[f_id].set_ylim(0, 6)

    ax[-1].legend()


## plotting the enthalpy and volume stages for all fluids
fig, ax = plt.subplots(4)
if __name__ == "__main__":

    t_id = ts.index(548.15)
    for f_id, f_res in enumerate(Turb_Vstages):
        ax[0].plot(qs, f_res[t_id], label=fluids[f_id][0])

    for f_id, f_res in enumerate(Turb_Hstages):
        ax[1].plot(qs, f_res[t_id], label=fluids[f_id][0])

    for f_id, f_res in enumerate(Turb_stages):
        ax[2].plot(qs, f_res[t_id], label=fluids[f_id][0])

    ax[0].set_xlabel("Inlet Steam Quality/%")
    ax[0].set_ylabel("\\(\\log_{V_{r,\\;stage}^{max}} V_{r,\\;isen}^{tot}\\)")
    ax[0].set_ylim(0, 6)

    ax[1].set_xlabel("Inlet Steam Quality/%")
    ax[1].set_ylabel("\\(\\frac{\\Delta h_{isen}^{tot}}{\\Delta h_{stage}^{max}}\\)")
    ax[1].set_ylim(0, 6)

    ax[2].set_xlabel("Inlet Steam Quality/%")
    ax[2].set_ylabel("Turbine Stages")
    ax[2].set_ylim(0, 6)

    ax[2].legend()

    tikzplotlib.save("Plots/TurbineStages_HandV.tex", figure=fig)

## plotting the number of stages and SP for all fluids
fig, ax = plt.subplots(2)
if __name__ == "__main__":

    t_id = ts.index(548.15)
    for f_id, f_res in enumerate(Turb_stages):
        ax[0].plot(qs, f_res[t_id], label=fluids[f_id][0])

    for f_id, f_res in enumerate(Turb_SP):
        ax[1].plot(qs, f_res[t_id], label=fluids[f_id][0])

    ax[0].set_xlabel("Inlet Steam Quality/%")
    ax[0].set_ylabel("Turbine Stages")
    ax[0].set_ylim(0, 6)

    ax[1].set_xlabel("Inlet Steam Quality/%")
    ax[1].set_ylabel("Size Parameter")
    # ax[1].set_ylim(0, 6)

    ax[1].legend()

    tikzplotlib.save("Plots/TurbineStages.tex", figure=fig)


## plotting the stages for CycloPentane
fig, ax = plt.subplots()
if __name__ == "__main__":

    f_id = 6
    fluid = fluids[f_id]

    ax.set_title("{}".format(fluid[0]))

    ax.plot([0,1], [-1,-1], "k", label="Stages")
    ax.plot([0,1], [-1,-1], "k--", label="Vr Stages")
    ax.plot([0,1], [-1,-1], "k:", label="H Stages")

    t_id = -1
    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[t_id]) + "}{\\K}"
    ax.plot(qs, Turb_stages[f_id][t_id], label=label, color=colors[0][t_id])
    ax.plot(qs, Turb_Vstages[f_id][t_id], "--", color=colors[0][t_id])
    ax.plot(qs, Turb_Hstages[f_id][t_id], ":", color=colors[0][t_id])

    ax.set_xlabel("Inlet Steam Quality/%")
    ax.set_ylabel("Turbine Stages")
    ax.set_ylim(0, 6)

plt.show()
