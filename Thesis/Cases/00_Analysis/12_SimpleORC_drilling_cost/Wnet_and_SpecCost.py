import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib


def get_thermo():
    with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
        results = json.load(file)
    with open("../../00_SimpleORC_additional_fluids/sensitivity_results.json", "r") as file:
        results += json.load(file)

    fluids = [
              ["n-Butane", 1],
              ["Cyclopentane", 1],
            ]

    Wnet = [np.NAN for f in fluids]
    SpecCost = [np.NAN for f in fluids]

    for result in results:
        if result:

            if result["Hot fluid input1"] != 473.15 or result["Hot fluid input2"] != 0.2:
                continue
            else:
                if result["Working fluid comp"] in fluids:
                    f_id = fluids.index(result["Working fluid comp"])
                else:
                    continue

                power = -result["NetPow_elec"] * 1e-6

                Wnet[f_id] = power
                SpecCost[f_id] = result["SpecificCost"]

    return Wnet, SpecCost, fluids


def get_techno():
    with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
        results = json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
        results += json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
        results += json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_d/sensitivity_results.json", "r") as file:
        results += json.load(file)

    fluids = [
        ["n-Butane", 1],
        ["Cyclopentane", 1],
    ]

    Wnet = [np.NAN for f in fluids]
    SpecCost = [np.NAN for f in fluids]

    for result in results:
        if result:

            if result["Hot fluid input1"] != 473.15 or result["Hot fluid input2"] != 0.2:
                continue
            else:
                if result["Working fluid comp"] in fluids:
                    f_id = fluids.index(result["Working fluid comp"])
                else:
                    continue

            power = -result["NetPow_elec"] * 1e-6

            Wnet[f_id] = power
            SpecCost[f_id] = result["SpecificCost"]

    return Wnet, SpecCost, fluids

