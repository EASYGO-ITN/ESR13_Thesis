import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_ORC_NCG():
    with open("../../14_SimpleORC_NCG_CarbFix_final/sensitivity_results.json", "r") as file:
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

    Pin = [np.NAN for n in ncg]
    Pabsorb = [np.NAN for f in ncg]
    Pout = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            Pin[n_id] = result["P_in"]* 1e-5
            Pabsorb[n_id] = result["P_Absorption"]* 1e-5
            Pout[n_id] = result["P_out"]* 1e-5
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Pin, Pabsorb, Pout, ncgs


def get_DSC_NCG():
    with open("../../15_DSC_single_flash_NCG_CarbFix_final/sensitivity_results.json", "r") as file:
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

    Pin = [np.NAN for n in ncg]
    Pmin = [np.NAN for n in ncg]
    Pabsorb = [np.NAN for f in ncg]
    Pout = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue


            Pin[n_id] = result["P_in"] * 1e-5
            Pmin[n_id] = result["Pmin"] * 1e-5
            Pabsorb[n_id] = result["P_Absorption"] * 1e-5
            Pout[n_id] = result["P_out"]* 1e-5
            ncgs[n_id] = ncg[n_id][-1] * 100

    return Pin, Pmin, Pabsorb, Pout, ncgs


ORC_Pin, ORC_Pabsorb, ORC_Pout, ORC_ncg = get_ORC_NCG()
DSC_Pin, DSC_Pmin, DSC_Pabsorb, DSC_Pout, DSC_ncg = get_DSC_NCG()

fig, ax = plt.subplots()

ax.plot(ORC_ncg, ORC_Pin, label="DSC/ORC Inlet")
ax.plot(DSC_ncg, DSC_Pmin, label="DSC Condenser")
ax.plot(ORC_ncg, ORC_Pout, label="DSC/ORC Outlet")

ax.plot(ORC_ncg, ORC_Pabsorb, label="ORC Absorber")
ax.plot(DSC_ncg, DSC_Pabsorb, label="DSC Absorber")

# ax.plot(DSC_ncg, DSC_Pout, label="DSC")

ax.set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax.set_ylabel("Pressure/\\unit{\\bar}")
ax.set_yscale("log")

ax.legend()

tikzplotlib.save("Plots/OPs")


plt.show()