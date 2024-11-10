import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_ORC_thermo_results(res_str, conv=1.0, min_val=True):
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
    qs= [0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 100.0]
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
            try:
                t_id = ts.index(result["Hot fluid input1"])
                q_id = qs.index(result["Hot fluid input2"]*100)
                f_id = fluids.index(result["Working fluid comp"])

                temp_res = result[res_str] * conv

                res[f_id][t_id][q_id] = temp_res

                if min_val:
                    if temp_res < res_best[t_id][q_id]:
                        res_best[t_id][q_id] = temp_res
                else:
                    if temp_res > res_best[t_id][q_id]:
                        res_best[t_id][q_id] = temp_res
            except:
                pass

    # qs = [q * 100 for q in qs]

    return res_best, res, ts, qs


def get_ORC_techno_results(res_str, conv=1.0, min_val=True):
    with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
        results_a = json.load(file)

    with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
        results_b = json.load(file)

    with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
        results_c = json.load(file)

    results = results_a + results_b + results_c

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

            temp_res = result[res_str] * conv

            res[f_id][t_id][q_id] = temp_res

            if min_val:
                if temp_res < res_best[t_id][q_id]:
                    res_best[t_id][q_id] = temp_res
            else:
                if temp_res > res_best[t_id][q_id]:
                    res_best[t_id][q_id] = temp_res

    qs = [q * 100 for q in qs]

    return res_best, res, ts, qs


# power delta power
if __name__ == "__main__":

    ORC_Wnet_best_thermo, ORC_Wnet_thermo, ORC_ts_thermo, ORC_qs_thermo = get_ORC_thermo_results("NetPow_elec", conv=-1e-6, min_val=False)
    ORC_Wnet_best_techno, ORC_Wnet_techno, ORC_ts_techno, ORC_qs_techno = get_ORC_techno_results("NetPow_elec", conv=-1e-6, min_val=False)

    fig, ax = plt.subplots(2)
    twin = ax[1].twinx()
    colors = [plt.cm.Greens([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Oranges([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Greys([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              ]

    for i, t in enumerate(ORC_ts_thermo):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}"

        diff = (np.array(ORC_Wnet_best_techno[i]) - np.array(ORC_Wnet_best_thermo[i]))
        ax[0].plot([0,1], [-1,-1], label=label, color=colors[2][i])
        ax[0].plot(ORC_qs_thermo, ORC_Wnet_best_techno[i], color=colors[1][i])
        twin.plot(ORC_qs_thermo, 100*diff/np.array(ORC_Wnet_best_thermo[i]), color=colors[0][i])
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

# spec cost and delta spec costs
if __name__ == "__main__":

    ORC_SpecCost_best_thermo, ORC_SpecCost_thermo, ORC_ts_thermo, ORC_qs_thermo = get_ORC_thermo_results("SpecificCost")
    ORC_SpecCost_best_techno, ORC_SpecCost_techno, ORC_ts_techno, ORC_qs_techno = get_ORC_techno_results("SpecificCost")

    fig, ax = plt.subplots(2)
    twin = ax[1].twinx()
    colors = [plt.cm.Greens([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Oranges([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              plt.cm.Greys([0.25, 0.375,0.45, 0.65, 0.85, 1 ]),
              ]

    for i, t in enumerate(ORC_ts_techno):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"

        diff = (np.array(ORC_SpecCost_best_techno[i]) - np.array(ORC_SpecCost_best_thermo[i]))
        ax[0].plot([0, 1], [-1, -1], label=label, color=colors[2][i])
        ax[0].plot(ORC_qs_techno, ORC_SpecCost_best_techno[i], color=colors[1][i])
        twin.plot(ORC_qs_techno, 100*diff/np.array(ORC_SpecCost_best_thermo[i]), color=colors[0][i])
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

plt.show()