def get_drilling_thermo():
    with open("../../12_SimpleORC_thermo_specCost_drillingCost/sensitivity_results.json", "r") as file:
        results = json.load(file)

    fluids = [
              ["n-Butane", 1],
              ["Cyclopentane", 1],
            ]

    Wnet = [np.NAN for f in fluids]
    SpecCost = [np.NAN for f in fluids]

    for result in results:
        if result:

            if result["Working fluid comp"] in fluids:
                f_id = fluids.index(result["Working fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6

            Wnet[f_id] = power
            SpecCost[f_id] = result["SpecificCost"]

    return Wnet, SpecCost, fluids


def get_drilling_techno():
    with open("../../12_SimpleORC_techno_specCost_drillingCost_b/sensitivity_results.json", "r") as file:
        results = json.load(file)

    fluids = [
              ["n-Butane", 1],
              ["Cyclopentane", 1],
            ]

    Wnet = [np.NAN for f in fluids]
    SpecCost = [np.NAN for f in fluids]

    for result in results:
        if result:

            if result["Working fluid comp"] in fluids:
                f_id = fluids.index(result["Working fluid comp"])
            else:
                continue

            power = -result["NetPow_elec"] * 1e-6

            Wnet[f_id] = power
            SpecCost[f_id] = result["SpecificCost"]

    return Wnet, SpecCost, fluids


def get_drilling():
    with open("../../12_SimpleORC_techno_specCost_drillingCost/sensitivity_results.json", "r") as file:
        results = json.load(file)

    drilling = []
    for result in results:
        if result:
            drilling.append(result["DrillingCosts"])

    drilling = list(set(drilling))
    drilling.sort()

    fluids = [
        ["n-Butane", 1],
        ["Cyclopentane", 1],
    ]

    Wnet = [[np.NAN + 0 for d in drilling] for f in fluids]
    SpecCost = [[np.NAN + 0 for d in drilling] for f in fluids]
    SpecCost_ex = [[np.NAN + 0 for d in drilling] for f in fluids]

    for result in results:
        if result:
            d_id = drilling.index(result["DrillingCosts"])
            f_id = fluids.index(result["Working fluid comp"])

            power = -result["NetPow_elec"] * 1e-6

            Wnet[f_id][d_id] = power
            SpecCost[f_id][d_id] = result["SpecificCost"]
            SpecCost_ex[f_id][d_id] = result["SpecificCost_exDrilling"]

    return Wnet, SpecCost, SpecCost_ex, drilling, fluids



# get the data
Wnet_thermo, SpecCost_thermo, fluids_thermo = get_thermo()
Wnet_techno, SpecCost_techno, fluids_techno = get_techno()
Wnet_drilling_thermo, SpecCost_drilling_thermo, fluids_drilling_thermo = get_drilling_thermo()
Wnet_drilling_techno, SpecCost_drilling_techno, fluids_drilling_techno = get_drilling_techno()
Wnet_drilling, SpecCost_drilling, SpecCost_ex_drilling, drilling, fluids_drilling = get_drilling()

colors = [plt.cm.Oranges(np.linspace(0.3, 1, 3)),
          plt.cm.Blues(np.linspace(0.3, 1, 3))]

# plot the net power
if __name__ == "__main__":
    fig, ax = plt.subplots(2)
    for i, fluid in enumerate(fluids_thermo):

        ax[i].set_title(fluid[0])

        f_id = fluids_thermo.index(fluid)
        w = [Wnet_thermo[f_id] for d in drilling]
        ax[i].plot(drilling, w, label="Thermodynamic Opt.", color=colors[i][0])

        f_id = fluids_techno.index(fluid)
        w = [Wnet_techno[f_id] for d in drilling]
        ax[i].plot(drilling, w, label="Techno-economic Opt. (excluding drilling costs)", color=colors[i][2])

        f_id = fluids_drilling.index(fluid)
        ax[i].plot(drilling, Wnet_drilling[f_id], label="Techno-economic Opt. (including drilling costs)", color=colors[i][1])

        # f_id = fluids_drilling_thermo.index(fluid)
        # w = [Wnet_drilling_thermo[f_id] for d in drilling]
        # ax[i].plot(drilling, w, "--", label="drilling_thermo", color=colors[i][2])

        # f_id = fluids_drilling_techno.index(fluid)
        # w = [Wnet_drilling_techno[f_id] for d in drilling]
        # ax[i].plot(drilling, w, ":", label="drilling_techno", color=colors[i][2])


        ax[i].set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax[i].set_ylabel("Net electrical power/\\unit{\\mega\\watt}")
        ax[i].set_ylim(0, 9)
        ax[i].set_xlim(0, None)
        ax[i].legend()

    tikzplotlib.save("Wnet.tex")

# plot the spec cost
if __name__ == "__main__":
    fig, ax = plt.subplots(2)
    for i, fluid in enumerate(fluids_thermo):

        ax[i].set_title(fluid[0])
        ax[i].plot([0,0],[-1,-1], label="Obj.Func")

        f_id = fluids_thermo.index(fluid)
        w = [SpecCost_thermo[f_id] for d in drilling]
        ax[i].plot(drilling, w, label="Thermodynamic Opt.", color=colors[i][0])

        f_id = fluids_techno.index(fluid)
        w = [SpecCost_techno[f_id] for d in drilling]
        ax[i].plot(drilling, w, label="Techno-economic Opt. (excluding drilling costs)", color=colors[i][2])

        f_id = fluids_drilling.index(fluid)
        # ax[i].plot(drilling, SpecCost_drilling[f_id], label="drilling", color=colors[i][2])
        ax[i].plot(drilling, SpecCost_ex_drilling[f_id], label="Techno-economic Opt. (including drilling costs)", color=colors[i][1])

        # f_id = fluids_drilling_thermo.index(fluid)
        # w = [SpecCost_drilling_thermo[f_id] for d in drilling]
        # ax[i].plot(drilling, w,"--", label="drilling_thermo", color=colors[i][2])
        #
        # f_id = fluids_drilling_techno.index(fluid)
        # w = [SpecCost_drilling_techno[f_id] for d in drilling]
        # ax[i].plot(drilling, w,":", label="drilling_techno", color=colors[i][2])


        ax[i].set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
        ax[i].set_ylabel("Specific plant cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
        ax[i].set_ylim(0, 4000)
        ax[i].set_xlim(0, None)
        ax[i].legend()

    tikzplotlib.save("SecCost.tex")

# plot nButane
if __name__ == "__main__":
    fig, ax = plt.subplots(2)

    f_id = fluids_thermo.index(["n-Butane", 1])
    w = [SpecCost_thermo[f_id] for d in drilling]
    ax[0].plot(drilling, w, label="Thermodynamic Opt.")

    v = [Wnet_thermo[f_id] for d in drilling]
    ax[1].plot(drilling, v, label="Thermodynamic Opt.")

    f_id = fluids_techno.index(["n-Butane", 1])
    w = [SpecCost_techno[f_id] for d in drilling]
    ax[0].plot(drilling, w, label="Techno-economic Opt. (excluding drilling costs)")

    v = [Wnet_techno[f_id] for d in drilling]
    ax[1].plot(drilling, v, label="Techno-economic Opt. (excluding drilling costs)")


    f_id = fluids_drilling.index(["n-Butane", 1])
    # ax[i].plot(drilling, SpecCost_drilling[f_id], label="drilling", color=colors[i][2])
    ax[0].plot(drilling, SpecCost_ex_drilling[f_id], label="Techno-economic Opt. (including drilling costs)")
    ax[i].plot(drilling, Wnet_drilling[f_id], label="Techno-economic Opt. (including drilling costs)")

    ax[0].set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].set_ylabel("Specific plant cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax[0].set_ylim(1500, 3000)
    ax[0].set_xlim(0, 60)
    ax[0].legend()

    ax[1].set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[1].set_ylabel("Net electrical power/\\unit{\\mega\\watt}")
    ax[1].set_ylim(0, 9)
    ax[1].set_xlim(0, 60)
    # ax[1].legend()

    tikzplotlib.save("Drilling_nButane.tex")

# plot Cyclopentane
if __name__ == "__main__":
    fig, ax = plt.subplots(2)

    f_id = fluids_thermo.index(["Cyclopentane", 1])
    w = [SpecCost_thermo[f_id] for d in drilling]
    ax[0].plot(drilling, w, label="Thermodynamic Opt.")

    v = [Wnet_thermo[f_id] for d in drilling]
    ax[1].plot(drilling, v, label="Thermodynamic Opt.")

    f_id = fluids_techno.index(["Cyclopentane", 1])
    w = [SpecCost_techno[f_id] for d in drilling]
    ax[0].plot(drilling, w, label="Techno-economic Opt. (excluding drilling costs)")

    v = [Wnet_techno[f_id] for d in drilling]
    ax[1].plot(drilling, v, label="Techno-economic Opt. (excluding drilling costs)")


    f_id = fluids_drilling.index(["Cyclopentane", 1])
    # ax[i].plot(drilling, SpecCost_drilling[f_id], label="drilling", color=colors[i][2])
    ax[0].plot(drilling, SpecCost_ex_drilling[f_id], label="Techno-economic Opt. (including drilling costs)")
    ax[i].plot(drilling, Wnet_drilling[f_id], label="Techno-economic Opt. (including drilling costs)")

    ax[0].set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[0].set_ylabel("Specific plant cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax[0].set_ylim(1500, 3000)
    ax[0].set_xlim(0, 60)
    ax[0].legend()

    ax[1].set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax[1].set_ylabel("Net electrical power/\\unit{\\mega\\watt}")
    ax[1].set_ylim(0, 9)
    ax[1].set_xlim(0, 60)
    # ax[1].legend()

    tikzplotlib.save("Drilling_Cyclopentane.tex")

# plot CostContrib
if __name__ == "__main__":
    fig, ax = plt.subplots()

    f_id = fluids_thermo.index(["n-Butane", 1])
    w = [100 - 100*d/(SpecCost_thermo[f_id]*Wnet_thermo[f_id]*1e-3 +d) for d in drilling]
    ax.plot(drilling, w, label="Thermodynamic Opt.")

    f_id = fluids_techno.index(["n-Butane", 1])
    w = [100 - 100*d/(SpecCost_techno[f_id]*Wnet_techno[f_id]*1e-3 +d) for d in drilling]
    ax.plot(drilling, w, label="Techno-economic Opt. (excluding drilling costs)")

    w = 100 - 100.0 * np.array(drilling) /(np.array(SpecCost_ex_drilling[f_id]) * np.array(Wnet_drilling[f_id]) * 1e-3 + np.array(drilling))
    ax.plot(drilling, w, label="Techno-economic Opt. (including drilling costs)")

    ax.set_xlabel("Drilling Cost/\\unit{\\mega\\USD\\of{2023}}")
    ax.set_ylabel("Specific plant cost/\\unit{\\USD\\of{2023}\\kilo\\watt}")
    ax.set_ylim(0, 100)
    ax.set_xlim(0, 60)
    ax.legend()

    tikzplotlib.save("Drilling_nButane.tex")

plt.show()



