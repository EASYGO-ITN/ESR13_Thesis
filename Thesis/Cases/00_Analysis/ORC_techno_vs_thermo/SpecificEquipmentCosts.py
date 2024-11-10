import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
import matplotlib

with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
    thermo_results = json.load(file)

with open("../../00_SimpleORC_additional_fluids/sensitivity_results.json", "r") as file:
    thermo_results += json.load(file)


with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
    techno_results = json.load(file)

with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
    techno_results += json.load(file)

with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
    techno_results += json.load(file)

with open("../../08_SimpleORC_techno_specCost/Part_d/sensitivity_results.json", "r") as file:
    techno_results += json.load(file)

def get_results(results):

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

    Wnet_best = [[-1e15 for q in qs] for t in ts]
    SpecCost_best = [[1e15 for q in qs] for t in ts]
    TurbineCost = [[np.NAN for q in qs] for t in ts]
    CondenserCost = [[np.NAN for q in qs] for t in ts]
    ReprCost = [[np.NAN for q in qs] for t in ts]
    OtherCost = [[np.NAN for q in qs] for t in ts]
    ConsCost = [[np.NAN for q in qs] for t in ts]
    PHECost = [[np.NAN for q in qs] for t in ts]
    TotCost = [[np.NAN for q in qs] for t in ts]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])

            specCost = result["SpecificCost"]

            if specCost < SpecCost_best[t_id][q_id]:
                power = -result["NetPow_elec"] * 1e-3
                Wnet_best[t_id][q_id] = power
                TotCost[t_id][q_id] = result["Cost"]

                TurbineCost[t_id][q_id] = 0
                CondenserCost[t_id][q_id] = 0
                ReprCost[t_id][q_id] = 0
                OtherCost[t_id][q_id] = 0
                ConsCost[t_id][q_id] = 0
                PHECost[t_id][q_id] = 0

                for equip in result["Costs"]:
                    if equip["equip"] == "Turbine":
                        TurbineCost[t_id][q_id] += equip["val"] / power
                    elif equip["equip"] in ["Condenser", "CoolingPump", "Fan"]:
                        CondenserCost[t_id][q_id] += equip["val"] / power
                    elif equip["equip"] in ["PHE"]:
                        PHECost[t_id][q_id] += equip["val"] / power
                    elif equip["equip"] in ["BrinePump", "CondensatePump", "Pump"]:
                        ReprCost[t_id][q_id] += equip["val"] / power
                    elif equip["equip"] in ["FlashSep", "Mixer"]:
                        OtherCost[t_id][q_id] += equip["val"] / power
                    elif equip["equip"] == "SecondaryEquip":
                        OtherCost[t_id][q_id] += equip["val"] *1e6 / power
                    elif equip["equip"] == "Construction":
                        ConsCost[t_id][q_id] += equip["val"] *1e6 / power

    qs = [q * 100 for q in qs]

    return TurbineCost, CondenserCost, ts, qs,


thermo_turbine, thermo_condenser, thermo_ts, thermo_qs = get_results(thermo_results)
techno_turbine, techno_condenser, techno_ts, techno_qs = get_results(techno_results)

