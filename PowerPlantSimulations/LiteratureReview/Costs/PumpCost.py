import matplotlib.pyplot as plt
from math import pow, log10, log, exp
from CoolProp.CoolProp import PropsSI

import numpy as np
import tikzplotlib

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

def Turton(W):

    yref = 2001

    if 1 <= W <= 300:
        logW = log10(W)

        logC = 3.3892 - 0.0536*logW + 0.1538*logW*logW

        cost = pow(10, logC)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency*corr_PPI

    return cost

def Smith(W):

    yref = 2000

    if 4 <=W <= 700:
        cost = 1.051e4 * pow(W/4, 0.55)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency*corr_PPI

    return cost

def Astolfi(W):

    yref = 2014

    cost = 1.4e4 * pow(W/200, 0.67)

    corr_currency = convert_EUR_to_USD(1, year=yref)
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency*corr_PPI

    return cost

def GETEM(W):

    yref = 2002

    Smat = 1  # 2.35 for stainless steel

    cost = 1185 * Smat * pow(1.34*W, 0.767)

    corr_currency = 1
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency*corr_PPI

    return cost

Ws = np.logspace(0, 3)

cost_Turton = [Turton(w) for w in Ws]
spec_cost_Turton = [Turton(w)/w for w in Ws]

cost_Astolfi = [Astolfi(w) for w in Ws]
spec_cost_Astolfi = [Astolfi(w)/w for w in Ws]

cost_Smith = [Smith(w) for w in Ws]
spec_cost_Smith = [Smith(w)/w for w in Ws]

cost_GETEM = [GETEM(w) for w in Ws]
spec_cost_GETEM = [GETEM(w)/w for w in Ws]

figa, axa = plt.subplots()
axa.plot(Ws, cost_Turton, label="Turton \\cite{Turton2012}")
axa.plot(Ws, cost_Astolfi, label="Astolfi \\cite{Astolfi2014B}")
axa.plot(Ws, cost_Smith, label="Smith \\cite{Smith2005}")
axa.plot(Ws, cost_GETEM, label="GETEM \\cite{GETEM2016}\\textsuperscript{a}")

axa.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axa.set_ylabel("Turbine Cost/\\unit{\\USD}2023")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()

figb, axb = plt.subplots()
axb.plot(Ws, spec_cost_Turton, label="Turton \\cite{Turton2012}")
axb.plot(Ws, spec_cost_Astolfi, label="Astolfi \\cite{Astolfi2014B}")
axb.plot(Ws, spec_cost_Smith, label="Smith \\cite{Smith2005}")
axb.plot(Ws, spec_cost_GETEM, label="GETEM \\cite{GETEM2016}\\textsuperscript{a}")

axb.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\kilo\\watt}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("PumpCost.tex", figure=figa)
tikzplotlib.save("PumpSpecCost.tex", figure=figb)

plt.show()
