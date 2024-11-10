import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib
import numpy as np
import json
from CoolProp.CoolProp import PropsSI


from Thesis.PowerPlants.simple_binary_superheater import ORC as simpleORC
from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream

Tin = 200 + 273.15
Qin = 0.2
Tmin = 308


def calc_cycle(Pr, DT):
    Cycle = simpleORC(recu=False)
    Cycle.deltaT_superheat = 2
    Cycle.condenser.deltaP_cold = 120
    Cycle.coolingpump.eta_isentropic = 0.6

    hot_fluid = Fluid(["water", 1])
    hot_fluid_stream = MaterialStream(hot_fluid, m=50)
    hot_fluid_stream.update("TQ", Tin, Qin)

    Cycle.set_geofluid(hot_fluid_stream)

    cold_fluid = Fluid(["air", 1])
    cold_fluid_stream = MaterialStream(cold_fluid, m=1)
    Cycle.set_coolant(cold_fluid_stream)

    workingfluid = Fluid(["Isopentane", 1])
    workingfluid_stream = MaterialStream(workingfluid, m=1)
    Cycle.set_workingfluid(workingfluid_stream)

    P_crit = workingfluid.state.state.state.p_critical()
    Pmax = P_crit * Pr

    workingfluid.update("PQ", Pmax, 0.5)
    Tsat = workingfluid.properties.T
    Tmax = Tsat + DT

    Cycle.calc(Pmax, Tmax, Tmin)

    return Cycle.net_power_elec

# insert code to plot the determined maximum
with open("../../00_SimpleORC_ConvergencePlot/sensitivity_results.json", "r") as file:
    results = json.load(file)

for result in results:

    Wnet_Power_Cycle = result["NetPow_elec"]

    Pcrit = PropsSI("Pcrit", "Isopentane")
    Pr = [result["Pmax"] / Pcrit]

    Tsat = PropsSI("T", "P", result["Pmax"], "Q", 0.5, "Isopentane")
    DT = [result["Tmax"] - Tsat]


# the full map
if __name__ == "__main__":

    matplotlib.use("pgf")

    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "figure.figsize": (4.9, 3.5),
        'font.family': 'serif',
        "font.size": 12.0,
        'text.usetex': True,
        "text.latex.preamble": "\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{siunitx}",
        'pgf.rcfonts': False,
    })

    Np = 20
    Nt = 20
    Prs = np.linspace(0.3, 0.8, Np)
    DTs = np.linspace(3, 15, Nt)

    Wnet = np.ones((Np, Nt)) * np.NAN

    for i, pr in enumerate(Prs):
        for j, dt in enumerate(DTs):

            Wnet[i][j] = - calc_cycle(pr, dt)

    Wnet_max = np.max(Wnet)
    ids = np.argwhere(Wnet == Wnet_max)[0]
    Wnet /= Wnet_max

    print((1 - Wnet_Power_Cycle/Wnet_max)*100)

    fig, ax = plt.subplots()

    cs = ax.contourf(DTs, Prs, Wnet, cmap=cm.Oranges)
    ax.plot([DTs[ids[1]]], [Prs[ids[0]]], "*", color="black", markersize=10)
    ax.plot([DT], [Pr], "o", color="black", markersize=10)
    fig.colorbar(cs, label="Net electric power")

    ax.set_xlabel("Reduced Pressure")
    ax.set_ylabel("Superheating")

    # ax.set_xlabel("Reduced Pressure")
    ax.set_ylim((None, 0.85))

    plt.tight_layout()

    plt.savefig('Plots/ObjFuncShape_Wnet.pgf')
    # plt.show()

# the dependency on DTsh
if __name__ == "__main_":
    Pr = 0.75
    Nt = 100
    DTs = np.linspace(3, 15, Nt)
    Wnet = np.ones(Nt) * np.NAN
    for i, dt in enumerate(DTs):
        Wnet[i] = - calc_cycle(Pr, dt)

    fig, ax = plt.subplots()
    ax.plot(DTs, Wnet*1e-6)

    ax.set_xlabel("Super-heating/\\unit{\K}")
    ax.set_ylabel("Net electric power/\\unit{\\kilo\\watt}")

    plt.show()
