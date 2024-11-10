import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_ORC_results(filepath, res_str, conv=1.0, min_val=True):
    with open(filepath, "r") as file:
        results = json.load(file)

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
    fluids.sort()

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

ORC_filename = "../../02_SimpleORC_superheated/sensitivity_results.json"
OtherORC_filename = "../../04_SimpleORC_superheated_recuperated/sensitivity_results.json"

ORC_series_name = "Superheated ORC"
Other_ORC_series_name = "Recup. Superh. ORC"

plotname_Wnet = "Plots/SupH_ORC_vs_ORCsuperheated_recuperated_Wnet.tex"
plotname_specCost = "Plots/SupH_ORC_vs_ORCsuperheated_recuperated_specCost.tex"
plotname_LCOE = "Plots/SupH_ORC_vs_ORCsuperheated_recuperated_LCOE.tex"
plotname_map = "Plots/SupH_ORC_vs_ORCsuperheated_recuperated_breakeven_map.tex"

OtherORC_Wnet_best, OtherORC_Wnet, OtherORC_ts, OtherORC_qs = get_ORC_results(OtherORC_filename, "NetPow_elec", conv=-1e-6, min_val=False)
OtherORC_SpecCost_best, OtherORC_SpecCost, OtherORC_ts, OtherORC_qs = get_ORC_results(OtherORC_filename, "SpecificCost",)
OtherORC_LCOE_best, OtherORC_LCOE, OtherORC_ts, OtherORC_qs = get_ORC_results(OtherORC_filename, "LCOE",)

ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs = get_ORC_results(ORC_filename, "NetPow_elec", conv=-1e-6, min_val=False)
ORC_SpecCost_best, ORC_SpecCost, ORC_ts, ORC_qs = get_ORC_results(ORC_filename, "SpecificCost")
ORC_LCOE_best, ORC_LCOE, ORC_ts, ORC_qs = get_ORC_results(ORC_filename, "LCOE")

try:
    tar_id = ORC_qs.index(90.0)
    for i, t in enumerate(ORC_Wnet_best):
        del ORC_Wnet_best[i][tar_id]
        del ORC_SpecCost_best[i][tar_id]
        del ORC_LCOE_best[i][tar_id]
    del ORC_qs[tar_id]
except:
    pass

colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
          plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
          plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
          ]

gfig, gax = plt.subplots()

gax.fill_between([0, 100], [550, 550], [551, 551], color="k", alpha=0.3, label="Binary ORC")

# power
if __name__ == "__main__":

    fig, ax = plt.subplots()

    ax.plot([0, 1], [1, 1], label=ORC_series_name, color=colors[0][2])
    ax.plot([0, 1], [1, 1], label=Other_ORC_series_name, color=colors[1][3])

    ORC_Wnet_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1, 1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    OtherORC_Wnet_best.reverse()
    OtherORC_ts.reverse()
    for i, t in enumerate(OtherORC_Wnet_best):
        ax.plot(OtherORC_qs, t, color=colors[1][i])

    qs_even = []
    ts_even = []
    Wnet_even = []

    ts_map =[]
    qs_map=[]
    for i, W in enumerate(OtherORC_Wnet_best):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_Wnet_best[i])
        qs = np.array(OtherORC_qs)

        diff = W_DSC-W_ORC
        break_q = np.interp(0, diff, qs)
        break_W = np.interp(break_q, qs, W_DSC)

        qs_even.append(break_q)
        Wnet_even.append(break_W)

        ts_map.append(OtherORC_ts[i])
        qs_map.append(break_q)

    q_max = [0 for q in qs_map]
    gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, label="Net Power")

    ax.plot(qs_even, Wnet_even, "ro", label="Break-even")

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax.legend()

    tikzplotlib.save(plotname_Wnet)

