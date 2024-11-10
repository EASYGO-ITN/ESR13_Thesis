import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

def get_DSC_results(res_str, conv=1.0):
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

            res[t_id][q_id] = result[res_str] * conv

    qs = [q * 100 for q in qs]

    tar_id = qs.index(90.0)
    for i, t in enumerate(res):
        del res[i][tar_id]
    del qs[tar_id]

    return res, ts, qs


def get_ORC_results(res_str, conv=1.0, min_val=True):
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

gfig, gax = plt.subplots()

gax.fill_between([0, 100], [550, 550], [551, 551], color="k", alpha=0.3, label="Binary ORC")

# power
if __name__ == "__main__":

    DSC_Wnet, DSC_ts, DSC_qs = get_DSC_results("NetPow_elec", conv=-1e-6)
    ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs = get_ORC_results("NetPow_elec", conv=-1e-6, min_val=False)

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    ORC_Wnet_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    DSC_Wnet.reverse()
    DSC_ts.reverse()
    for i, t in enumerate(DSC_Wnet):
        ax.plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    ts_even = []
    Wnet_even = []

    ts_map =[]
    qs_map=[]
    for i, W in enumerate(DSC_Wnet):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_Wnet_best[i])
        qs = np.array(DSC_qs)

        diff = W_DSC-W_ORC
        break_q = np.interp(0, diff, qs)
        break_W = np.interp(break_q, qs, W_DSC)

        qs_even.append(break_q)
        Wnet_even.append(break_W)

        ts_map.append(DSC_ts[i])
        qs_map.append(break_q)

    q_max = [0 for q in qs_map]
    gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, label="Net Power")

    ax.plot(qs_even, Wnet_even, "ro", label="Break-even")

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax.legend()

    tikzplotlib.save("Plots/DSC_vs_ORC_Wnet.tex")

# LEGACY costs
if __name__ == "__main_":
    DSC_Cost, DSC_ts, DSC_qs = get_DSC_results("Cost")
    ORC_Cost_best, ORC_Cost, ORC_ts, ORC_qs = get_ORC_results("Cost")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    ORC_Cost_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Cost_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    DSC_Cost.reverse()
    DSC_ts.reverse()
    for i, t in enumerate(DSC_Cost):
        ax.plot(DSC_qs, t, color=colors[1][i])


    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax.legend()

    # tikzplotlib.save("Plots/DSC_vs_ORC_Cost.tex")

# spec costs
if __name__ == "__main_":
    DSC_SpecCost, DSC_ts, DSC_qs = get_DSC_results("SpecificCost")
    ORC_SpecCost_best, ORC_SpecCost, ORC_ts, ORC_qs = get_ORC_results("SpecificCost")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    ORC_SpecCost_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_SpecCost_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    DSC_SpecCost.reverse()
    DSC_ts.reverse()
    for i, t in enumerate(DSC_SpecCost):
        ax.plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    SpecCost_even = []

    ts_map = []
    qs_map = []
    for i, W in enumerate(DSC_SpecCost):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_SpecCost_best[i])
        qs = np.array(DSC_qs)

        diff = W_DSC - W_ORC

        if diff.min() < 0.0 < diff.max():
            indices = np.argsort(diff)

            temp_diff = diff[indices]
            temp_qs = qs[indices]
            temp_W_DSC = W_DSC[indices]

            break_q = np.interp(0, temp_diff, temp_qs)
            break_W = np.interp(break_q, qs, temp_W_DSC)

            qs_even.append(break_q)
            SpecCost_even.append(break_W)

            ts_map.append(DSC_ts[i])
            qs_map.append(break_q)
        elif diff.min() >= 0.0:
            ts_map.append(DSC_ts[i])
            qs_map.append(100)
        elif diff.max() <= 0.0:
            ts_map.append(DSC_ts[i])
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

    tikzplotlib.save("Plots/DSC_vs_ORC_SpecCost.tex")

if __name__ == "__main__":
    DSC_SpecCost, DSC_ts, DSC_qs = get_DSC_results("SpecificCost")
    ORC_SpecCost_best, ORC_SpecCost, ORC_ts, ORC_qs = get_ORC_results("SpecificCost")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    ORC_SpecCost_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_SpecCost_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    DSC_SpecCost.reverse()
    DSC_ts.reverse()
    for i, t in enumerate(DSC_SpecCost):
        ax.plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    SpecCost_even = []

    ts_map = []
    qs_map = []
    for i, W in enumerate(DSC_SpecCost):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_SpecCost_best[i])
        qs = np.array(DSC_qs)

        diff = W_DSC - W_ORC

        if diff.min() < 0.0 < diff.max():

            tar_i = 0
            while diff[tar_i+1] > 0.0:
                tar_i += 1

            m_a = (W_DSC[tar_i+1] - W_DSC[tar_i]) / (qs[tar_i+1] - qs[tar_i])
            c_a = W_DSC[tar_i] - qs[tar_i]*m_a

            m_b = (W_ORC[tar_i+1] - W_ORC[tar_i]) / (qs[tar_i+1] - qs[tar_i])
            c_b = W_ORC[tar_i] - qs[tar_i]*m_b

            break_q = (c_a - c_b) / (m_b - m_a)
            break_W = m_a * break_q + c_a

            qs_even.append(break_q)
            SpecCost_even.append(break_W)

            ts_map.append(DSC_ts[i])
            qs_map.append(break_q)
        elif diff.min() >= 0.0:
            ts_map.append(DSC_ts[i])
            qs_map.append(100)
        elif diff.max() <= 0.0:
            ts_map.append(DSC_ts[i])
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

    tikzplotlib.save("Plots/DSC_vs_ORC_SpecCost.tex")

