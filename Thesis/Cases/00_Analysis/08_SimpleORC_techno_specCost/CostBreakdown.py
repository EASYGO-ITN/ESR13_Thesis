import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
import matplotlib

def get_ORC_results(res_str, conv=1.0, min_val=True, ignore_min_val=True, ignore_conv=False):
    with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
        results_a = json.load(file)

    with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
        results_b = json.load(file)

    with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
        results_c = json.load(file)

    with open("../../08_SimpleORC_techno_specCost/Part_d/sensitivity_results.json", "r") as file:
        results_d = json.load(file)

    results = results_a + results_b + results_c + results_d

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
              ["Cyclopropane", 1],
              ["IsoButane", 1],
              ["n-Butane", 1],
              ["Isopentane", 1],
              ["Isohexane", 1],
              ["Cyclopentane", 1],
              ["n-Heptane", 1]]

    res = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

    if min_val:
        dummy = 1e15
    else:
        dummy = -1e15

    res_best = [[dummy for q in qs] for t in ts]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])
            f_id = fluids.index(result["Working fluid comp"])

            temp_res = result[res_str]
            if not ignore_conv:
                temp_res *= conv

            res[f_id][t_id][q_id] = temp_res

            if not ignore_min_val:
                if min_val:
                    if temp_res < res_best[t_id][q_id]:
                        res_best[t_id][q_id] = temp_res
                else:
                    if temp_res > res_best[t_id][q_id]:
                        res_best[t_id][q_id] = temp_res

    qs = [q * 100 for q in qs]

    return res_best, res, ts, qs, fluids


ORC_Wnet_best, ORC_Costs, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("Costs", ignore_min_val=True, ignore_conv=True)

equips = {"Turbine": "Turbine",
          "FlashSep": "Other Equipment",
          "NCGSep": "Ncg Handling",
          "Condenser": "Condenser",
          "BrinePump": "Repressurisation",
          "CondensatePump": "Repressurisation",
          "NCGComp": "Ncg Handling",
          "Mixer": "Other Equipment",
          "CoolingPump": "Condenser",
          "SecondaryEquip": "Other Equipment",
          "Construction": "Construction",
          "Superheater": "PHE",
          "Evaporator": "PHE",
          "PreHeater": "PHE",
          "Pump": "Pump",
          "Recuperator": "Recuperator",
          "Fan": "Condenser",
          }

unique_equips_ = []
# ordered_equips = ['Turbine', 'Condenser', 'Other Equipment', 'Construction', 'Repressurisation', 'Ncg Handling',  'PHE', 'Pump', 'Recuperator']
ordered_equips = ['Turbine', 'Condenser', 'Repressurisation', 'Other Equipment', 'Ncg Handling',  'PHE', 'Pump', 'Recuperator', 'Construction']
for equip in equips:
    if equips[equip] not in unique_equips_:
        unique_equips_.append(equips[equip])

unique_equips = []
for equip in ordered_equips:
    if equip in unique_equips_:
        unique_equips.append(equip)


