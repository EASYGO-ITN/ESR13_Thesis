import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

def get_DSC_NCG():
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

    xout = [np.NAN for n in ncg]
    eta_isen = [np.NAN for f in ncg]
    ncgs = [np.NAN for f in ncg]

    for result in results:
        if result:

            if result["Hot fluid comp"] in ncg:
                n_id = ncg.index(result["Hot fluid comp"])
            else:
                continue

            xout[n_id] = result["Qturb_out"] * 100
            eta_isen[n_id] = result["Eta_isen_turb_app"] * 100
            ncgs[n_id] = ncg[n_id][-1] * 100

    return xout, eta_isen, ncgs


DSC_xout, DSC_eta, DSC_ncg = get_DSC_NCG()

fig, ax = plt.subplots()

ax.plot(DSC_ncg, DSC_xout, label="Outlet Quality")

ax.plot(DSC_ncg, DSC_eta, label="Efficiency")

ax.set_xlabel("Geofluid \\ce{CO2} content/\\unit{\\mol\\percent}")
ax.set_ylabel("Efficiency/\\unit{\\percent}")
ax.legend()

# tikzplotlib.save("Plots/Quality.tex")

plt.show()