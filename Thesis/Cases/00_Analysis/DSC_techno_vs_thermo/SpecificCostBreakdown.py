import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
import matplotlib

with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
    thermo_results = json.load(file)

with open("../../10_DSC_single_flash_techno_specCost/sensitivity_results.json", "r") as file:
    techno_results = json.load(file)

ts = []
qs = []
for result in thermo_results:
    if result:
        ts.append(result["Hot fluid input1"])
        qs.append(result["Hot fluid input2"])

ts = list(set(ts))
ts.sort()
qs = list(set(qs))
qs.sort()

thermo_Wnet = [[0.0 for q in qs] for t in ts]
thermo_TurbineCost = [[np.NAN for q in qs] for t in ts]
thermo_CondenserCost = [[np.NAN for q in qs] for t in ts]
thermo_ReprCost = [[np.NAN for q in qs] for t in ts]
thermo_OtherCost = [[np.NAN for q in qs] for t in ts]
thermo_ConsCost = [[np.NAN for q in qs] for t in ts]
thermo_TotCost = [[np.NAN for q in qs] for t in ts]


for result in thermo_results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])

        power = -result["NetPow_elec"]*1e-3
        thermo_Wnet[t_id][q_id] = power
        thermo_TotCost[t_id][q_id] = result["Cost"]

        thermo_TurbineCost[t_id][q_id] = 0
        thermo_CondenserCost[t_id][q_id] = 0
        thermo_ReprCost[t_id][q_id] = 0
        thermo_OtherCost[t_id][q_id] = 0
        thermo_ConsCost[t_id][q_id] = 0

        for equip in result["Costs"]:
            if equip["equip"] == "Turbine":
                thermo_TurbineCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["Condenser", "CoolingPump", "Fan"]:
                thermo_CondenserCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["BrinePump", "CondensatePump"]:
                thermo_ReprCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["FlashSep", "Mixer"]:
                thermo_OtherCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] == "SecondaryEquip":
                thermo_OtherCost[t_id][q_id] += equip["val"] *1e6 / power
            elif equip["equip"] == "Construction":
                thermo_ConsCost[t_id][q_id] += equip["val"] *1e6 / power


techno_Wnet = [[0.0 for q in qs] for t in ts]
techno_TurbineCost = [[np.NAN for q in qs] for t in ts]
techno_CondenserCost = [[np.NAN for q in qs] for t in ts]
techno_ReprCost = [[np.NAN for q in qs] for t in ts]
techno_OtherCost = [[np.NAN for q in qs] for t in ts]
techno_ConsCost = [[np.NAN for q in qs] for t in ts]
techno_TotCost = [[np.NAN for q in qs] for t in ts]


for result in techno_results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])

        power = -result["NetPow_elec"]*1e-3
        techno_Wnet[t_id][q_id] = power
        techno_TotCost[t_id][q_id] = result["SpecificCost"]

        techno_TurbineCost[t_id][q_id] = 0
        techno_CondenserCost[t_id][q_id] = 0
        techno_ReprCost[t_id][q_id] = 0
        techno_OtherCost[t_id][q_id] = 0
        techno_ConsCost[t_id][q_id] = 0

        for equip in result["Costs"]:
            if equip["equip"] == "Turbine":
                techno_TurbineCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["Condenser", "CoolingPump", "Fan"]:
                techno_CondenserCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["BrinePump", "CondensatePump"]:
                techno_ReprCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] in ["FlashSep", "Mixer"]:
                techno_OtherCost[t_id][q_id] += equip["val"] / power
            elif equip["equip"] == "SecondaryEquip":
                techno_OtherCost[t_id][q_id] += equip["val"] *1e6 / power
            elif equip["equip"] == "Construction":
                techno_ConsCost[t_id][q_id] += equip["val"] *1e6 / power

qs = [q * 100 for q in qs]

colors = [plt.cm.Oranges([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Blues([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Greys([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          ]

# plot of the turbine cost by temperature
if __name__ == "__main__":
    plot_change=True

    fig1, ax1 = plt.subplots()
    # fig1.suptitle("Specific Turbine Cost")

    ax1.plot([0, 1], [-1, -1], label="Techno-economic Opt.", color=colors[2][2])
    ax1.plot([0, 1], [-1, -1], "--", label="Thermodynamic Opt.", color=colors[2][2])

    ax1.plot([0, 1], [-1, -1], label="Turbine", color=colors[0][2])
    ax1.plot([0, 1], [-1, -1], label="Condenser", color=colors[1][2])

    for t_id, t in enumerate(ts):
        label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"
        ax1.plot([0, 1], [-1, -1], label=label, color=colors[2][t_id])

    for f_id, f_res in enumerate(thermo_TurbineCost):
        ax1.plot(qs, f_res, "--", color=colors[0][f_id])

    for f_id, f_res in enumerate(techno_TurbineCost):
        ax1.plot(qs, f_res, color=colors[0][f_id])

    for f_id, f_res in enumerate(thermo_CondenserCost):
        ax1.plot(qs, f_res, "--", color=colors[1][f_id])

    for f_id, f_res in enumerate(techno_CondenserCost):
        ax1.plot(qs, f_res, color=colors[1][f_id])

        ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1.set_ylabel("Cost Contribution/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
        ax1.set_ylim(0, None)

    if plot_change:
        twin = ax1.twinx()

        for f_id, f_res in enumerate(techno_TurbineCost):
            techno = np.array(f_res)
            thermo = np.array((thermo_TurbineCost[f_id]))
            twin.plot(qs, (thermo-techno)/thermo, ":", color=colors[0][f_id])

        for f_id, f_res in enumerate(techno_CondenserCost):
            techno = np.array(f_res)
            thermo = np.array((thermo_CondenserCost[f_id]))
            twin.plot(qs, (thermo-techno)/thermo, ":", color=colors[1][f_id])

    ax1.legend()

    # tikzplotlib.save("Plots/CostReduction_by_T.tex", figure=fig1)

plt.show()
