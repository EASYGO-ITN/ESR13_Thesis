import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

with open("../../01_SimpleORC_recuperated/sensitivity_results.json", "r") as file:
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

Wnet = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Wnet_best = [[0 for q in qs] for t in ts]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        power = -result["NetPow_elec"] * 1e-6

        Wnet[f_id][t_id][q_id] = power

        if power > Wnet_best[t_id][q_id]:
            Wnet_best[t_id][q_id] = power

qs = [q * 100 for q in qs]

colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Oranges(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
          plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
          plt.cm.Purples(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts)))]

for fluid in fluids:
    fig, ax = plt.subplots()
    ax.set_title("{}".format(fluid[0]))

    f_id = fluids.index(fluid)
    for i, t in enumerate(Wnet[f_id]):
        ax.plot(qs, t, label=ts[i], color=colors[f_id][i])

    ax.set_xlabel("Inlet Steam Quality/%")
    ax.set_ylabel("Net electric power/MW")
    ax.legend()

fig, ax = plt.subplots()
# ax.set_title("Best Working Fluid")

ts.reverse()
Wnet_best.reverse()
colors = plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])
for i, t in enumerate(Wnet_best):
    ax.plot(qs, t, label="\\qty{"+str(ts[i])+"}{\\K}", color=colors[i])

ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
ax.set_ylabel("Net electric power/\\unit{\\mega\watt}")
ax.legend()

tikzplotlib.save("Plots/Best_WF_by_T.tex", figure=fig)

ts.reverse()
Wnet_best.reverse()

# for t_id, t in enumerate(ts):
#     fig, ax = plt.subplots()
#     ax.set_title("T={} K".format(t))
#
#     for f_id, f_res in enumerate(Wnet):
#         ax.plot(qs, f_res[t_id], label=fluids[f_id][0])
#
#     ax.plot(qs, Wnet_best[t_id], "k:", linewidth=3, label="Best WF")
#
#     ax.set_xlabel("Inlet Steam Quality/%")
#     ax.set_ylabel("Net electric power/MW")
#     ax.legend()
#
# plt.show()

fig1, ax1 = plt.subplots(len(ts))
for t_id, t in enumerate(ts):
    ax1[t_id].set_title("T=\\qty{"+str(t)+"}{\\K}")

    for f_id, f_res in enumerate(Wnet):
        ax1[t_id].plot(qs, f_res[t_id], label=fluids[f_id][0])

    ax1[t_id].plot(qs, Wnet_best[t_id], "k:", linewidth=3, label="Best WF")

    ax1[t_id].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax1[t_id].set_ylabel("Net electric power/\\unit{\\mega\watt}")

ax1[-1].legend()

tikzplotlib.save("Plots/WFs_by_T.tex", figure=fig1)

plt.show()
