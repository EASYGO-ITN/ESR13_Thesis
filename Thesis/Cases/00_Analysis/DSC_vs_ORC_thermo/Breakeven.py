import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

def get_DSC_results():
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

    Wnet = [[np.NAN + 0 for q in qs] for t in ts]
    SpecCost = [[np.NAN + 0 for q in qs] for t in ts]

    for result in results:
        if result:
            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])

            Wnet[t_id][q_id] = -result["NetPow_elec"] * 1e-6
            SpecCost[t_id][q_id] = result["SpecificCost"]

    qs = [q * 100 for q in qs]

    return Wnet, SpecCost, ts, qs

def get_ORC_results():
    with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
        results = json.load(file)

    with open("../../00_SimpleORC_additional_fluids/sensitivity_results.json", "r") as file:
        results += json.load(file)

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


    Wnet = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    SpecCost = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Wnet_best = [[-1e15 + 0 for q in qs] for t in ts]
    Wnet_best_best = [[np.NAN + 0 for q in qs] for t in ts]
    SpecCost_best = [[np.NAN + 0 for q in qs] for t in ts]
    SpecCost_best_best = [[1e15 + 0 for q in qs] for t in ts]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])
            f_id = fluids.index(result["Working fluid comp"])

            power = -result["NetPow_elec"] * 1e-6
            spec_cost = result["SpecificCost"]

            Wnet[f_id][t_id][q_id] = power
            SpecCost[f_id][t_id][q_id] = spec_cost

            if power > Wnet_best[t_id][q_id]:
                Wnet_best[t_id][q_id] = power
                SpecCost_best[t_id][q_id] = spec_cost

            if spec_cost < SpecCost_best_best[t_id][q_id]:
                SpecCost_best_best[t_id][q_id] = spec_cost
                Wnet_best_best[t_id][q_id] = power


    qs = [q * 100 for q in qs]

    return Wnet_best, Wnet_best_best, SpecCost_best, SpecCost_best_best, Wnet, SpecCost, ts, qs, fluids

DSC_Wnet, DSC_SpecCost, DSC_ts, DSC_qs = get_DSC_results()
ORC_Wnet_best, ORC_Wnet_best_best, ORC_SpecCost_best, ORC_SpecCost_best_best, ORC_Wnet, ORC_SpecCost, ORC_ts, ORC_qs, ORC_fluids = get_ORC_results()

