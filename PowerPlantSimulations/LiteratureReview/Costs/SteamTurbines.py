import matplotlib.pyplot as plt
from math import pow, log10, log, exp

import numpy as np
import tikzplotlib

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

eta_mech = 0.97


def GETEM(W):

    yref = 2002

    W *= eta_mech

    cost = 2830*pow(W, 0.745) + 3685*pow(W, 0.617)

    corr_currency = 1
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


def genGEO(W):

    yref = 2002

    cost = 0.67 * (2830*pow(W, 0.745) + 3685*pow(W, 0.617))

    corr_currency = 1
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


def Turton(W):

    yref = 2001

    if W < 70:
        # spec_cost = Turton(70)/70
        # cost = spec_cost * W

        cost = np.NAN
    elif 70 <= W <= 7500:
        logW = log10(W)
        logcost = 2.6259 + 1.4398*logW - 0.1776 * logW*logW

        cost = pow(10, logcost)
    else:
        # spec_cost = Turton(7500) / 7500
        # cost = spec_cost * W

        cost = np.NAN

    corr_currency = convert_EUR_to_USD(1, year=yref)
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


def Thermoflex(W):

    yref = 2021

    if W < 500:
        # spec_cost = Thermoflex(500)/500
        # cost = spec_cost*W
        cost = np.NAN
    elif 500 <= W <= 70000:

        W *= eta_mech
        logW = log(W)

        cost = 1000 * exp(-0.0408*logW*logW + 1.3039*logW - 0.158304)

    else:
        # spec_cost = Thermoflex(70000)/70000
        # cost = spec_cost*W
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


Ws = np.logspace(1, 5)

cost_GETEM = [GETEM(w) for w in Ws]
spec_cost_GETEM = [GETEM(w)/w for w in Ws]

cost_genGEO = [genGEO(w) for w in Ws]
spec_cost_genGEO = [genGEO(w)/w for w in Ws]

cost_Turton = [Turton(w) for w in Ws]
spec_cost_Turton = [Turton(w)/w for w in Ws]

cost_ThermoFlex = [Thermoflex(w) for w in Ws]
spec_cost_ThermoFlex = [Thermoflex(w)/w for w in Ws]

figa, axa = plt.subplots()
axa.plot(Ws, cost_GETEM, label="GETEM \\cite{GETEM2016}")
axa.plot(Ws, cost_genGEO, label="genGEO \\cite{Adams2021}")
axa.plot(Ws, cost_Turton, label="Turton \\cite{Turton2012}")
axa.plot(Ws, cost_ThermoFlex, label="Thermoflex \\cite{Thermoflex2021}\\textsuperscript{a}")

axa.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axa.set_ylabel("Turbine Cost/\\unit{\\USD}2023")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()

figb, axb = plt.subplots()
axb.plot(Ws, spec_cost_GETEM, label="GETEM \\cite{GETEM2016}")
axb.plot(Ws, spec_cost_genGEO, label="genGEO \\cite{Adams2021}")
axb.plot(Ws, spec_cost_Turton, label="Turton \\cite{Turton2012}")
axb.plot(Ws, spec_cost_ThermoFlex, label="Thermoflex \\cite{Thermoflex2021}\\textsuperscript{a}")

axb.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\kilo\\watt}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("SteamTurbineCost.tex", figure=figa)
tikzplotlib.save("SteamTurbineSpecCost.tex", figure=figb)

plt.show()
