import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

ccplantadjfactor = 1

def ORC_subcrit(T, Pow):
    MaxProducedTemperature = T - 273.15
    ElectricityProduced = Pow

    if MaxProducedTemperature < 150.:
        C3 = -1.458333E-3
        C2 = 7.6875E-1
        C1 = -1.347917E2
        C0 = 1.0075E4
        CCAPP1 = C3 * MaxProducedTemperature ** 3 + C2 * MaxProducedTemperature ** 2 + C1 * MaxProducedTemperature + C0
    else:
        CCAPP1 = 2231 - 2 * (MaxProducedTemperature - 150.)
    x = ElectricityProduced * 1
    y = ElectricityProduced * 1
    if y == 0.0:
        y = 15.0
    z = pow(y / 15., -0.06)

    Cplantcorrelation = CCAPP1 * z * x * 1000. / 1E6

    # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs. factor 1.10 to convert from 2016 to 2022 factor 1.03 to convert from 2022 to 2023
    Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.10 * 1.03

    return Cplant


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
# fluids.sort()
fluids = [["n-Propane", 1],
          ["CycloPropane", 1],
          ["IsoButane", 1],
          ["n-Butane", 1],
          ["Isopentane", 1],
          ["Isohexane", 1],
          ["Cyclopentane", 1],
          ["n-Heptane", 1]]

SpecCost = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
SpecCost_best = [[1e15 for q in qs] for t in ts]

LCOE = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
LCOE_best = [[1e15 for q in qs] for t in ts]

Wnet = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Wnet_best = [[-1e15 for q in qs] for t in ts]
SpecCost_geophires = [[np.NAN for q in qs] for t in ts]


for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        spec_cost = result["SpecificCost"]
        lcoe = result["LCOE"]
        power = -result["NetPow_elec"] * 1e-6

        SpecCost[f_id][t_id][q_id] = spec_cost
        LCOE[f_id][t_id][q_id] = lcoe

        if spec_cost < SpecCost_best[t_id][q_id]:
            SpecCost_best[t_id][q_id] = spec_cost

        if lcoe < LCOE_best[t_id][q_id]:
            LCOE_best[t_id][q_id] = lcoe

        if power > Wnet_best[t_id][q_id]:
            Wnet_best[t_id][q_id] = power
            SpecCost_geophires[t_id][q_id] = ORC_subcrit(ts[t_id], power)*1000/power


qs = [q * 100 for q in qs]

colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Oranges(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
          plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
          plt.cm.Purples(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts)))]

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
        ax1[t_id].set_ylim(0, 6000)

    ax1[-1].legend()

    tikzplotlib.save("Plots/SpecCost_by_WF_T.tex", figure=fig1)

## plotting the specific Cost for nButane
if __name__ == "__main__":
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

    tikzplotlib.save("Plots/SpecCost_nButane.tex", figure=fig1)

plt.show()
