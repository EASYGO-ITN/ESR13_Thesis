import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
import matplotlib

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

Wnet = [[[0.0 for q in qs] for t in ts] for f in fluids]
TurbineCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
CondenserCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
PHECost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
ReprCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
NCGCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
OtherCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
ConsCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
PumpCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
RecupCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
TotCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]
CheckCost = [[[np.NAN for q in qs] for t in ts] for f in fluids]


for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        power = -result["NetPow_elec"]*1e-3
        Wnet[f_id][t_id][q_id] = power
        CheckCost[f_id][t_id][q_id] = result["Cost"]

        TurbineCost[f_id][t_id][q_id] = 0
        CondenserCost[f_id][t_id][q_id] = 0
        PHECost[f_id][t_id][q_id] = 0
        ReprCost[f_id][t_id][q_id] = 0
        OtherCost[f_id][t_id][q_id] = 0
        NCGCost[f_id][t_id][q_id] = 0
        ConsCost[f_id][t_id][q_id] = 0
        PumpCost[f_id][t_id][q_id] = 0
        RecupCost[f_id][t_id][q_id] = 0
        TotCost[f_id][t_id][q_id] = 0

        for equip in result["Costs"]:
            if equip["equip"] == "Turbine":
                TurbineCost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["Condenser", "CoolingPump", "Fan"]:
                CondenserCost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["Superheater", "Evaporator", "Preheater"]:
                PHECost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["BrinePump", "CondensatePump"]:
                ReprCost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["FlashSep", "Mixer"]:
                OtherCost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] == "SecondaryEquip":
                OtherCost[f_id][t_id][q_id] += equip["val"] *1e6 / power
            elif equip["equip"] in ["NCGSep", "NCGComp"]:
                NCGCost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] == "Construction":
                ConsCost[f_id][t_id][q_id] += equip["val"] *1e6 / power
            elif equip["equip"] == "Pump":
                PumpCost[f_id][t_id][q_id] += equip["val"] / power
            elif equip["equip"] == "Recuperator":
                RecupCost[f_id][t_id][q_id] += equip["val"] / power

            if equip["equip"] in ["SecondaryEquip", "Construction"]:
                TotCost[f_id][t_id][q_id] += equip["val"]
            else:
                TotCost[f_id][t_id][q_id] += equip["val"] * 1e-6


qs = [q * 100 for q in qs]

# plot of the turbine cost by temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    # fig1.suptitle("Specific Turbine Cost")
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(TurbineCost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Specific Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax1[t_id].set_ylim(0, 2750)

    ax1[-1].legend()

    # tikzplotlib.save("Plots/SpecTurbCost_by_T.tex", figure=fig1)

# plot of the turbine cost for given temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots()
    # fig1.suptitle("Specific Turbine Cost")
    # for t_id, t in enumerate(ts):
        # ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

    t_id = ts.index(548.15)
    for f_id, f_res in enumerate(TurbineCost):
        ax1.plot(qs, f_res[t_id], label=fluids[f_id][0])

    ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax1.set_ylabel("Specific Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax1.set_ylim(0, 2750)

    ax1.legend()

    tikzplotlib.save("Plots/SpecTurbCost.tex", figure=fig1)

# plot of the condenser cost by temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    fig1.suptitle("Specific Condenser Cost")
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(CondenserCost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Condenser Cost/\\unit{\\mega\\USD\\of{2023}}")
        # ax1[t_id].set_ylim(0, 7.5)

    ax1[-1].legend()

    # tikzplotlib.save("Plots/SpecCost_by_T.tex", figure=fig1)

# plot of the condenser cost for given temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots()
    # fig1.suptitle("Specific Condenser Cost")
    # for t_id, t in enumerate(ts):
    #     ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")
    t_id = ts.index(548.15)
    for f_id, f_res in enumerate(CondenserCost):
        ax1.plot(qs, f_res[t_id], label=fluids[f_id][0])

    ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax1.set_ylabel("Condenser Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax1.set_ylim(0, 1000)

    ax1.legend()

    # tikzplotlib.save("Plots/SpecCondCost.tex", figure=fig1)

# plot of the PHE cost by temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    fig1.suptitle("Specific PHE Cost")
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(PHECost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("PHE Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax1[t_id].set_ylim(0, None)

    ax1[-1].legend()

    # tikzplotlib.save("Plots/SpecCost_by_T.tex", figure=fig1)

# plot of the pump cost by temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    fig1.suptitle("Specific Pump Cost")
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(PumpCost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Pump Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax1[t_id].set_ylim(0, None)

    ax1[-1].legend()

    # tikzplotlib.save("Plots/SpecCost_by_T.tex", figure=fig1)

# plot of the other equipment cost by temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    fig1.suptitle("Specific Secondary Equipment Cost")
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(OtherCost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Other Equipment Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax1[t_id].set_ylim(0, None)

    ax1[-1].legend()

    # tikzplotlib.save("Plots/SpecCost_by_T.tex", figure=fig1)

# plot of the construction cost by temperature
if __name__ == "__main__":
    fig1, ax1 = plt.subplots(len(ts))
    fig1.suptitle("Specific Construction Cost")
    for t_id, t in enumerate(ts):
        ax1[t_id].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}")

        for f_id, f_res in enumerate(ConsCost):
            ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

        ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1[t_id].set_ylabel("Construction Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax1[t_id].set_ylim(0, None)

    ax1[-1].legend()

    # tikzplotlib.save("Plots/SpecCost_by_T.tex", figure=fig1)

plt.show()
