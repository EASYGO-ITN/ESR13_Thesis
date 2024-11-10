import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

import os.path

print(os.path.abspath("../../"))

def get_techno():

    with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
        results = json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
        results += json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
        results += json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_d/sensitivity_results.json", "r") as file:
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

    fluids = [["n-Propane", 1],
              ["Cyclopropane", 1],
              ["IsoButane", 1],
              ["n-Butane", 1],
              ["Isopentane", 1],
              ["Isohexane", 1],
              ["Cyclopentane", 1],
              ["n-Heptane", 1]]

    stages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Vstages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Hstages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    SP = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])
            f_id = fluids.index(result["Working fluid comp"])

            stages[f_id][t_id][q_id] = result["Turbine_Stages"]
            Hstages[f_id][t_id][q_id] = result["Turbine_HStages"]
            Vstages[f_id][t_id][q_id] = result["Turbine_VStages"]
            SP[f_id][t_id][q_id] = result["Turbine_SP"]

    qs = [q * 100 for q in qs]

    return stages, Hstages, Vstages, SP, ts, qs, fluids


def get_thermo():
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
    qs = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]

    fluids = [["n-Propane", 1],
              ["CycloPropane", 1],
              ["IsoButane", 1],
              ["n-Butane", 1],
              ["Isopentane", 1],
              ["Isohexane", 1],
              ["Cyclopentane", 1],
              ["n-Heptane", 1]]

    stages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Vstages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Hstages = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    SP = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

    for result in results:
        if result:
            t_id = ts.index(result["Hot fluid input1"])
            if result["Hot fluid input2"] in qs:
                q_id = qs.index(result["Hot fluid input2"])
            else:
                continue
            f_id = fluids.index(result["Working fluid comp"])

            stages[f_id][t_id][q_id] = result["Turbine_Stages"]
            Hstages[f_id][t_id][q_id] = result["Turbine_HStages"]
            Vstages[f_id][t_id][q_id] = result["Turbine_VStages"]
            SP[f_id][t_id][q_id] = result["Turbine_SP"]

    qs = [q * 100 for q in qs]

    return stages, Hstages, Vstages, SP, ts, qs, fluids

techno_stages, techno_Hstages, techno_Vstages, techno_SP, techno_ts, techno_qs, techno_fluids = get_techno()
thermo_stages, thermo_Hstages, thermo_Vstages, thermo_SP, thermo_ts, thermo_qs, thermo_fluids = get_thermo()

## plotting the number of stages and SP for all fluids
if __name__ == "__main_":

    fig, ax = plt.subplots(2)
    t_id = thermo_ts.index(548.15)
    for f_id, f_res in enumerate(techno_stages):
        p = ax[0].plot(techno_qs, techno_stages[f_id][t_id], label=techno_fluids[f_id][0])
        q = ax[1].plot(techno_qs, techno_SP[f_id][t_id], label=techno_fluids[f_id][0])

        if techno_fluids[f_id] == ['Cyclopropane', 1]:
            f_id_ = thermo_fluids.index(['CycloPropane', 1])
        else:
            f_id_ = thermo_fluids.index(techno_fluids[f_id])
        ax[0].plot(thermo_qs, thermo_stages[f_id_][t_id], "--", color=p[0].get_color())
        ax[1].plot(thermo_qs, thermo_SP[f_id_][t_id], "--", color=q[0].get_color())

    ax[0].set_xlabel("Inlet Steam Quality/%")
    ax[0].set_ylabel("Turbine Stages")
    ax[0].set_ylim(0, 6)

    ax[1].set_xlabel("Inlet Steam Quality/%")
    ax[1].set_ylabel("Size Parameter")
    ax[1].set_yscale("log")

    ax[1].legend()

    # tikzplotlib.save("Plots/TurbineStages.tex", figure=fig)

# plotting the number of stages and the SP, as well as their deltas
if __name__ == "__main__":
    aig, ax = plt.subplots(2)
    big, bx = plt.subplots(2)

    t_id = thermo_ts.index(548.15)
    for f_id, f_res in enumerate(techno_stages):
        p = ax[0].plot(techno_qs, techno_stages[f_id][t_id], label=techno_fluids[f_id][0])

        q = bx[0].plot(techno_qs, techno_SP[f_id][t_id], label=techno_fluids[f_id][0])

        if techno_fluids[f_id] == ['Cyclopropane', 1]:
            f_id_ = thermo_fluids.index(['CycloPropane', 1])
        else:
            f_id_ = thermo_fluids.index(techno_fluids[f_id])

        diff_stages = np.array(techno_stages[f_id][t_id]) - np.array(thermo_stages[f_id_][t_id])
        diff_SP = np.array(techno_SP[f_id][t_id]) - np.array(thermo_SP[f_id_][t_id])
        ax[1].plot(techno_qs, diff_stages, color=p[0].get_color())
        bx[1].plot(techno_qs, diff_SP, color=q[0].get_color())
        # twin_SP.plot(techno_qs, 100*diff_SP / np.array(thermo_SP[f_id_][t_id]), color=q[0].get_color())

    ax[0].set_xlabel("Inlet Steam Quality/%")
    ax[0].set_ylabel("Turbine Stages")
    ax[0].set_ylim(0, 4)
    ax[0].legend()

    ax[1].set_xlabel("Inlet Steam Quality/%")
    ax[1].set_ylabel("Delta Turbine Stages")
    ax[1].set_ylim(-4, 0)

    bx[0].set_xlabel("Inlet Steam Quality/%")
    bx[0].set_ylabel("Size Parameter/\\unit{\\m}")
    bx[0].legend()

    bx[1].set_xlabel("Inlet Steam Quality/%")
    bx[1].set_ylabel("Delta Size Parameter/\\unit{\\m}")


    tikzplotlib.save("Plots/DTurbineStages.tex", figure=aig)
    tikzplotlib.save("Plots/DSP.tex", figure=big)

plt.show()
