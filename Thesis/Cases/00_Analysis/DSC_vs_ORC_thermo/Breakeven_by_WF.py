import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

def get_DSC_results(res_str, conv=1.0):
    with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
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


def get_DSC_results_b(res_str, conv=1.0):
    with open("../../06_DSC_single_flash_additional_temperatures/sensitivity_results.json", "r") as file:
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


def get_ORC_results(res_str, conv=1.0, min_val=True):
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

    return res_best, res, ts, qs, fluids


def get_ORC_results_b(res_str, conv=1.0, min_val=True):
    with open("../../00_SimpleORC_additional_temperatures/sensitivity_results.json", "r") as file:
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

    return res_best, res, ts, qs, fluids


# DSC vs Butane ORC
if __name__ == "__main_":

    DSC_Wnet, DSC_ts, DSC_qs = get_DSC_results("NetPow_elec", conv=-1e-6)
    ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("NetPow_elec", conv=-1e-6, min_val=False)

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    f_id = ORC_fluids.index(["n-Butane", 1])
    ORC_Wnet_butane = ORC_Wnet[f_id]
    ORC_Wnet_butane.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_butane):
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
        W_ORC = np.array(ORC_Wnet_butane[i])
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

    DSC_Wnet, DSC_ts, DSC_qs = get_DSC_results("SpecificCost")
    ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("SpecificCost")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    ax.plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax.plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    f_id = ORC_fluids.index(["n-Butane", 1])
    ORC_Wnet_butane = ORC_Wnet[f_id]
    ORC_Wnet_butane.reverse()
    ORC_ts.reverse()
    for i, t in enumerate(ORC_ts):
        ax.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_butane):
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
        W_ORC = np.array(ORC_Wnet_butane[i])
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

    # tikzplotlib.save("Plots/DSC_vs_ORC_Wnet.tex")

# DSC vs Butane ORC
if __name__ == "__main__":

    DSC_Wnet, DSC_ts, DSC_qs = get_DSC_results("NetPow_elec", conv=-1e-6)
    ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("NetPow_elec", conv=-1e-6, min_val=False)

    DSC_specCost, DSC_ts, DSC_qs = get_DSC_results("SpecificCost")
    ORC_SpecCost_best, ORC_SpecCost, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("SpecificCost")

    f_id = ORC_fluids.index(["n-Butane", 1])
    t_id = ORC_ts.index(473.15)
    ORC_Wnet_butane = ORC_Wnet[f_id][t_id]
    ORC_SpecCost_butane = ORC_SpecCost[f_id][t_id]

    fig, ax = plt.subplots(2)
    ax[0].plot(ORC_qs, ORC_Wnet_butane, label="Binary ORC")
    ax[0].plot(DSC_qs, DSC_Wnet[t_id], label="Single Flash DSC")
    ax[0].plot([25,25], [0, 30], "k:")
    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Net electrical power/\\unit{\\mega\\watt}")
    ax[0].set_ylim(0, 25)
    ax[0].legend()

    ax[1].plot(ORC_qs, ORC_SpecCost_butane, label="Binary ORC")
    ax[1].plot(DSC_qs, DSC_specCost[t_id], label="Single Flash DSC")
    ax[1].plot([25,25], [0, 4000], "k:")
    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\per\\kilo\\watt}")
    ax[1].set_ylim(0, 4000)
    ax[1].legend()

    tikzplotlib.save("Plots/nButane.tex")

