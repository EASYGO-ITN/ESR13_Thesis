import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

file_path_thermo = "../../06_DSC_single_flash/sensitivity_results.json"
file_path_techno = "../../10_DSC_single_flash_techno_specCost/sensitivity_results.json"

show_change = False

def get_DSC_results(filepath, res_str, conv=1.0):
    with open(filepath, "r") as file:
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

            res[t_id][q_id] = result[res_str] * conv

    qs = [q * 100 for q in qs]

    return res, ts, qs


# power and delta Power
if __name__ == "__main__":


    DSC_Wnet_thermo, DSC_ts_thermo, DSC_qs_thermo = get_DSC_results(file_path_thermo, "NetPow_elec", conv=-1e-6)
    DSC_Wnet_techno, DSC_ts_techno, DSC_qs_techno = get_DSC_results(file_path_techno, "NetPow_elec", conv=-1e-6)

    fig, ax = plt.subplots(2)
    twin = ax[1].twinx()
    colors = [plt.cm.Greens([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Oranges([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Greys([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              ]

    for i, t in enumerate(DSC_ts_thermo):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"

        diff = (np.array(DSC_Wnet_techno[i]) - np.array(DSC_Wnet_thermo[i]))
        ax[0].plot([0,1], [-1,-1], label=label, color=colors[2][i])
        ax[0].plot(DSC_qs_thermo, DSC_Wnet_techno[i], color=colors[1][i])
        twin.plot(DSC_qs_thermo, 100*diff/np.array(DSC_Wnet_thermo[i]), color=colors[0][i])
        ax[1].plot([0, 100], [diff.min(), diff.max()], linestyle='', marker="")

    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax[0].set_ylim(0, None)
    ax[0].legend()

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Delta net electric power/\\unit{\\mega\\watt}")
    ax[1].set_ylim(None, 0)

    twin.set_ylabel("Delta net electric power/\\unit{\\percent}")
    twin.set_ylim(None, 0)

    tikzplotlib.save("Plots/DWnet.tex")


# spec cost and delta spec cost
if __name__ == "__main__":


    DSC_Wnet_thermo, DSC_ts_thermo, DSC_qs_thermo = get_DSC_results(file_path_thermo, "SpecificCost")
    DSC_Wnet_techno, DSC_ts_techno, DSC_qs_techno = get_DSC_results(file_path_techno, "SpecificCost")

    fig, ax = plt.subplots(2)
    twin = ax[1].twinx()
    colors = [plt.cm.Greens([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
              plt.cm.Oranges([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
              plt.cm.Greys([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
              ]

    for i, t in enumerate(DSC_ts_thermo):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"

        diff = (np.array(DSC_Wnet_techno[i]) - np.array(DSC_Wnet_thermo[i]))
        ax[0].plot([0, 1], [-1, -1], label=label, color=colors[2][i])
        ax[0].plot(DSC_qs_thermo, DSC_Wnet_techno[i], color=colors[1][i])
        twin.plot(DSC_qs_thermo, 100*diff/np.array(DSC_Wnet_thermo[i]), color=colors[0][i])
        ax[1].plot([0, 100], [diff.min(), diff.max()], linestyle='', marker="")

    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
    ax[0].set_ylim(0, None)
    ax[0].legend()

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Delta Specific Cost/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
    ax[1].set_ylim(None, 0)

    twin.set_ylabel("Delta Specific Cost/\\unit{\\percent}")
    twin.set_ylim(None, 0)

    tikzplotlib.save("Plots/DSpecCost.tex")

# LCOE
if __name__ == "__main_":

    DSC_LCOE_thermo, DSC_ts_thermo, DSC_qs_thermo = get_DSC_results(file_path_thermo, "LCOE")
    DSC_LCOE_techno, DSC_ts_techno, DSC_qs_techno = get_DSC_results(file_path_techno, "LCOE")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Oranges([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Greys([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              ]

    ax.plot([0, 1], [-1, -1], label="Thermodynamic Optimisation", color=colors[0][2])
    ax.plot([0, 1], [-1, -1], label="Techno-economic Optimisation", color=colors[1][3])

    for i, t in enumerate(DSC_ts_thermo):
        ax.plot([0, 1], [-1,-1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(DSC_LCOE_thermo):
        ax.plot(DSC_qs_thermo, t, color=colors[0][i])

    for i, t in enumerate(DSC_LCOE_techno):
        ax.plot(DSC_qs_techno, t, color=colors[1][i])

    if show_change:
        twin = ax.twinx()

        for i, t in enumerate(DSC_LCOE_techno):
            techno = np.array(t)
            thermo = np.array(DSC_LCOE_thermo[i])
            twin.plot(DSC_qs_techno, (thermo - techno) / thermo, color=colors[2][i])

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")
    ax.set_ylim(0, None)
    ax.legend()

    tikzplotlib.save("Plots/LCOE.tex")

plt.show()
