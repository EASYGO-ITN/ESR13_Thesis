import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_ORC_NCG_liq():
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


def get_DSC_NCG_liq():
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


def get_ORC_NCG_noliq():
    with open("../../20_SimpleORC_NCG_Reinjection_no_liq/sensitivity_results.json", "r") as file:
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


def get_DSC_NCG_noliq():
    with open("../../21_DSC_single_flash_NCG_Reinjection_no_liq/sensitivity_results.json", "r") as file:
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


ORC_Wnet_liq, ORC_Wcycle_liq, ORC_Wpara_liq, ORC_Wncg_liq, ORC_ncg_liq = get_ORC_NCG_liq()
DSC_Wnet_liq, DSC_Wcycle_liq, DSC_Wpara_liq, DSC_Wncg_liq, DSC_ncg_liq = get_DSC_NCG_liq()

ORC_Wnet_noliq, ORC_Wcycle_noliq, ORC_Wpara_noliq, ORC_Wncg_noliq, ORC_ncg_noliq = get_ORC_NCG_noliq()
DSC_Wnet_noliq, DSC_Wcycle_noliq, DSC_Wpara_noliq, DSC_Wncg_noliq, DSC_ncg_noliq = get_DSC_NCG_noliq()

fig, ax = plt.subplots(2)

ax[1].set_title("Single flash DSC")
ax[1].plot([0, DSC_ncg_liq[-1]], [0,0], "k:")
ax[1].plot(DSC_ncg_liq, DSC_Wnet_liq, label="Net")
ax[1].plot(DSC_ncg_liq, DSC_Wcycle_liq, label="Cycle")
ax[1].plot(DSC_ncg_liq, DSC_Wpara_liq, label="Parasitic")
ax[1].plot(DSC_ncg_liq, DSC_Wncg_liq, label="NCG Handling")
ax[1].set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax[1].set_ylabel("Net electrical power /\\unit{\\mega\\watt}")
ax[1].set_xlim(0, 16)
ax[1].set_ylim(-10, 10)
# ax[1].legend()

ax[0].set_title("Binary ORC")
ax[0].plot([0, ORC_ncg_liq[-1]], [0, 0], "k:")
ax[0].plot(ORC_ncg_liq, ORC_Wnet_liq, label="Net")
ax[0].plot(ORC_ncg_liq, ORC_Wcycle_liq, label="Cycle")
ax[0].plot(ORC_ncg_liq, ORC_Wpara_liq, label="Parasitic")
ax[0].plot(ORC_ncg_liq, ORC_Wncg_liq, label="NCG Handling")
ax[0].set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax[0].set_ylabel("Net electrical power /\\unit{\\mega\\watt}")
ax[0].set_ylim(-10, 10)
ax[0].set_xlim(0, 16)
ax[0].legend()

tikzplotlib.save("Plots/PowerBreakdown.tex")

plt.show()