# spec costs
if __name__ == "__main__":

    fig, ax = plt.subplots()

    ax.plot([0, 1], [1, 1], label=ORC_series_name, color=colors[0][2])
    ax.plot([0, 1], [1, 1], label=Other_ORC_series_name, color=colors[1][3])

    ORC_SpecCost_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_SpecCost_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    OtherORC_SpecCost_best.reverse()
    OtherORC_ts.reverse()
    for i, t in enumerate(OtherORC_SpecCost_best):
        ax.plot(ORC_qs, t, color=colors[1][i])

    qs_even = []
    SpecCost_even = []

    ts_map = []
    qs_map = []
    for i, W in enumerate(OtherORC_SpecCost_best):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_SpecCost_best[i])
        qs = np.array(OtherORC_qs)

        diff = W_DSC - W_ORC

        if diff.min() < 0.0 < diff.max():
            indices = np.argsort(diff)

            temp_diff = diff[indices]
            temp_qs = qs[indices]
            temp_W_DSC = W_DSC[indices]

            break_q = np.interp(0, temp_diff, temp_qs)
            break_W = np.interp(break_q, qs, W_DSC)

            qs_even.append(break_q)
            SpecCost_even.append(break_W)

            ts_map.append(OtherORC_ts[i])
            qs_map.append(break_q)
        elif diff.min() >= 0.0:
            ts_map.append(OtherORC_ts[i])
            qs_map.append(100)
        elif diff.max() <= 0.0:
            ts_map.append(OtherORC_ts[i])
            qs_map.append(0)

    t_max = [550 for q in qs_map]
    q_max = [0 for q in qs_map]
    # gax.fill_between(qs_map, ts_map, t_max, alpha=0.3)
    gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, label="Specific Cost")

    ax.plot(qs_even, SpecCost_even, "ro", label="Break-even")

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax.legend()

    tikzplotlib.save(plotname_specCost)

# LCOE
if __name__ == "__main__":

    fig, ax = plt.subplots()

    ax.plot([0, 1], [1, 1], label=ORC_series_name, color=colors[0][2])
    ax.plot([0, 1], [1, 1], label=Other_ORC_series_name, color=colors[1][3])

    ORC_LCOE_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_LCOE_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    OtherORC_LCOE_best.reverse()
    OtherORC_ts.reverse()
    for i, t in enumerate(OtherORC_LCOE_best):
        ax.plot(OtherORC_qs, t, color=colors[1][i])

    qs_even = []
    ts_map = []
    qs_map = []
    LCOE_even = []
    for i, W in enumerate(OtherORC_LCOE_best):

        W_DSC = np.array(W)
        W_ORC = np.array(ORC_LCOE_best[i])
        qs = np.array(OtherORC_qs)

        diff = W_DSC - W_ORC

        if diff.min() < 0.0 < diff.max():
            indices = np.argsort(diff)

            temp_diff = diff[indices]
            temp_qs = qs[indices]
            temp_W_DSC = W_DSC[indices]

            break_q = np.interp(0, temp_diff, temp_qs)
            break_W = np.interp(break_q, qs, W_DSC)

            qs_even.append(break_q)
            LCOE_even.append(break_W)

            ts_map.append(OtherORC_ts[i])
            qs_map.append(break_q)
        elif diff.min() >= 0.0:
            ts_map.append(OtherORC_ts[i])
            qs_map.append(100)
        elif diff.max() <= 0.0:
            ts_map.append(OtherORC_ts[i])
            qs_map.append(0)

    t_max = [550 for q in qs_map]
    q_max = [0 for q in qs_map]
    gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, label="LCOE")

    ax.plot(qs_even, LCOE_even, "ro", label="Break-even")

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")
    ax.legend()

    tikzplotlib.save(plotname_LCOE)

gax.set_xlabel("Geofluid Inlet Steam Quality/\\unit{\\percent}")
gax.set_ylabel("Geofluid Inlet Temperature/\\unit{\\K}")
gax.set_xlim(0, 100)
gax.set_ylim(423, 548)
gax.legend()

tikzplotlib.save(plotname_map, figure=gfig)


plt.show()