# LCOE
if __name__ == "__main_":
    DSC_LCOE, DSC_ts, DSC_qs = get_DSC_results("LCOE")
    ORC_LCOE_best, ORC_LCOE, ORC_ts, ORC_qs = get_ORC_results("LCOE")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    ORC_LCOE_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_LCOE_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    DSC_LCOE.reverse()
    DSC_ts.reverse()
    for i, t in enumerate(DSC_LCOE):
        ax.plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    ts_map = []
    qs_map = []
    LCOE_even = []
    for i, W in enumerate(DSC_LCOE):

        W_DSC = np.array(W)
        W_ORC = np.array(ORC_LCOE_best[i])
        qs = np.array(DSC_qs)

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

            ts_map.append(DSC_ts[i])
            qs_map.append(break_q)
        elif diff.min() >= 0.0:
            ts_map.append(DSC_ts[i])
            qs_map.append(100)
        elif diff.max() <= 0.0:
            ts_map.append(DSC_ts[i])
            qs_map.append(0)

    t_max = [550 for q in qs_map]
    q_max = [0 for q in qs_map]
    gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, label="LCOE")

    ax.plot(qs_even, LCOE_even, "ro", label="Break-even")

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")
    ax.legend()

    tikzplotlib.save("Plots/DSC_vs_ORC_LCOE.tex")

if __name__ == "__main__":
    DSC_LCOE, DSC_ts, DSC_qs = get_DSC_results("LCOE")
    ORC_LCOE_best, ORC_LCOE, ORC_ts, ORC_qs = get_ORC_results("LCOE")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    ORC_LCOE_best.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_LCOE_best):
        ax.plot(ORC_qs, t, color=colors[0][i])

    DSC_LCOE.reverse()
    DSC_ts.reverse()
    for i, t in enumerate(DSC_LCOE):
        ax.plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    ts_map = []
    qs_map = []
    LCOE_even = []
    for i, W in enumerate(DSC_LCOE):

        W_DSC = np.array(W)
        W_ORC = np.array(ORC_LCOE_best[i])
        qs = np.array(DSC_qs)

        diff = W_DSC - W_ORC

        if diff.min() < 0.0 < diff.max():

            tar_i = 0
            while diff[tar_i+1] > 0.0:
                tar_i += 1

            m_a = (W_DSC[tar_i+1] - W_DSC[tar_i]) / (qs[tar_i+1] - qs[tar_i])
            c_a = W_DSC[tar_i] - qs[tar_i]*m_a

            m_b = (W_ORC[tar_i+1] - W_ORC[tar_i]) / (qs[tar_i+1] - qs[tar_i])
            c_b = W_ORC[tar_i] - qs[tar_i]*m_b

            break_q = (c_a - c_b) / (m_b - m_a)
            break_W = m_a * break_q + c_a

            qs_even.append(break_q)
            LCOE_even.append(break_W)

            ts_map.append(DSC_ts[i])
            qs_map.append(break_q)
        elif diff.min() >= 0.0:
            ts_map.append(DSC_ts[i])
            qs_map.append(100)
        elif diff.max() <= 0.0:
            ts_map.append(DSC_ts[i])
            qs_map.append(0)

    t_max = [550 for q in qs_map]
    q_max = [0 for q in qs_map]
    gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, label="LCOE")

    ax.plot(qs_even, LCOE_even, "ro", label="Break-even")

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("LCOE/\\unit{\\USD\\of{2023}\\per\\MWh}")
    ax.legend()

    tikzplotlib.save("Plots/DSC_vs_ORC_LCOE.tex")

gax.set_xlabel("Geofluid Inlet Steam Quality/\\unit{\\percent}")
gax.set_ylabel("Geofluid Inlet Temperature/\\unit{\\K}")
gax.set_xlim(0, 100)
gax.set_ylim(423, 548)
gax.legend()

tikzplotlib.save("Plots/DSC_vs_ORC_breakeven_map.tex", figure=gfig)


plt.show()
