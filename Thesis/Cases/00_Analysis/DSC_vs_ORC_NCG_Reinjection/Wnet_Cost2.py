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
    Wnet_exNCG = [np.NAN for n in ncg]
    SpecCost = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6
            power_NCG = -result["ncg_handling_power_elec"] * 1e-6

            Wnet[n_id] = power
            Wnet_exNCG[n_id] = power - power_NCG
            SpecCost[n_id] = result["Cost"]
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wnet_exNCG, SpecCost, ncgs


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
    Wnet_exNCG = [np.NAN for n in ncg]
    SpecCost = [np.NAN for n in ncg]
    ncgs = [np.NAN for n in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6
            power_NCG = -result["ncg_handling_power_elec"] * 1e-6

            Wnet[n_id] = power
            Wnet_exNCG[n_id] = power - power_NCG
            SpecCost[n_id] = result["Cost"]
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wnet_exNCG, SpecCost, ncgs


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
    Wnet_exNCG = [np.NAN for n in ncg]
    SpecCost = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6
            power_NCG = -result["ncg_handling_power_elec"] * 1e-6

            Wnet[n_id] = power
            Wnet_exNCG[n_id] = power - power_NCG
            SpecCost[n_id] = result["Cost"]
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wnet_exNCG, SpecCost, ncgs


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
    Wnet_exNCG = [np.NAN for n in ncg]
    SpecCost = [np.NAN for n in ncg]
    ncgs = [np.NAN for n in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6
            power_NCG = -result["ncg_handling_power_elec"] * 1e-6

            Wnet[n_id] = power
            Wnet_exNCG[n_id] = power - power_NCG
            SpecCost[n_id] = result["Cost"]
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wnet_exNCG, SpecCost, ncgs


def get_ORC_pureWater():
    with open("../../14_SimpleORC_pureWater/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ncg = [["water", 1.00, "carbondioxide", 0.00],
           ]

    Wnet = [np.NAN for n in ncg]
    SpecCost = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6

            Wnet[n_id] = power * 1.0
            SpecCost[n_id] = result["Cost"]
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wnet, SpecCost, ncgs


def get_DSC_pureWater():
    with open("../../15_DSC_single_flash_pureWater/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ncg = [["water", 1.00, "carbondioxide", 0.00],
           ]

    Wnet = [np.NAN for n in ncg]
    SpecCost = [np.NAN for n in ncg]
    ncgs = [np.NAN for n in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6

            Wnet[n_id] = power
            SpecCost[n_id] = result["Cost"]
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Wnet, Wnet, SpecCost, ncgs


ORC_Wnet, ORC_Wnet_exNCG, ORC_SpecCost, ORC_ncg = get_ORC_NCG_liq()
DSC_Wnet, DSC_Wnet_exNCG, DSC_SpecCost, DSC_ncg = get_DSC_NCG_liq()

ORC_Wnet_noliq, ORC_Wnet_exNCG_noliq, ORC_SpecCost_noliq, ORC_ncg_noliq = get_ORC_NCG_noliq()
DSC_Wnet_noliq, DSC_Wnet_exNCG_noliq, DSC_SpecCost_noliq, DSC_ncg_noliq = get_DSC_NCG_noliq()


fig, ax = plt.subplots(2)

ax[0].plot([0, DSC_ncg[-1]], [0, 0], "k:")
ax[0].plot(ORC_ncg, ORC_Wnet, label="Binary ORC")
ax[0].plot(DSC_ncg, DSC_Wnet, label="Single Flash DSC")
ax[0].plot(ORC_ncg_noliq, ORC_Wnet_noliq, label="Binary ORC noliq")
ax[0].plot(DSC_ncg_noliq, DSC_Wnet_noliq, label="Single Flash DSC noliq")
ax[0].set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax[0].set_ylabel("Net electrical power /\\unit{\\mega\\watt}")
ax[0].set_xlim(0, 16)
ax[0].set_ylim(-2, 10)
ax[0].legend()

ax[1].plot(ORC_ncg, ORC_SpecCost)
ax[1].plot(DSC_ncg, DSC_SpecCost)
ax[1].plot(ORC_ncg_noliq, ORC_SpecCost_noliq)
ax[1].plot(DSC_ncg_noliq, DSC_SpecCost_noliq)
ax[1].set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax[1].set_ylabel("Plant Cost/\\unit{\\mega\\USD\\of{2023}}")
ax[1].set_xlim(0, 16)
ax[1].set_ylim(0, 100)

# tikzplotlib.save("Plots/Wnet_Cost.tex")

fig, ax = plt.subplots()
ax.plot([0, DSC_ncg[-1]], [0, 0], "k:")
ax.plot(ORC_ncg, ORC_Wnet, label="Binary ORC")
ax.plot(DSC_ncg, DSC_Wnet, label="Single Flash DSC")
ax.plot(ORC_ncg_noliq, ORC_Wnet_noliq, label="Binary ORC noliq")
ax.plot(DSC_ncg_noliq, DSC_Wnet_noliq, label="Single Flash DSC noliq")
ax.set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax.set_ylabel("Net electrical power /\\unit{\\mega\\watt}")
ax.set_xlim(0, 16)
ax.set_ylim(-2, 10)
ax.legend()

# tikzplotlib.save("Plots/Wnet.tex")

fig, ax = plt.subplots()
ax.plot(ORC_ncg, ORC_SpecCost, label="Binary ORC")
ax.plot(DSC_ncg, DSC_SpecCost, label="Single Flash DSC")
ax.plot(ORC_ncg_noliq, ORC_SpecCost_noliq)
ax.plot(DSC_ncg_noliq, DSC_SpecCost_noliq)
ax.set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax.set_ylabel("Plant Cost/\\unit{\\mega\\USD\\of{2023}}")
ax.set_xlim(0, 16)
ax.set_ylim(0, 100)
ax.legend()

# tikzplotlib.save("Plots/Cost.tex")


plt.show()
