import matplotlib.pyplot as plt
from math import pow, log10, log, exp, sqrt

import numpy as np
import tikzplotlib

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

eta_mech = 0.97

# for Astolfi

rho_wf = 10.44857971
deltaH = 78.7498334
n_stages = 3


def GETEM(W):

    yref = 2002

    W *=eta_mech

    if W > 11000:
        cost = np.NAN
    else:

        cost = 7400*pow(W, 0.6) + 1800 *pow(W, 0.67)

    corr_currency = 1
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


def TowlerSinnot(W):

    yref = 2010

    if 100 <=W<=20000:
        cost = -1.4e4 + 1900*pow(W, 0.75)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


def Turton(W):

    yref = 2001

    if 100 <= W <= 7500:
        logW = log10(W)
        logcost = 2.7051 + 1.4398*logW - 0.1776 * logW*logW

        cost = pow(10, logcost)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)
    cost *= corr_currency*corr_PPI

    return cost


def Astolfi(W):

    yref = 2014

    Vrate = W / deltaH / rho_wf
    SP = sqrt(Vrate) / pow(1000*deltaH, 0.25)

    cost = 1.23e6 * sqrt(n_stages/2) * pow(SP/0.18, 1.1) + 2e5*pow(W/5000, 0.67)

    corr_currency = convert_EUR_to_USD(1, year=yref)
    corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", yref)

    cost *= corr_currency*corr_PPI

    return cost


Ws = np.logspace(1, 5)

cost_GETEM = [GETEM(w) for w in Ws]
spec_cost_GETEM = [GETEM(w)/w for w in Ws]

cost_TowlerSinnot = [TowlerSinnot(w) for w in Ws]
spec_cost_TowlerSinnot = [TowlerSinnot(w)/w for w in Ws]

cost_Turton = [Turton(w) for w in Ws]
spec_cost_Turton = [Turton(w)/w for w in Ws]

cost_Astolfi = [Astolfi(w) for w in Ws]
spec_cost_Astolfi = [Astolfi(w)/w for w in Ws]

figa, axa = plt.subplots()
axa.plot(Ws, cost_GETEM, label="GETEM \\cite{GETEM2016}")
axa.plot(Ws, cost_TowlerSinnot, label="Towler-Sinnot \\cite{TowlerGavin2013}")
axa.plot(Ws, cost_Turton, label="Turton \\cite{Turton2012}")
axa.plot(Ws, cost_Astolfi, label="Astolfi \\cite{Astolfi2014B}\\textsuperscript{a}")

axa.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axa.set_ylabel("Cost/\\unit{\\USD}2023")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()

figb, axb = plt.subplots()
axb.plot(Ws, spec_cost_GETEM, label="GETEM \\cite{GETEM2016}")
axb.plot(Ws, spec_cost_TowlerSinnot, label="Towler-Sinnot \\cite{TowlerGavin2013}")
axb.plot(Ws, spec_cost_Turton, label="Turton \\cite{Turton2012}")
axb.plot(Ws, spec_cost_Astolfi, label="Astolfi \\cite{Astolfi2014B}\\textsuperscript{a}")

axb.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\kilo\\watt}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("ORCTurbineCost.tex", figure=figa)
tikzplotlib.save("ORCTurbineSpecCost.tex", figure=figb)

plt.show()



