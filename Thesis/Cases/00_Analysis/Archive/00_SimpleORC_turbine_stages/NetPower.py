import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

with open("../../00_SimpleORC_turbine_stages/sensitivity_results.json", "r") as file:
    results = json.load(file)

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
# fluids.sort()

Turb_Stages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Turb_HStages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Turb_VStages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Turb_SP = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        power = -result["NetPow_elec"] * 1e-6

        Turb_Stages[f_id][t_id][q_id] = result["Turbine_Stages"]
        Turb_HStages[f_id][t_id][q_id] = result["Turbine_HStages"]
        Turb_VStages[f_id][t_id][q_id] = result["Turbine_VStages"]
        Turb_SP[f_id][t_id][q_id] = result["Turbine_SP"]


qs = [q * 100 for q in qs]

Nt = len(ts)
if Nt < 2:
    Nt = 3
colors = [plt.cm.Blues(np.linspace(0.3, 1, Nt)),
          plt.cm.Oranges(np.linspace(0.3, 1, Nt)),
          plt.cm.Greens(np.linspace(0.3, 1, Nt)),
          plt.cm.Reds(np.linspace(0.3, 1, Nt)),
          plt.cm.Purples(np.linspace(0.3, 1, Nt)),
          plt.cm.Greys(np.linspace(0.3, 1, Nt))]

# plot stages
if __name__ == "__main__":

    fig, ax = plt.subplots()

    ax.plot([0,100], [-1, -1], "k--", label="Enthalpy Stages")
    ax.plot([0,100], [-1, -1], "k:", label="Volume Stages")

    for f_id, fluid in enumerate(fluids):
        ax.set_title("{}".format(fluid[0]))

        for i, t in enumerate(Turb_HStages[f_id]):
            ax.plot(qs, t, "--", color=colors[f_id][1])

        for i, t in enumerate(Turb_VStages[f_id]):
            ax.plot(qs, t, ":", color=colors[f_id][1])

        for i, t in enumerate(Turb_Stages[f_id]):
            ax.plot(qs, t, label=fluid[0], color=colors[f_id][1])

    ax.set_xlabel("Inlet Steam Quality/%")
    ax.set_ylabel("Net electric power/MW")
    ax.set_ylim(0, None)
    ax.legend()


plt.show()
