import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

with open("../../02_SimpleORC_superheated/sensitivity_results.json", "r") as file:
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

SpecCost = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
SpecCost_best = [[1e15 for q in qs] for t in ts]

LCOE = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
LCOE_best = [[1e15 for q in qs] for t in ts]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        spec_cost = result["SpecificCost"]
        lcoe = result["LCOE"]

        SpecCost[f_id][t_id][q_id] = spec_cost
        LCOE[f_id][t_id][q_id] = lcoe

        if spec_cost < SpecCost_best[t_id][q_id]:
            SpecCost_best[t_id][q_id] = spec_cost

        if lcoe < LCOE_best[t_id][q_id]:
            LCOE_best[t_id][q_id] = lcoe

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
    SpecCost_best.reverse()

    colors = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(SpecCost_best):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[i])

    # ax.plot([0, 100], [1860, 1860], "k--", label="Astolfi",)

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
    # ax.set_ylim(0, 4000)
    ax.legend()

    tikzplotlib.save("Plots/SimpleORC_SpecCost_Best_WF.tex", figure=fig)

    ts.reverse()
    SpecCost_best.reverse()

## plotting the LCOE for the best fluids
if __name__ == "__main__":
    fig, ax = plt.subplots()
    # ax.set_title("Best Working Fluid")

    ts.reverse()
    LCOE_best.reverse()
    colors = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])
    for i, t in enumerate(LCOE_best):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[i])

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")

    # ax.set_ylim(20, 150)

    ax.legend()

    tikzplotlib.save("Plots/SimpleORC_LCOE_Best_WF.tex", figure=fig)

    ts.reverse()
    LCOE_best.reverse()


## plotting the specific cost for the all fluids and the best fluid
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(SpecCost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].plot(qs, SpecCost_best[t_id], "k:", linewidth=3, label="Best WF")

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
        ax1[t_id].set_ylim(1000, 5000)

    ax1[-1].legend()

    tikzplotlib.save("Plots/SimpleORC_SpecCost_by_T.tex", figure=fig1)

## plotting the LCOE for the all fluids and the best fluid
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(LCOE):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].plot(qs, LCOE_best[t_id], "k:", linewidth=3, label="Best WF")

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")

        ax1[t_id].set_ylim(20, 150)

    ax1[-1].legend()

    tikzplotlib.save("Plots/SimpleORC_LCOE_by_T.tex", figure=fig1)

## plotting the specific Cost for nButane
if __name__ == "__main_":
    fig1, ax1 = plt.subplots()

    f_id = 3
    colors = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])

    ts.reverse()
    SpecCost[f_id].reverse()

    for t_id, t in enumerate(ts):
        label ="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t) + "}{\\K}"

        ax1.plot(qs, SpecCost[f_id][t_id], label=label, color=colors[t_id])

    ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax1.set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")

    ax1.set_ylim(1000, 4500)

    ax1.legend()

    ts.reverse()
    SpecCost[f_id].reverse()

    tikzplotlib.save("Plots/SimpleORC_SpecCost_nButane.tex", figure=fig1)

## plotting the LCOE for nButane
if __name__ == "__main_":
    fig1, ax1 = plt.subplots()

    f_id = 3
    colors = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])

    ts.reverse()
    LCOE[f_id].reverse()

    for t_id, t in enumerate(ts):
        label ="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t) + "}{\\K}"

        ax1.plot(qs, LCOE[f_id][t_id], label=label, color=colors[t_id])

    ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax1.set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")

    ax1.set_ylim(20, 100)

    ax1.legend()

    ts.reverse()
    LCOE[f_id].reverse()

    tikzplotlib.save("Plots/SimpleORC_LCOE_nButane.tex", figure=fig1)

plt.show()
