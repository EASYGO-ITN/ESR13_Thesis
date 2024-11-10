import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_DSC_results(res_str):
    with open("../../18_DSC_single_flash_NCG_Venting_final/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ncg = [["water", 0.99, "carbondioxide", 0.01],
           ["water", 0.98, "carbondioxide", 0.02],
           ["water", 0.97, "carbondioxide", 0.03],
           ["water", 0.96, "carbondioxide", 0.04],
           ["water", 0.95, "carbondioxide", 0.05],
           ["water", 0.93, "carbondioxide", 0.07],
           ["water", 0.91, "carbondioxide", 0.09],
           ["water", 0.89, "carbondioxide", 0.11],
           ["water", 0.87, "carbondioxide", 0.13],
           ["water", 0.85, "carbondioxide", 0.15]
           ]

    res = [np.NAN + 0 for q in ncg]
    zs = [np.NAN + 0 for q in ncg]

    for result in results:
        if result:
            z_id = ncg.index(result["Hot fluid comp"])

            temp_res = result[res_str]
            res[z_id] = temp_res
            zs[z_id] = result["Hot fluid comp"][3]*100

    return res, zs


def get_ORC_results(res_str):
    with open("../../16_SimpleORC_NCG_Venting_final/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ncg = [["water", 0.99, "carbondioxide", 0.01],
           ["water", 0.98, "carbondioxide", 0.02],
           ["water", 0.97, "carbondioxide", 0.03],
           ["water", 0.96, "carbondioxide", 0.04],
           ["water", 0.95, "carbondioxide", 0.05],
           ["water", 0.93, "carbondioxide", 0.07],
           ["water", 0.91, "carbondioxide", 0.09],
           ["water", 0.89, "carbondioxide", 0.11],
           ["water", 0.87, "carbondioxide", 0.13],
           ["water", 0.85, "carbondioxide", 0.15]
           ]

    res = [np.NAN + 0 for q in ncg]
    zs = [np.NAN + 0 for q in ncg]

    for result in results:
        if result:
            z_id = ncg.index(result["Hot fluid comp"])

            temp_res = result[res_str]
            res[z_id] = temp_res
            zs[z_id] = result["Hot fluid comp"][3] * 100

    return res, zs


DSC_Costs, DSC_zs, = get_DSC_results("Costs")
ORC_Costs, ORC_zs, = get_ORC_results("Costs")

# plotting DSC costs
if __name__ == "__main__":
    equips = {"Turbine": "Turbine",
              "FlashSep": "Other Equipment",
              "NCGSep": "NCG Handling",
              "Condenser": "Condenser",
              "BrinePump": "Repressurisation",
              "CondPump": "Repressurisation",
              "NCGComp": "NCG Handling",
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
    ordered_equips = ['Turbine', 'Condenser', 'Other Equipment', 'Repressurisation', 'NCG Handling', 'PHE', 'Pump',
                      'Recuperator', 'Construction', ]
    for equip in equips:
        if equips[equip] not in unique_equips_:
            unique_equips_.append(equips[equip])

    unique_equips = []
    for equip in ordered_equips:
        if equip in unique_equips_:
            unique_equips.append(equip)

    DSC_results = {equip: np.zeros(len(DSC_zs)) for equip in unique_equips}
    DSC_totals = np.zeros(len(DSC_zs))

    for i, Costs in enumerate(DSC_Costs):

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
            DSC_totals[i] += value

    removals = []
    for item in DSC_results:
        if sum(DSC_results[item]) == 0:
            removals.append(item)

    for remove in removals:
        del DSC_results[remove]

    fig, ax = plt.subplots(ncols=2)

    xlabel = [q for q in DSC_zs]
    bottom = np.zeros(len(DSC_zs))
    for label, costs in DSC_results.items():
        p = ax[0].bar(xlabel, costs, 1, label=label, bottom=bottom)
        bottom += costs

    ax[0].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].legend()


    xlabel = [q for q in DSC_zs]
    bottom = np.zeros(len(DSC_zs))

    for item in DSC_results:
        DSC_results[item] /= DSC_totals * 0.01

    for label, costs in DSC_results.items():
        p = ax[1].bar(xlabel, costs, 1, label=label, bottom=bottom)
        bottom += costs

    ax[1].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Cost Contribution/\\unit{\\percent}")
    # ax[1].legend()

    tikzplotlib.save("Plots/CostBreakdown_DSC.tex")

# plotting ORC costs
if __name__ == "__main__":
    equips = {"Turbine": "Turbine",
              "FlashSep": "Other Equipment",
              "NCGSep": "NCG Handling",
              "Condenser": "Condenser",
              "BrinePump": "Repressurisation",
              "CondPump": "Repressurisation",
              "NCGComp": "NCG Handling",
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
    ordered_equips = ['Turbine', 'Condenser', 'Other Equipment', 'Repressurisation', 'NCG Handling', 'PHE', 'Pump',
                      'Recuperator', 'Construction', ]
    for equip in equips:
        if equips[equip] not in unique_equips_:
            unique_equips_.append(equips[equip])

    unique_equips = []
    for equip in ordered_equips:
        if equip in unique_equips_:
            unique_equips.append(equip)

    ORC_results = {equip: np.zeros(len(ORC_zs)) for equip in unique_equips}
    ORC_totals = np.zeros(len(ORC_zs))

    for i, Costs in enumerate(ORC_Costs):

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

            ORC_results[equip][i] += value
            ORC_totals[i] += value

    removals = []
    for item in ORC_results:
        if sum(ORC_results[item]) == 0:
            removals.append(item)

    for remove in removals:
        del ORC_results[remove]

    fig, ax = plt.subplots(ncols=2)

    xlabel = [q for q in ORC_zs]
    bottom = np.zeros(len(ORC_zs))
    for label, costs in ORC_results.items():
        p = ax[0].bar(xlabel, costs, 1, label=label, bottom=bottom)
        bottom += costs

    ax[0].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].legend()


    xlabel = [q for q in ORC_zs]
    bottom = np.zeros(len(ORC_zs))

    for item in ORC_results:
        ORC_results[item] /= ORC_totals * 0.01

    for label, costs in ORC_results.items():
        p = ax[1].bar(xlabel, costs, 1, label=label, bottom=bottom)
        bottom += costs

    ax[1].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Cost Contribution/\\unit{\\percent}")
    # ax[1].legend()

    tikzplotlib.save("Plots/CostBreakdown_ORC.tex")

# plotting both
if __name__ == "__main__":

    fig, ax = plt.subplots(ncols=2)

    xlabel = [q for q in ORC_zs]
    bottom = np.zeros(len(ORC_zs))
    for label, costs in ORC_results.items():
        p = ax[0].bar(xlabel, costs, 1, label=label, bottom=bottom)
        bottom += costs

    ax[0].set_title("Binary ORC")
    ax[0].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].legend()


    xlabel = [q for q in DSC_zs]
    bottom = np.zeros(len(DSC_zs))
    for label, costs in DSC_results.items():
        p = ax[1].bar(xlabel, costs, 1, label=label, bottom=bottom)
        bottom += costs

    ax[1].set_title("Single flash DSC")
    ax[1].set_xlabel("Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[1].legend()

    tikzplotlib.save("Plots/CostBreakdown_ORC_DSC.tex")

plt.show()