colors = [plt.cm.Oranges([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Blues([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Greys([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          ]

# plot of the turbine cost by temperature
if __name__ == "__main_":
    plot_change=False

    fig1, ax1 = plt.subplots()
    twin = ax1.twinx()
    ax1.plot([0, 1], [-1, -1], label="Techno-economic Opt.", color=colors[2][2])
    ax1.plot([0, 1], [-1, -1], "--", label="Thermodynamic Opt.", color=colors[2][2])

    ax1.plot([0, 1], [-1, -1], label="Turbine", color=colors[0][2])
    ax1.plot([0, 1], [-1, -1], label="Condenser", color=colors[1][2])

    for t_id, t in enumerate(thermo_ts):
        label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"
        ax1.plot([0, 1], [-1, -1], label=label, color=colors[2][t_id])

    for f_id, f_res in enumerate(thermo_turbine):
        ax1.plot(thermo_qs, f_res, "--", color=colors[0][f_id])

    for f_id, f_res in enumerate(techno_turbine):
        ax1.plot(techno_qs, f_res, color=colors[0][f_id])

    for f_id, f_res in enumerate(thermo_condenser):
        ax1.plot(thermo_qs, f_res, "--", color=colors[1][f_id])

    for f_id, f_res in enumerate(techno_condenser):
        ax1.plot(techno_qs, f_res, color=colors[1][f_id])

        ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1.set_ylabel("Cost Contribution/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
        # ax1.set_ylim(0, None)

    if plot_change:
        twin = ax1.twinx()

        for f_id, f_res in enumerate(techno_turbine):
            techno = np.array(f_res)
            thermo = np.array((thermo_turbine[f_id]))
            twin.plot(techno_qs, (thermo-techno)/thermo, ":", color=colors[0][f_id])

        for f_id, f_res in enumerate(techno_condenser):
            techno = np.array(f_res)
            thermo = np.array((thermo_condenser[f_id]))
            twin.plot(thermo_qs, (thermo-techno)/thermo, ":", color=colors[1][f_id])

    ax1.legend()

    # tikzplotlib.save("Plots/CostReduction_by_T.tex", figure=fig1)

# plot of the turbine cost by temperature
if __name__ == "__main__":
    plot_change=False

    fig1, ax1 = plt.subplots()
    twin = ax1.twinx()
    ax1.plot([0, 1], [-1, -1], label="Techno-economic Opt.", color=colors[2][2])
    ax1.plot([0, 1], [-1, -1], "--", label="Thermodynamic Opt.", color=colors[2][2])

    ax1.plot([0, 1], [-1, -1], label="Turbine", color=colors[0][2])
    ax1.plot([0, 1], [-1, -1], label="Condenser", color=colors[1][2])

    for t_id, t in enumerate(thermo_ts):
        label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"
        ax1.plot([0, 1], [-1, -1], label=label, color=colors[2][t_id])
    #
    for f_id, f_res in enumerate(thermo_turbine):
        # ax1.plot(thermo_qs, thermo_turbine[f_id], "--", color=colors[0][f_id])
        # ax1.plot(techno_qs, techno_turbine[f_id], color=colors[0][f_id])
        twin.plot(techno_qs, 100 * (np.array(techno_turbine[f_id]) - np.array(
            thermo_turbine[f_id][0:9] + [thermo_turbine[f_id][10]])) / np.array(
            thermo_turbine[f_id][0:9] + [thermo_turbine[f_id][10]]), ":", color=colors[0][f_id])

    # for f_id, f_res in enumerate(thermo_condenser):
    #     for f_id, f_res in enumerate(thermo_condenser):
    #         ax1.plot(thermo_qs, thermo_condenser[f_id], "--", color=colors[1][f_id])
    #         ax1.plot(techno_qs, techno_condenser[f_id], color=colors[1][f_id])
    #         twin.plot(techno_qs, 100 * (np.array(techno_condenser[f_id]) - np.array(
    #             thermo_condenser[f_id][0:9] + [thermo_condenser[f_id][10]])) / np.array(
    #             thermo_condenser[f_id][0:9] + [thermo_condenser[f_id][10]]), ":", color=colors[1][f_id])

        ax1.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
        ax1.set_ylabel("Cost Contribution/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
        # ax1.set_ylim(0, None)

    if plot_change:
        twin = ax1.twinx()

        for f_id, f_res in enumerate(techno_turbine):
            techno = np.array(f_res)
            thermo = np.array((thermo_turbine[f_id]))
            twin.plot(techno_qs, (thermo-techno)/thermo, ":", color=colors[0][f_id])

        for f_id, f_res in enumerate(techno_condenser):
            techno = np.array(f_res)
            thermo = np.array((thermo_condenser[f_id]))
            twin.plot(thermo_qs, (thermo-techno)/thermo, ":", color=colors[1][f_id])

    ax1.legend()

    # tikzplotlib.save("Plots/CostReduction_by_T.tex", figure=fig1)

plt.show()
