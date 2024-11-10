import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI

with open("../../00_SimpleORC_high_def/sensitivity_results.json", "r") as file:
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

TQs = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

vals = ["T_coolant", "Q_coolant", "T_wf_heating", "Q_wf_heating", "T_wf_cooling", "Q_wf_cooling", "T_geofluid", "Q_geofluid"]

for result in results:
    if result:

        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])
        f_id = fluids.index(result["Working fluid comp"])

        res = {}
        for val in vals:

            if val[0] == "Q":
                res[val] = [r*1e-6 for r in result[val]]
            else:
                res[val] = result[val]

        TQs[f_id][t_id][q_id] = res

qs = [q * 100 for q in qs]

fig, ax = plt.subplots(nrows=4)

f_id = 2
TQ = TQs[f_id][0][0]
if type(TQ) is not float:
    ax[0].plot(TQ["Q_coolant"], TQ["T_coolant"], "b")
    ax[0].plot(TQ["Q_geofluid"], TQ["T_geofluid"], "r")
    ax[0].plot(TQ["Q_wf_heating"], TQ["T_wf_heating"], "g")
    ax[0].plot(TQ["Q_wf_cooling"], TQ["T_wf_cooling"], "g")
    ax[0].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[0])+"}{\\K}")

TQ = TQs[f_id][1][0]
if type(TQ) is not float:
    ax[1].plot(TQ["Q_coolant"], TQ["T_coolant"], "b")
    ax[1].plot(TQ["Q_geofluid"], TQ["T_geofluid"], "r")
    ax[1].plot(TQ["Q_wf_heating"], TQ["T_wf_heating"], "g")
    ax[1].plot(TQ["Q_wf_cooling"], TQ["T_wf_cooling"], "g")
    ax[1].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[1])+"}{\\K}")

TQ = TQs[f_id][2][0]
if type(TQ) is not float:
    ax[2].plot(TQ["Q_coolant"], TQ["T_coolant"], "b")
    ax[2].plot(TQ["Q_geofluid"], TQ["T_geofluid"], "r")
    ax[2].plot(TQ["Q_wf_heating"], TQ["T_wf_heating"], "g")
    ax[2].plot(TQ["Q_wf_cooling"], TQ["T_wf_cooling"], "g")
    ax[2].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[2])+"}{\\K}")

TQ = TQs[f_id][4][0]
if type(TQ) is not float:
    ax[3].plot(TQ["Q_geofluid"], TQ["T_geofluid"], "r", label="Geofluid")
    ax[3].plot(TQ["Q_wf_heating"], TQ["T_wf_heating"], "g", label="Working Fluid")
    ax[3].plot(TQ["Q_coolant"], TQ["T_coolant"], "b", label="Coolant")
    ax[3].plot(TQ["Q_wf_cooling"], TQ["T_wf_cooling"], "g")
    ax[3].set_title("\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[4])+"}{\\K}")
    ax[3].legend()

xlims = ax[3].get_xlim()
ax[0].set_xlim(xlims)
ax[1].set_xlim(xlims)
ax[2].set_xlim(xlims)

ylims = ax[3].get_ylim()
ax[0].set_ylim(ylims)
ax[1].set_ylim(ylims)
ax[2].set_ylim(ylims)


ax[0].set_xlabel("Heat Transferred/\\unit{\\mega\\watt}")
ax[1].set_xlabel("Heat Transferred/\\unit{\\mega\\watt}")
ax[2].set_xlabel("Heat Transferred/\\unit{\\mega\\watt}")
ax[3].set_xlabel("Heat Transferred/\\unit{\\mega\\watt}")

ax[0].set_ylabel("Temperature/\\unit{\\K}")
ax[1].set_ylabel("Temperature/\\unit{\\K}")
ax[2].set_ylabel("Temperature/\\unit{\\K}")
ax[3].set_ylabel("Temperature/\\unit{\\K}")

tikzplotlib.save("Plots/SimpleORC_highdef_TQ_by_T.tex", figure=fig)

plt.show()
