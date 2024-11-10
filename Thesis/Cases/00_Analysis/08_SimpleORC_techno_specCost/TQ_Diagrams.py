import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI

# with open("../00_SimpleORC/sensitivity_results.json", "r") as file:
#     results = json.load(file)
with open("../../08_SimpleORC_techno_specCost/sensitivity_results.json", "r") as file:
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

        res = {val:result[val] for val in vals}

        TQs[f_id][t_id][q_id] = res

qs = [q * 100 for q in qs]


# colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
#           plt.cm.Oranges(np.linspace(0.3, 1, len(ts))),
#           plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
#           plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
#           plt.cm.Purples(np.linspace(0.3, 1, len(ts))),
#           plt.cm.Greys(np.linspace(0.3, 1, len(ts)))]


# plot the maximum pressure
fig, ax = plt.subplots()

# TQ = TQs[0][1][0]
#
# TQs_ = TQs[1][0]

for TQ in TQs[0][0]:

    # TQ = TQ_[0]

    if type(TQ) is not float:
        ax.plot(TQ["Q_coolant"], TQ["T_coolant"], "b")
        ax.plot(TQ["Q_geofluid"], TQ["T_geofluid"], "r")
        ax.plot(TQ["Q_wf_heating"], TQ["T_wf_heating"], "g")
        ax.plot(TQ["Q_wf_cooling"], TQ["T_wf_cooling"], "g")

# tikzplotlib.save("Plots/SimpleORC_Pmax.tex", figure=fig)

plt.show()