# Breakeven for all ORC fluids by Wnet
if __name__ == "__main__":

    DSC_Wnet, DSC_ts, DSC_qs = get_DSC_results("NetPow_elec", conv=-1e-6)
    ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("NetPow_elec", conv=-1e-6, min_val=False)

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    # ax.plot([0, 1], [-1, -1], label="Binary ORC", color=colors[0][2])
    # ax.plot([0, 1], [-1, -1], label="Single flash DSC", color=colors[1][3])

    ORC_ts.reverse()
    DSC_ts.reverse()
    DSC_Wnet.reverse()
    for f_id, fluid in enumerate(ORC_fluids):
        ORC_Wnet_fluid = ORC_Wnet[f_id]

        ORC_Wnet_fluid.reverse()

        # big, bx = plt.subplots()
        # for i, t in enumerate(ORC_ts):
        #     bx.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])
        #
        # for i, t in enumerate(ORC_Wnet_fluid):
        #     bx.plot(ORC_qs, t, color=colors[0][i])
        #
        # for i, t in enumerate(DSC_Wnet):
        #     bx.plot(DSC_qs, t, color=colors[1][i])

        qs_even = []
        ts_even = []
        Wnet_even = []

        ts_map =[]
        qs_map=[]
        for i, W in enumerate(DSC_Wnet):
            W_DSC = np.array(W)
            W_ORC = np.array(ORC_Wnet_fluid[i])

            qs = np.flip(np.array(DSC_qs))
            diff = np.flip(W_DSC-W_ORC)
            if diff.min() < 0:
                for j, d in enumerate(diff):
                    if j == 0:
                        if d < 0:
                            qs_even.append(100)
                            qs_map.append(100)
                            ts_map.append(DSC_ts[i])
                        else:
                            continue

                    if d <= 0 <= diff[j-1]:
                        m = (d-diff[j-1]) / (qs[j] - qs[j-1])
                        c = d - m * qs[j]
                        q = -c / m

                        qs_even.append(q)
                        qs_map.append(q)
                        ts_map.append(DSC_ts[i])
                        Wnet_even.append(np.interp(q, ORC_qs, W_ORC))

                        continue

        #     # break_q = np.interp(0, diff, qs)
        #     # break_W = np.interp(break_q, qs, W_DSC)
        #     #
        #     # qs_even.append(break_q)
        #     # Wnet_even.append(break_W)
        #     #
        #     # ts_map.append(DSC_ts[i])
        #     # qs_map.append(break_q)
        #
        # # q_max = [0 for q in qs_map]
        # # gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
        # # gax.plot(qs_map, ts_map, label="Net Power")
        #
        # bx.plot(qs_even, Wnet_even, "ro", label=fluid[0])
        ax.plot(qs_even, ts_map, label=fluid[0])

        # bx.legend()

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Inlet Temperature/\\unit{\\K}")
    ax.set_xlim(0, 100)
    ax.set_ylim(423, 548)
    ax.legend()

    tikzplotlib.save("Plots/Breakeven_Fluid_Wnet.tex")

# Breakeven for all ORC fluids by Specific Cost
if __name__ == "__main__":

    DSC_Wnet, DSC_ts, DSC_qs = get_DSC_results("SpecificCost")
    ORC_Wnet_best, ORC_Wnet, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results("SpecificCost")

    fig, ax = plt.subplots()
    colors = [plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              ]

    # ax.plot([0, 1], [-1, -1], label="Binary ORC", color=colors[0][2])
    # ax.plot([0, 1], [-1, -1], label="Single flash DSC", color=colors[1][3])

    ORC_ts.reverse()
    DSC_ts.reverse()
    DSC_Wnet.reverse()
    for f_id, fluid in enumerate(ORC_fluids):
        ORC_Wnet_fluid = ORC_Wnet[f_id]

        ORC_Wnet_fluid.reverse()

        # big, bx = plt.subplots()
        # for i, t in enumerate(ORC_ts):
        #     bx.plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])
        #
        # for i, t in enumerate(ORC_Wnet_fluid):
        #     bx.plot(ORC_qs, t, color=colors[0][i])
        #
        # for i, t in enumerate(DSC_Wnet):
        #     bx.plot(DSC_qs, t, color=colors[1][i])

        qs_even = []
        ts_even = []
        Wnet_even = []

        ts_map =[]
        qs_map=[]
        for i, W in enumerate(DSC_Wnet):
            W_DSC = np.array(W)
            W_ORC = np.array(ORC_Wnet_fluid[i])

            qs = np.array(DSC_qs)
            diff = W_DSC-W_ORC
            if diff.min() < 0:
                for j, d in enumerate(diff):
                    if j == 0:
                        if d < 0:
                            qs_even.append(0)
                            qs_map.append(0)
                            ts_map.append(DSC_ts[i])
                        else:
                            continue

                    if d <= 0 <= diff[j-1]:
                        m = (d-diff[j-1]) / (qs[j] - qs[j-1])
                        c = d - m * qs[j]
                        q = -c / m

                        qs_even.append(q)
                        qs_map.append(q)
                        ts_map.append(DSC_ts[i])
                        Wnet_even.append(np.interp(q, ORC_qs, W_ORC))

                        continue

        #     # break_q = np.interp(0, diff, qs)
        #     # break_W = np.interp(break_q, qs, W_DSC)
        #     #
        #     # qs_even.append(break_q)
        #     # Wnet_even.append(break_W)
        #     #
        #     # ts_map.append(DSC_ts[i])
        #     # qs_map.append(break_q)
        #
        # # q_max = [0 for q in qs_map]
        # # gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
        # # gax.plot(qs_map, ts_map, label="Net Power")
        #
        # bx.plot(qs_even, Wnet_even, "ro", label=fluid[0])
        ax.plot(qs_even, ts_map, label=fluid[0])

        # bx.legend()

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Inlet Temperature/\\unit{\\K}")
    ax.set_xlim(0, 100)
    ax.set_ylim(423, 548)
    ax.legend()

    tikzplotlib.save("Plots/Breakeven_Fluid_SpecCost.tex")

plt.show()
