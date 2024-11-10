import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
import matplotlib

def get_thermo(res_str, conv=1.0, min_val=True, ignore_min_val=True, ignore_conv=False):
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

def get_techno(res_str, conv=1.0, min_val=True, ignore_min_val=True, ignore_conv=False):
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


def format_results(messy_result, ts, qs, Ttarget):

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
    ordered_equips = ['Turbine', 'Condenser', 'Repressurisation', 'Other Equipment', 'Ncg Handling', 'PHE', 'Pump',
                      'Recuperator', 'Construction']
    for equip in equips:
        if equips[equip] not in unique_equips_:
            unique_equips_.append(equips[equip])

    unique_equips = []
    for equip in ordered_equips:
        if equip in unique_equips_:
            unique_equips.append(equip)

    results = {equip: np.zeros(len(qs)) for equip in unique_equips}
    totals = np.zeros(len(qs))

    t_id = ts.index(Ttarget)

    for i, result in enumerate(messy_result[t_id]):

        if type(result) is np.NAN:
            continue

        for item in result:

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

            results[equip][i] += value
            totals[i] += value

    removals = []
    for item in results:
        if sum(results[item]) == 0:
            removals.append(item)

    for remove in removals:
        del results[remove]

    return results, totals

Ftarget = [["n-Propane", 1],
           ["Isopentane", 1],
           # ["n-Butane", 1],
           ["n-Heptane", 1]]

Ttarget = 225 + 273.15

Costs_best_thermo, Costs_thermo, ts_thermo, qs_thermo, fluid_thermo = get_thermo("Costs", ignore_min_val=True, ignore_conv=True)
Costs_best_techno, Costs_techno, ts_techno, qs_techno, fluid_techno = get_techno("Costs", ignore_min_val=True, ignore_conv=True)

if __name__ == "__main__":

    fig, ax = plt.subplots(nrows=3, ncols=2)

    Cmax = [25, 40, 100]

    for j, f in enumerate(Ftarget):

        ax[j][0].set_title(f[0] + ": Techno-Economic Opt.")
        ax[j][1].set_title(f[0] + ": Thermodynamic Opt.")

        f_id_thermo = fluid_thermo.index(f)
        f_id_techno = fluid_techno.index(f)

        techno_res, techno_totals = format_results(Costs_techno[f_id_techno], ts_techno, qs_techno, Ttarget)
        thermo_res, thermo_totals = format_results(Costs_thermo[f_id_thermo], ts_thermo, qs_thermo, Ttarget)

        xlabel = [q for q in qs_techno]
        bottom = np.zeros(len(qs_techno))
        for label, costs in techno_res.items():
            p = ax[j][0].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        ax[j][0].set_xlabel("Steam Quality/\\unit{\\percent}")
        ax[j][0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax[j][0].set_ylim(0, Cmax[j])

        xlabel = [q for q in qs_thermo]
        bottom = np.zeros(len(qs_thermo))
        for label, costs in thermo_res.items():
            p = ax[j][1].bar(xlabel, costs, 5, label=label, bottom=bottom)
            bottom += costs

        ax[j][1].set_xlabel("Steam Quality/\\unit{\\percent}")
        ax[j][1].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax[j][1].set_ylim(0, Cmax[j])

    ax[0][0].legend()

    plt.tight_layout()

    tikzplotlib.save("Plots/CostBreakdown.tex")

plt.show()
