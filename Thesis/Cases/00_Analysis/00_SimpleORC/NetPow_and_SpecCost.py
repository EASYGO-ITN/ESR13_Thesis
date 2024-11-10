import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

def get_ORC_results():
    with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
        results = json.load(file)

    with open("../../00_SimpleORC_additional_fluids/sensitivity_results.json", "r") as file:
        results += json.load(file)

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
    SpecCost = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Wnet_best = [[-1e15 + 0 for q in qs] for t in ts]
    Wnet_best_best = [[np.NAN for q in qs] for t in ts]
    SpecCost_best = [[np.NAN  for q in qs] for t in ts]
    SpecCost_best_best = [[1e15 for q in qs] for t in ts]

    geophires_a = [[np.NAN for q in qs] for t in ts]
    geophires_b = [[np.NAN for q in qs] for t in ts]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])
            f_id = fluids.index(result["Working fluid comp"])

            power = -result["NetPow_elec"] * 1e-6
            spec_cost = result["SpecificCost"]

            Wnet[f_id][t_id][q_id] = power
            SpecCost[f_id][t_id][q_id] = spec_cost

            if power > Wnet_best[t_id][q_id]:
                    Wnet_best[t_id][q_id] = power
                    SpecCost_best[t_id][q_id] = spec_cost
                    geophires_a[t_id][q_id] = ORC_subcrit(ts[t_id], power)*1000/power

            if spec_cost < SpecCost_best_best[t_id][q_id]:
                    SpecCost_best_best[t_id][q_id] = spec_cost
                    Wnet_best_best[t_id][q_id] = power
                    geophires_b[t_id][q_id] = ORC_subcrit(ts[t_id], power)*1000/power

    qs = [q * 100 for q in qs]

    return Wnet_best, Wnet_best_best, SpecCost_best, SpecCost_best_best, Wnet, SpecCost, ts, qs, fluids, geophires_a, geophires_b

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


ORC_Wnet_best, ORC_Wnet_best_best, ORC_SpecCost_best, ORC_SpecCost_best_best, ORC_Wnet, ORC_SpecCost, ORC_ts, ORC_qs, ORC_fluids, geophires_best, geophires_best_best = get_ORC_results()

colors = [plt.cm.Oranges([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Blues([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Greys([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          ]

# power
if __name__ == "__main__":
    fig, ax = plt.subplots(2)

    for i, t in enumerate(ORC_ts):
        ax[0].plot([0, 1], [-1, -1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_best):
        ax[0].plot(ORC_qs, t, color=colors[0][i])

    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax[0].legend()

    # plotting the specific cost
    ax[1].plot([0, 1], [-1, -1], label="Binary ORC", color=colors[0][3])
    ax[1].plot([0, 1], [-1, -1], label="Geophires-X", color=colors[1][3])

    for i, t in enumerate(ORC_SpecCost_best):
        ax[1].plot(ORC_qs, t, color=colors[0][i])

    for i, t in enumerate(geophires_best):
        ax[1].plot(ORC_qs, t, color=colors[1][i])

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax[1].legend()

    tikzplotlib.save("Plots/Wnet_best_SpecCost.tex")

# net power of lowest spec cost
if __name__ == "__main__":
    fig, ax = plt.subplots(2)

    for i, t in enumerate(ORC_ts):
        ax[0].plot([0, 1], [-1, -1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_best_best):
        ax[0].plot(ORC_qs, t, color=colors[0][i])

    ax[1].plot([0, 1], [-1, -1], label="Binary ORC", color=colors[0][3])
    ax[1].plot([0, 1], [-1, -1], label="Geophires-X", color=colors[1][3])

    for i, t in enumerate(ORC_SpecCost_best_best):
        ax[1].plot(ORC_qs, t, color=colors[0][i])

    for i, t in enumerate(geophires_best_best):
        ax[1].plot(ORC_qs, t, color=colors[1][i])

    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax[0].legend()

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax[1].legend()

    tikzplotlib.save("Plots/Wnet_of_min_SpecCost.tex")

plt.show()
