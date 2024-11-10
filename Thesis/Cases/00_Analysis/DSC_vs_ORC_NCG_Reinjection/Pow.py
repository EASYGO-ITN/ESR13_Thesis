import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_ORC_NCG():
    with open("../../17_SimpleORC_NCG_Reinjection_final/sensitivity_results.json", "r") as file:
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

    Wnet = [np.NAN for n in ncg]
    Wcycle = [np.NAN for n in ncg]
    Wpara = [np.NAN for f in ncg]
    Wncg = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            Wnet[n_id] = -result["NetPow_elec"] * 1e-6
            Wcycle[n_id] = -result["CyclePow_elec"] * 1e-6
            Wpara[n_id] = -result["ParasiticPow_elec"] * 1e-6
            Wncg[n_id] = -result["ncg_handling_power_elec"] * 1e-6
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wcycle, Wpara, Wncg, ncgs


def get_DSC_NCG():
    with open("../../19_DSC_single_flash_NCG_Reinjection_final/sensitivity_results.json", "r") as file:
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

    Wnet = [np.NAN for n in ncg]
    Wcycle = [np.NAN for n in ncg]
    Wpara = [np.NAN for f in ncg]
    Wncg = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6
            power_NCG = -result["ncg_handling_power_elec"] * 1e-6

            Wnet[n_id] = -result["NetPow_elec"] * 1e-6
            Wcycle[n_id] = -result["CyclePow_elec"] * 1e-6
            Wpara[n_id] = -result["ParasiticPow_elec"] * 1e-6
            Wncg[n_id] = -result["ncg_handling_power_elec"] * 1e-6
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wcycle, Wpara, Wncg, ncgs


# def get_ORC_pureWater():
#     with open("../../14_SimpleORC_pureWater/sensitivity_results.json", "r") as file:
#         results = json.load(file)
#
#     ncg = [["water", 1.00, "carbondioxide", 0.00],
#            ]
#
#     Wnet = [np.NAN for n in ncg]
#     SpecCost = [np.NAN for f in ncg]
#     ncgs = [np.NAN for f in ncg]
#
#     for result in results:
#         if result:
#
#             if result["Hot fluid comp"] in ncg:
#                 n_id = ncg.index(result["Hot fluid comp"])
#             else:
#                 continue
#
#             power = -result["NetPow_elec"] * 1e-6
#
#             Wnet[n_id] = power * 1.0
#             SpecCost[n_id] = result["Cost"]
#             ncgs[n_id] = ncg[n_id][-1] * 100
#
#     return Wnet, Wnet, SpecCost, ncgs


# def get_DSC_pureWater():
#     with open("../../15_DSC_single_flash_pureWater/sensitivity_results.json", "r") as file:
#         results = json.load(file)
#
#     ncg = [["water", 1.00, "carbondioxide", 0.00],
#            ]
#
#     Wnet = [np.NAN for n in ncg]
#     SpecCost = [np.NAN for n in ncg]
#     ncgs = [np.NAN for n in ncg]
#
#     for result in results:
#         if result:
#
#             if result["Hot fluid comp"] in ncg:
#                 n_id = ncg.index(result["Hot fluid comp"])
#             else:
#                 continue
#
#             power = -result["NetPow_elec"] * 1e-6
#
#             Wnet[n_id] = power
#             SpecCost[n_id] = result["Cost"]
#             ncgs[n_id] = ncg[n_id][-1] * 100
#
#     return Wnet, Wnet, SpecCost, ncgs


# ORC_Wnet_w, ORC_Wnet_exNCG_w, ORC_SpecCost_w, ORC_ncg_w = get_ORC_pureWater()
# DSC_Wnet_w, DSC_Wnet_exNCG_w, DSC_SpecCost_w, DSC_ncg_w = get_DSC_pureWater()

ORC_Wnet, ORC_Wcycle, ORC_Wpara, ORC_Wncg, ORC_ncg = get_ORC_NCG()
DSC_Wnet, DSC_Wcycle, DSC_Wpara, DSC_Wncg, DSC_ncg = get_DSC_NCG()

# ORC_Wnet = ORC_Wnet_w + ORC_Wnet
# ORC_Wnet_exNCG = ORC_Wnet_exNCG_w + ORC_Wnet_exNCG
# ORC_SpecCost = ORC_SpecCost_w + ORC_SpecCost
# ORC_ncg = ORC_ncg_w + ORC_ncg
#
# DSC_Wnet = DSC_Wnet_w + DSC_Wnet
# DSC_Wnet_exNCG = DSC_Wnet_exNCG_w + DSC_Wnet_exNCG
# DSC_SpecCost = DSC_SpecCost_w + DSC_SpecCost
# DSC_ncg = DSC_ncg_w + DSC_ncg

fig, ax = plt.subplots(2)

ax[1].set_title("Single flash DSC")
ax[1].plot([0, DSC_ncg[-1]], [0,0], "k:")
ax[1].plot(DSC_ncg, DSC_Wnet, label="Net")
ax[1].plot(DSC_ncg, DSC_Wcycle, label="Cycle")
ax[1].plot(DSC_ncg, DSC_Wpara, label="Parasitic")
ax[1].plot(DSC_ncg, DSC_Wncg, label="NCG Handling")
ax[1].set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax[1].set_ylabel("Net electrical power /\\unit{\\mega\\watt}")
ax[1].set_xlim(0, 16)
ax[1].set_ylim(-10, 10)
# ax[1].legend()

ax[0].set_title("Binary ORC")
ax[0].plot([0, ORC_ncg[-1]], [0, 0], "k:")
ax[0].plot(ORC_ncg, ORC_Wnet, label="Net")
ax[0].plot(ORC_ncg, ORC_Wcycle, label="Cycle")
ax[0].plot(ORC_ncg, ORC_Wpara, label="Parasitic")
ax[0].plot(ORC_ncg, ORC_Wncg, label="NCG Handling")
ax[0].set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax[0].set_ylabel("Net electrical power /\\unit{\\mega\\watt}")
ax[0].set_ylim(-10, 10)
ax[0].set_xlim(0, 16)
ax[0].legend()

tikzplotlib.save("Plots/PowerBreakdown.tex")

plt.show()