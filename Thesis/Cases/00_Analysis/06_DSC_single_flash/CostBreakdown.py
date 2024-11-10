import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_DSC_results(res_str, conv=1.0, ignore_conv=False):
    with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ts = []
    qs = []
    for result in results:
        if result:
            ts.append(result["Hot fluid input1"])
            qs.append(result["Hot fluid input2"])

    ts = list(set(ts))
    ts.sort()
    qs = list(set(qs))
    qs.sort()

    res = [[np.NAN + 0 for q in qs] for t in ts]

    for result in results:
        if result:
            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])

            temp_res = result[res_str]
            if not ignore_conv:
                temp_res *= conv

            res[t_id][q_id] = temp_res

    qs = [q * 100 for q in qs]

    return res, ts, qs


def get_ORC_results(res_str, conv=1.0, min_val=True, ignore_min_val=True, ignore_conv=False):
    with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
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
    fluids.sort()

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

    return res_best, res, ts, qs


DSC_Costs, DSC_ts, DSC_qs = get_DSC_results("Costs", ignore_conv=True)
ORC_Wnet_best, ORC_Costs, ORC_ts, ORC_qs = get_ORC_results("Costs", ignore_min_val=True, ignore_conv=True)

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
ordered_equips = ['Turbine', 'Condenser', 'Other Equipment', 'Repressurisation', 'Ncg Handling',  'PHE', 'Pump', 'Recuperator', 'Construction',]
for equip in equips:
    if equips[equip] not in unique_equips_:
        unique_equips_.append(equips[equip])

unique_equips = []
for equip in ordered_equips:
    if equip in unique_equips_:
        unique_equips.append(equip)

DSC_results = {equip: np.zeros(len(DSC_qs)) for equip in unique_equips}
totals = np.zeros(len(DSC_qs))

t = 225 + 273.15
t_id = DSC_ts.index(t)

for i, Costs in enumerate(DSC_Costs[t_id]):

    if type(Costs) is np.NAN:
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

        DSC_results[equip][i] += value
        totals[i] += value

removals = []
for item in DSC_results:
    if sum(DSC_results[item]) == 0:
        removals.append(item)

for remove in removals:
    del DSC_results[remove]

if __name__ == "__main__":
    fig, ax = plt.subplots(ncols=2)

    xlabel = [q for q in DSC_qs]
    bottom = np.zeros(len(DSC_qs))
    for label, costs in DSC_results.items():
        p = ax[0].bar(xlabel, costs, 5, label=label, bottom=bottom)
        bottom += costs

    ax[0].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].legend()


    xlabel = [q for q in DSC_qs]
    bottom = np.zeros(len(DSC_qs))

    for item in DSC_results:
        DSC_results[item] /= totals * 0.01

    for label, costs in DSC_results.items():
        p = ax[1].bar(xlabel, costs, 5, label=label, bottom=bottom)
        bottom += costs

    ax[1].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Cost Contribution/\\unit{\\percent}")
    # ax[1].legend()

    tikzplotlib.save("Plots/DSC_SingleFlash_CostBreakdown.tex")

# LEGACY
if __name__ == "__main_":
    fig, ax = plt.subplots()

    xlabel = [q for q in DSC_qs]
    bottom = np.zeros(len(DSC_qs))
    for label, costs in DSC_results.items():
        p = ax.bar(xlabel, costs, 5, label=label, bottom=bottom)
        bottom += costs

    ax.set_xlabel("Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax.legend()

    tikzplotlib.save("Plots/DSC_SingleFlash_CostBreakdown_abs.tex")

    fig, ax = plt.subplots()

    xlabel = [q for q in DSC_qs]
    bottom = np.zeros(len(DSC_qs))

    for item in DSC_results:
        DSC_results[item] /= totals * 0.01

    for label, costs in DSC_results.items():
        p = ax.bar(xlabel, costs, 5, label=label, bottom=bottom)
        bottom += costs

    ax.set_xlabel("Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Cost Contribution/\\unit{\\percent}")
    ax.legend()

    tikzplotlib.save("Plots/DSC_SingleFlash_CostBreakdown_rel.tex")

plt.show()