colors = [plt.cm.Blues([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Oranges([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          plt.cm.Greys([0.25, 0.375, 0.45, 0.65, 0.85, 1]),
          ]

gfig, gax = plt.subplots()  # the combined plot
gax.plot([0, 1], [-1, -1], "k", label="max \\(W_{elec}^{net}\\)")
gax.plot([0, 1], [-1, -1], "k--", label="min \\(\\frac{C_{plant}}{W_{elec}^{net}}\\)")

big, bx = plt.subplots()  # the Wnet plot
cig, cx = plt.subplots()  # the SpecCost

# best power and corresponding spec cost
if __name__ == "__main__":
    fig, ax = plt.subplots(2)

    ax[0].plot([0, 1], [-1, -1], label="Binary ORC", color=colors[0][2])
    ax[0].plot([0, 1], [-1, -1], label="Single flash DSC", color=colors[1][3])

    for i, t in enumerate(ORC_ts):
        ax[0].plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_best):
        ax[0].plot(ORC_qs, t, color=colors[0][i])

    for i, t in enumerate(DSC_Wnet):
        ax[0].plot(DSC_qs, t, color=colors[1][i])

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
    # gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    w = gax.plot(qs_map, ts_map, label="Net Power")
    bx.plot(qs_map, ts_map, label="Net Power Parity")

    ax[0].plot(qs_even, Wnet_even, "ro", label="Break-even")

    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax[0].set_ylim(0, 30)
    ax[0].legend()

    # spec costs
    for i, t in enumerate(ORC_SpecCost_best):
        ax[1].plot(ORC_qs, t, color=colors[0][i])

    for i, t in enumerate(DSC_SpecCost):
        ax[1].plot(DSC_qs, t, color=colors[1][i])

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
    # gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    s = gax.plot(qs_map, ts_map, label="Specific Cost")
    bx.plot(qs_map, ts_map, label="Specific Cost Parity")

    ax[1].plot(qs_even, SpecCost_even, "ro", label="Break-even")

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax[1].set_ylim(0, 6000)
    ax[1].legend()

    tikzplotlib.save("Plots/Wnet_best_SpecCost.tex")

# power (from best specCost)
if __name__ == "__main__":
    fig, ax = plt.subplots(2)

    ax[0].plot([0, 1], [1, 1], label="Binary ORC", color=colors[0][2])
    ax[0].plot([0, 1], [1, 1], label="Single flash DSC", color=colors[1][3])

    for i, t in enumerate(ORC_ts):
        ax[0].plot([0, 1], [1,1], label="\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(t)+"}{\\K}", color=colors[2][i])

    for i, t in enumerate(ORC_Wnet_best_best):
        ax[1].plot(ORC_qs, t, color=colors[0][i])

    for i, t in enumerate(DSC_Wnet):
        ax[1].plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    ts_even = []
    Wnet_even = []

    ts_map =[]
    qs_map=[]
    for i, W in enumerate(DSC_Wnet):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_Wnet_best_best[i])
        qs = np.array(DSC_qs)

        diff = W_DSC-W_ORC
        break_q = np.interp(0, diff, qs)
        break_W = np.interp(break_q, qs, W_DSC)

        qs_even.append(break_q)
        Wnet_even.append(break_W)

        ts_map.append(DSC_ts[i])
        qs_map.append(break_q)

    q_max = [0 for q in qs_map]
    # gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, "--", color=w[0].get_color())
    cx.plot(qs_map, ts_map, label="Net Power Parity")

    ax[1].plot(qs_even, Wnet_even, "ro", label="Break-even")

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("Net electric power/\\unit{\\mega\\watt}")
    ax[1].set_ylim(0, 30)
    # ax[1].legend()

# best spec costs

    for i, t in enumerate(ORC_SpecCost_best_best):
        ax[0].plot(ORC_qs, t, color=colors[0][i])

    for i, t in enumerate(DSC_SpecCost):
        ax[0].plot(DSC_qs, t, color=colors[1][i])

    qs_even = []
    SpecCost_even = []

    ts_map = []
    qs_map = []
    for i, W in enumerate(DSC_SpecCost):
        W_DSC = np.array(W)
        W_ORC = np.array(ORC_SpecCost_best_best[i])
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
    # gax.fill_betweenx(ts_map, qs_map, q_max, alpha=0.3)
    gax.plot(qs_map, ts_map, "--", color=s[0].get_color())
    cx.plot(qs_map, ts_map, label="Specific Cost Parity")

    ax[0].plot(qs_even, SpecCost_even, "ro", label="Break-even")

    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Specific Cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax[0].set_ylim(0, 6000)
    ax[0].legend()

    tikzplotlib.save("Plots/SpecCost_best_Wnet.tex")

gax.set_xlabel("Geofluid Inlet Steam Quality/\\unit{\\percent}")
gax.set_ylabel("Geofluid Inlet Temperature/\\unit{\\K}")
gax.set_xlim(0, 100)
gax.set_ylim(423, 548)
gax.legend()

bx.annotate("Region 3", (90, 500), horizontalalignment="center")
bx.annotate("Region 2", (40, 475), horizontalalignment="center")
bx.annotate("Region 1", xy=(2.5, 450), xytext=(10, 450), arrowprops=dict(
    arrowstyle="-"))

bx.set_xlabel("Geofluid Inlet Steam Quality/\\unit{\\percent}")
bx.set_ylabel("Geofluid Inlet Temperature/\\unit{\\K}")
bx.set_xlim(0, 100)
bx.set_ylim(423, 548)
bx.legend()

cx.annotate("Region 3", (70, (525+450)/2), horizontalalignment="center")
cx.annotate("Region 2", (20, 450), horizontalalignment="center")
cx.annotate("Region 1", (10, 525), horizontalalignment="center")

cx.set_xlabel("Geofluid Inlet Steam Quality/\\unit{\\percent}")
cx.set_ylabel("Geofluid Inlet Temperature/\\unit{\\K}")
cx.set_xlim(0, 100)
cx.set_ylim(423, 548)
cx.legend()


tikzplotlib.save("Plots/Breakeven_map.tex", figure=gfig)
tikzplotlib.save("Plots/Breakeven_Wnet.tex", figure=big)
tikzplotlib.save("Plots/Breakeven_SpecCost.tex", figure=cig)

plt.show()
