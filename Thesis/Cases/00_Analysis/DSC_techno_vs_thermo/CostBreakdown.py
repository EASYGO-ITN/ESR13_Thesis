import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_DSC_results(res_str, conv=1.0, ignore_conv=False):
    with open("../../10_DSC_single_flash_techno_specCost/sensitivity_results.json", "r") as file:
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

def get_DSC_results_b(res_str, conv=1.0, ignore_conv=False):
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
    ordered_equips = ['Turbine', 'Condenser', 'Other Equipment', 'Repressurisation', 'Ncg Handling', 'PHE', 'Pump',
                      'Recuperator', 'Construction', ]
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

DSC_Costs, DSC_ts, DSC_qs = get_DSC_results("Costs", ignore_conv=True)
DSC_results, DSC_totals = format_results(DSC_Costs, DSC_ts, DSC_qs, 225+273.15)

DSC_Costs_b, DSC_ts_b, DSC_qs_b = get_DSC_results_b("Costs", ignore_conv=True)
DSC_results_b, DSC_totals_b = format_results(DSC_Costs_b, DSC_ts_b, DSC_qs_b, 225+273.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(ncols=2)

    xlabel = [q for q in DSC_qs]
    bottom = np.zeros(len(DSC_qs))
    for label, costs in DSC_results.items():
        p = ax[0].bar(xlabel, costs, 5, label=label, bottom=bottom)
        bottom += costs

    ax[0].set_title("Techno-Economic Opt.")
    ax[0].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].set_ylim(0,35)
    ax[0].legend()

    xlabel = [q for q in DSC_qs_b]
    bottom = np.zeros(len(DSC_qs_b))

    # for item in DSC_results_b:
    #     DSC_results_b[item] /= DSC_totals_b * 0.01

    for label, costs in DSC_results_b.items():
        p = ax[1].bar(xlabel, costs, 5, label=label, bottom=bottom)
        bottom += costs

    ax[1].set_title("Thermodynamic Opt.")
    ax[1].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[1].set_ylim(0,35)

    tikzplotlib.save("Plots/DSC_SingleFlash_CostBreakdown.tex")

plt.show()