if __name__ == "__main__":
    t = 225 + 273.15
    t_id = ORC_ts.index(t)


    aig, ax = plt.subplots(nrows=3, ncols=2)

    for f_id in range(3):

        ax[f_id][0].set_title(ORC_fluids[f_id][0])
        ax[f_id][1].set_title(ORC_fluids[f_id][0])

        fORC_Costs = ORC_Costs[f_id]

        ORC_results = {equip: np.zeros(len(ORC_qs)) for equip in unique_equips}
        totals = np.zeros(len(ORC_qs))

        for i, Costs in enumerate(fORC_Costs[t_id]):

            if type(Costs) is not list:
                continue

            for item in Costs:

                if item["equip"] in ["SecondaryEquip", "Construction"]:

                    if item["equip"] == "SecondaryEquip":
                        equip = equips[item["equip"]]
                        value = item["val"]
                    elif item["equip"] == "Construction":
                        equip = equips[item["equip"]]
                        value = item["val"]
                else:
                    equip = equips[item["equip"]]
                    value = item["val"] * 1e-6

                ORC_results[equip][i] += value
                totals[i] += value

        removals = []
        for item in ORC_results:
            if sum(ORC_results[item]) == 0:
                removals.append(item)

        for remove in removals:
            del ORC_results[remove]

        xlabel = [q for q in ORC_qs]

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = ax[f_id][0].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        ax[f_id][0].set_xlabel("Steam Quality/\\unit{\\percent}")
        ax[f_id][0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
        # ax[f_id][0].set_xlabel("Steam Quality/unit{percent}")
        # ax[f_id][0].set_ylabel("Cost/unit{megaUSDof{2023}}")
        # max_val = ax[f_id][0].get_ylim()[1]
        # ax[f_id][0].annotate(ORC_fluids[f_id][0], (0, max_val*1.05))

        for item in ORC_results:
            ORC_results[item] /= totals * 0.01

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = ax[f_id][1].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        # ax[f_id][1].set_title(ORC_fluids[f_id][0])
        ax[f_id][1].set_xlabel("Steam Quality/\\unit{\\percent}")
        ax[f_id][1].set_ylabel("Cost Contribution/\\unit{\\percent}")
        # ax[f_id][1].set_xlabel("Steam Quality/unit{percent}")
        # ax[f_id][1].set_ylabel("Cost Contribution/unit{percent}")


    big, bx = plt.subplots(nrows=3, ncols=2)

    for f_id in range(3):

        bx[f_id][0].set_title(ORC_fluids[f_id+3][0])
        bx[f_id][1].set_title(ORC_fluids[f_id+3][0])

        fORC_Costs = ORC_Costs[f_id+3]

        ORC_results = {equip: np.zeros(len(ORC_qs)) for equip in unique_equips}
        totals = np.zeros(len(ORC_qs))

        for i, Costs in enumerate(fORC_Costs[t_id]):

            if type(Costs) is not list:
                continue

            for item in Costs:

                if item["equip"] in ["SecondaryEquip", "Construction"]:

                    if item["equip"] == "SecondaryEquip":
                        equip = equips[item["equip"]]
                        value = item["val"]
                    elif item["equip"] == "Construction":
                        equip = equips[item["equip"]]
                        value = item["val"]
                else:
                    equip = equips[item["equip"]]
                    value = item["val"] * 1e-6

                ORC_results[equip][i] += value
                totals[i] += value

        removals = []
        for item in ORC_results:
            if sum(ORC_results[item]) == 0:
                removals.append(item)

        for remove in removals:
            del ORC_results[remove]

        xlabel = [q for q in ORC_qs]

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = bx[f_id][0].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        bx[f_id][0].set_xlabel("Steam Quality/\\unit{\\percent}")
        bx[f_id][0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
        # bx[f_id][0].set_xlabel("Steam Quality/unit{percent}")
        # bx[f_id][0].set_ylabel("Cost/unit{megaUSDof{2023}}")

        for item in ORC_results:
            ORC_results[item] /= totals * 0.01

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = bx[f_id][1].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        bx[f_id][1].set_xlabel("Steam Quality/\\unit{\\percent}")
        bx[f_id][1].set_ylabel("Cost Contribution/\\unit{\\percent}")
        # bx[f_id][1].set_xlabel("Steam Quality/unit{percent}")
        # bx[f_id][1].set_ylabel("Cost Contribution/unit{percent}")



    cig, cx = plt.subplots(nrows=2, ncols=2)

    for f_id in range(2):

        cx[f_id][0].set_title(ORC_fluids[f_id+6][0])
        cx[f_id][1].set_title(ORC_fluids[f_id+6][0])

        fORC_Costs = ORC_Costs[f_id+6]

        ORC_results = {equip: np.zeros(len(ORC_qs)) for equip in unique_equips}
        totals = np.zeros(len(ORC_qs))

        for i, Costs in enumerate(fORC_Costs[t_id]):

            if type(Costs) is not list:
                continue

            for item in Costs:

                if item["equip"] in ["SecondaryEquip", "Construction"]:

                    if item["equip"] == "SecondaryEquip":
                        equip = equips[item["equip"]]
                        value = item["val"]
                    elif item["equip"] == "Construction":
                        equip = equips[item["equip"]]
                        value = item["val"]
                else:
                    equip = equips[item["equip"]]
                    value = item["val"] * 1e-6

                ORC_results[equip][i] += value
                totals[i] += value

        removals = []
        for item in ORC_results:
            if sum(ORC_results[item]) == 0:
                removals.append(item)

        for remove in removals:
            del ORC_results[remove]

        xlabel = [q for q in ORC_qs]

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = cx[f_id][0].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        cx[f_id][0].set_xlabel("Steam Quality/\\unit{\\percent}")
        cx[f_id][0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
        # bx[f_id][0].set_xlabel("Steam Quality/unit{percent}")
        # bx[f_id][0].set_ylabel("Cost/unit{megaUSDof{2023}}")

        for item in ORC_results:
            ORC_results[item] /= totals * 0.01

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = cx[f_id][1].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        cx[f_id][1].set_xlabel("Steam Quality/\\unit{\\percent}")
        cx[f_id][1].set_ylabel("Cost Contribution/\\unit{\\percent}")
        # bx[f_id][1].set_xlabel("Steam Quality/unit{percent}")
        # bx[f_id][1].set_ylabel("Cost Contribution/unit{percent}")

    ax[-1][0].legend()
    bx[-1][0].legend()
    cx[-1][0].legend()

    plt.tight_layout()


    tikzplotlib.save("Plots/SimpleORC_CostBreakdown_Part_A.tex", figure=aig)
    tikzplotlib.save("Plots/SimpleORC_CostBreakdown_Part_B.tex", figure=big)
    tikzplotlib.save("Plots/SimpleORC_CostBreakdown_Part_C.tex", figure=cig)

# LEGACY
if __name__ == "__main_":
    t = 225 + 273.15
    t_id = ORC_ts.index(t)

    aig, ax = plt.subplots(nrows=len(ORC_Costs))
    big, bx = plt.subplots(nrows=len(ORC_Costs))

    for f_id, fORC_Costs in enumerate(ORC_Costs):

        ax[f_id].set_title(ORC_fluids[f_id][0])
        bx[f_id].set_title(ORC_fluids[f_id][0])

        ORC_results = {equip: np.zeros(len(ORC_qs)) for equip in unique_equips}
        totals = np.zeros(len(ORC_qs))

        for i, Costs in enumerate(fORC_Costs[t_id]):

            if type(Costs) is not list:

                continue

            for item in Costs:

                if item["equip"] in ["SecondaryEquip", "Construction"]:

                    if item["equip"] == "SecondaryEquip":
                        equip = equips[item["equip"]]
                        value = item["val"]
                    elif item["equip"] == "Construction":
                        equip = equips[item["equip"]]
                        value = item["val"]
                else:
                    equip = equips[item["equip"]]
                    value = item["val"] * 1e-6

                ORC_results[equip][i] += value
                totals[i] += value

        removals = []
        for item in ORC_results:
            if sum(ORC_results[item]) == 0:
                removals.append(item)

        for remove in removals:
            del ORC_results[remove]

        xlabel = [q for q in ORC_qs]

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = ax[f_id].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        ax[f_id].set_xlabel("Steam Quality/\\unit{\\percent}")
        ax[f_id].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")


        for item in ORC_results:
            ORC_results[item] /= totals * 0.01

        bottom = np.zeros(len(ORC_qs))
        for label, costs in ORC_results.items():
            p = bx[f_id].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        bx[f_id].set_xlabel("Steam Quality/\\unit{\\percent}")
        bx[f_id].set_ylabel("Cost Contribution/\\unit{\\percent}")

    ax[-1].legend()
    bx[-1].legend()

    tikzplotlib.save("Plots/SimpleORC_CostBreakdown_abs.tex", figure=aig)
    tikzplotlib.save("Plots/SimpleORC_CostBreakdown_rel.tex", figure=big)

plt.show()
